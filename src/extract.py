import yfinance as yf
import pandas as pd

def fetch_historical_data(ticker_list: list):
    """
    Uses a list of strings containing ticker name and returns its historical data.
    Only works with .PA, paris tickers.
    
    returns a dictionary with ticker name as key, and yf.history as value.
    """
    ticker_historical_data = {}

    # using memory because small set, would have to dynamically put it in the database if there were more tickers or more information
    for ticker in ticker_list:
        try:
            ticker_yf = yf.Ticker(f"{ticker}.PA") #.pa for paris, all the tickers are from CAC 40
            ticker_historical_data[ticker] = ticker_yf.history(period="5y")
        except Exception:
            print(f"{ticker} was not found and could not be included in the dataframe.")

    return ticker_historical_data


def normalise_historical_data(raw_data: dict):
    '''
    Uses a dictionary with ticker name as key, and yf.history as value.

    Gets the date out of index and sets it as a column, 
    adds ticker as a column, 
    trims Dividends and Stock Splits columns (aren't used in this project).
    Lowercases each name.

    Returns the dataset with all the tickers in one.
    '''
    dataframe = pd.concat(raw_data, names=["ticker"]) # this gives us a ticker column which wasn't in the yfinance .history
    dataframe = dataframe.reset_index() # sets dataframe index to column (the ticker and the date)
    dataframe = dataframe.drop(["Dividends", "Stock Splits"], axis="columns") # deletes the columns
    dataframe = dataframe.rename(str.lower, axis="columns") # lowercase on every column name
    dataframe["date"] = dataframe["date"].dt.tz_localize(None) # simplifies the date to XXXX-XX-XX (removes the timezone)
    return dataframe


def get_dataframe(ticker_list: list):
    """
    Uses a list of tickers in .PA market to fetch the historical data and normalise it, before returning a dataframe with:
    ticker , date , open , high , low , close , volume
    """
    # historical data fetch
    ticker_historical_data = fetch_historical_data(ticker_list)
    # normalisation
    dataframe = normalise_historical_data(ticker_historical_data)

    return dataframe


if __name__ == "__main__":
    ticker_list = ["AI", "AIR", "BNP", "CAP", "CA", "BN", "ENGI", "MC", "ML", "ORA"]

    dataframe = get_dataframe(ticker_list)
    print("A QUICK LOOK AT THE DATAFRAME:\n\n")
    print(dataframe.head())
    print("\n\nDATAFRAME .INFO():\n\n")
    dataframe.info()