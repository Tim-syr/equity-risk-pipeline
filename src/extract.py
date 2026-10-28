import yfinance as yf
import pandas as pd
import config
import logging
import time
import psycopg
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

def fetch_historical_data(ticker_list: list):
    """
    Uses a list of strings containing ticker name and returns its historical data.
    Only works with .PA, paris tickers.
    
    returns a dictionary with ticker name as key, and yf.history as value.
    """
    ticker_historical_data = {}
    
    failed_ticker_list = []

    # using memory because small set, would have to dynamically put it in the database if there were more tickers or more information
    for ticker in ticker_list:
        try:
            ticker_yf = yf.Ticker(f"{ticker}.PA") #.pa for paris, all the tickers are from CAC 40
            ticker_historical_data[ticker] = ticker_yf.history(period="5y")
            retries = 0
            while (ticker_historical_data[ticker].empty and retries < config.MAX_RETRIES):
                retries += 1
                logger.warning(f"{ticker}: no data, retry {retries}/{config.MAX_RETRIES} in {config.RETRY_DELAY_SECONDS}s")
                time.sleep(config.RETRY_DELAY_SECONDS)
                ticker_historical_data[ticker] = ticker_yf.history(period="5y")
            if (ticker_historical_data[ticker].empty):
                logger.warning(f"{ticker}: yfinance returned no data (delisted or misspelt?)")
                failed_ticker_list.append(ticker)
            else:
                logger.info(f"{ticker} fetched successfully")
        except Exception as error:
            logger.error(f"{ticker}: yfinance request failed: {error}")

    return (ticker_historical_data, failed_ticker_list)



def normalise_historical_data(raw_data: dict):
    '''
    Uses a dictionary with ticker name as key, and yf.history as value.

    Gets the date out of index and sets it as a column, 
    adds ticker as a column, 
    trims Dividends and Stock Splits columns (aren't used in this project).
    Lowercases each name.
    Rounds the numerical values to the 6th decimal (see why in docs/Difficulties.md, 1st week)

    Returns the dataset with all the tickers in one.
    '''
    dataframe = pd.concat(raw_data, names=["ticker"]) # this gives us a ticker column which wasn't in the yfinance .history
    dataframe = dataframe.reset_index() # sets dataframe index to column (the ticker and the date)
    dataframe = dataframe.drop(["Dividends", "Stock Splits"], axis="columns") # deletes the columns
    dataframe = dataframe.rename(str.lower, axis="columns") # lowercase on every column name
    dataframe["date"] = dataframe["date"].dt.tz_localize(None) # simplifies the date to XXXX-XX-XX (removes the timezone)

    float_columns = dataframe.select_dtypes(include='float').columns
    dataframe[float_columns] = dataframe[float_columns].round(6)
    return dataframe


def get_dataframe(ticker_list: list):
    """
    Uses a list of tickers in .PA market to fetch the historical data and normalise it, before returning a dataframe with:
    ticker , date , open , high , low , close , volume
    """
    # historical data fetch
    ticker_historical_data, failed_ticker_list = fetch_historical_data(ticker_list)
    # normalisation
    dataframe = normalise_historical_data(ticker_historical_data)

    return (dataframe, failed_ticker_list)

def get_raw_prices_dataframe() -> pd.DataFrame:
    """
    Fetches historical prices from raw_prices table and returns a pandas dataframe
    (only ticker, date and close are really useable for calculation right now)
    """
    load_dotenv()
    connection_string = os.getenv("DATABASE_URL")

    with psycopg.connect(connection_string) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT ticker, date, close FROM raw_prices")
            rows = cursor.fetchall()
            column_names = [column.name for column in cursor.description]
            logger.info("%d entries fetched from raw_prices", len(rows))

    dataframe = pd.DataFrame(rows, columns=column_names)
    dataframe["close"] = dataframe["close"].astype(float)

    return dataframe

if __name__ == "__main__":

    dataframe, failed_ticker_list = get_dataframe(config.TICKER_LIST)
    print("A QUICK LOOK AT THE DATAFRAME:\n\n")
    print(dataframe.head())
    print("\n\nDATAFRAME .INFO():\n\n")
    dataframe.info()