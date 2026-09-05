import yfinance as yf

ticker_list = ["AI", "AIR", "BNP", "CAP", "CA", "BN", "ENGI", "MC", "ML", "ORA"]

# historical data fetch
ticker_historical_data = {}

# using cache because small set, would have to dynamically put it in the database if there were more tickers
for ticker in ticker_list:
    ticker_yf = yf.Ticker(f"{ticker}.PA") #.pa for paris, all the tickers are from CAC 40
    ticker_historical_data[ticker] = ticker_yf.history(period="5y")

# Each dataframe columns: Open        High         Low       Close   Volume  Dividends  Stock Splits
