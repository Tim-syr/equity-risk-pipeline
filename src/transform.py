import pandas
import numpy

def nan_to_null(dataframe: pandas.DataFrame) -> pandas.DataFrame:
    """
    Turns the NaN inside of the dataframe into None, so that psycopg can insert them as null values which can be detected better in sql
    """
    dataframe = dataframe.astype(object).where(dataframe.notna(), None) #where replaces the false given by .notna() to None
    return dataframe

def add_log_change_column(dataframe : pandas.DataFrame):
    """
    Takes a pandas Dataframe with at least ticker, date and close columns.
    Adds a column log_change containing the log change.
    Returns the newly formed Dataframe.
    """
    dataframe = dataframe.sort_values(["ticker", "date"])
    dataframe["log_change"] = numpy.log(dataframe["close"] / dataframe.groupby("ticker")["close"].shift(1))

    return dataframe

def add_volatility_21_days(dataframe: pandas.DataFrame):
    """
    Takes a pandas Dataframe with at least ticker, date and log_change column. 
    Adds a column volatility_21 containing the rolling volatility of the past month.
    Returns the newly formed Dataframe.
    """
    dataframe = dataframe.sort_values(["ticker", "date"])
    dataframe["volatility_21"] = dataframe.groupby("ticker")["log_change"].rolling(21).std().droplevel(0) * numpy.sqrt(252)

    return dataframe

def add_drawdown(dataframe: pandas.DataFrame):
    """
    Takes a pandas Dataframe with at least ticker, date and close column.
    Adds a column drawdown containing the drawdown from its ath (past 5y).
    Returns the newly formed Dataframe.
    """
    dataframe = dataframe.sort_values(["ticker", "date"])
    dataframe["drawdown"] = (dataframe["close"] / dataframe.groupby("ticker")["close"].cummax()) -1

    return dataframe

def add_daily_metrics(dataframe: pandas.DataFrame) -> pandas.DataFrame:
    """
    Takes a pandas DataFrame with at least ticker, date and close columns.
    Adds the log_change, volatility_21, and drawdown columns and returns the newly made dataframe. 
    """
    dataframe = add_log_change_column(dataframe)
    dataframe = add_volatility_21_days(dataframe)
    dataframe = add_drawdown(dataframe)

    return dataframe