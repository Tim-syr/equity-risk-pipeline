from pydantic import BaseModel
import extract
import config
import datetime
from pydantic import model_validator, field_validator, ValidationError, Field
import pandas

class PriceRecord(BaseModel):
    #ticker, date, open, high, low, close, volume
    ticker: str
    date: datetime.date
    open: float = Field(allow_inf_nan=False) # no NaN values basically
    high: float = Field(allow_inf_nan=False)
    low: float = Field(allow_inf_nan=False)
    close: float = Field(allow_inf_nan=False)
    volume: int

    @field_validator("ticker", mode="after")
    @classmethod
    def non_empty_ticker(cls, ticker: str):
        ticker = ticker.strip()
        if (ticker == ''):
            raise ValueError("ticker string is empty, check if it exists.")
        return ticker
    
    @field_validator("date", mode="after")
    @classmethod
    def non_future_date(cls, date: datetime.date):
        if (date > datetime.date.today()):
            raise ValueError("date is in the future.")
        return date
    
    @field_validator("volume", mode="after")
    @classmethod
    def non_negative_volume(cls, volume: int):
        if (volume < 0):
            raise ValueError("volume is negative.")
        return volume
    
    @field_validator("open", mode="after")
    @classmethod
    def positive_open(cls, open):
        if (open <= 0):
            raise ValueError("open is lesser or equal to 0")
        return open

    @field_validator("close", mode="after")
    @classmethod
    def positive_close(cls, close):
        if (close <= 0):
            raise ValueError("close is lesser or equal to 0")
        return close

    @field_validator("low", mode="after")
    @classmethod
    def positive_low(cls, low):
        if (low <= 0):
            raise ValueError("low is lesser or equal to 0")
        return low

    @field_validator("high", mode="after")
    @classmethod
    def positive_high(cls, high):
        if (high <= 0):
            raise ValueError("high is lesser or equal to 0")
        return high
    
    @model_validator(mode="after")
    def coherent_low_open_close_high(self):
        problems = []
        if (self.high < self.low):
            problems.append("high field is lower than low field")
        if (self.close < self.low):
            problems.append("close field is lower than low field")
        if (self.close > self.high):
            problems.append("close field is higher than high field")
        if (self.open > self.high):
            problems.append("open field is higher than high field")
        if (self.open < self.low):
            problems.append("open field is lower than low field")
        if problems:
            raise ValueError("; ".join(problems))
        return self
    
def dict_row_to_string(row: dict):
    """
    Takes a pandas_dataframe.to_dict single row and returns a new dict containing all the fields with string values.
    {'ticker': 'XXXX', 'date': pandas_timestamp, 'open': X.XX, ...}
    """
    string_row = {}
    for field in row.keys():
        string_row[field] = str(row[field])
    return string_row
    

def validate(raw_data: pandas.DataFrame):
    """
    takes a pandas dataframe from extract.py and returns 2 lists, one containing valid rows, the other containing tuples of non valid row + reason
    """
    # [{'ticker': 'XXXX', 'date': pandas_timestamp, 'open': X.XX, ...}, {...} ...]
    rows = raw_data.to_dict(orient="records")

    raw_prices_list = []
    rejected_list = []

    for row in rows:
        try:
            pydantic_row = PriceRecord(**row) # same as ticker=row['ticker'], date=row['date'], open=row['open'], high=row['high'], low=row['low'], close=row['close'], volume=row['volume']
            # one pydantic_row entry: ticker='AI' date=datetime.date(2021, 9, 22) open=99.246118 high=99.698113 low=98.807823 close=99.054367 volume=791527
            raw_prices_list.append(pydantic_row)
        except ValidationError as reason:
            rejected_list.append((dict_row_to_string(row), reason))
    return (raw_prices_list, rejected_list)


if __name__ == "__main__":
    validate(extract.get_dataframe(config.TICKER_LIST))