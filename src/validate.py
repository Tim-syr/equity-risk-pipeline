from pydantic import BaseModel
import extract
import config
import datetime
from pydantic import model_validator, field_validator, ValidationError, Field

class PriceRecord(BaseModel):
    #ticker, date, open, high, low, close, volume
    ticker: str
    date: datetime.date
    open: float = Field(allow_inf_nan=False) # no null values basically
    high: float = Field(allow_inf_nan=False)
    low: float = Field(allow_inf_nan=False)
    close: float = Field(allow_inf_nan=False)
    volume: int

    @field_validator("ticker", mode="after")
    @classmethod
    def non_empty_ticker(cls, ticker: str):
        ticker = ticker.strip()
        if (ticker == ''):
            raise ValueError("ticker string is empty, check if it's not delisted or if it exists.")
        return ticker
    @field_validator("date", mode="after")
    @classmethod
    def non_future_date(cls, date: datetime.date):
        if (date > datetime.date.today()):
            raise ValueError("date is in the future.")
        return date
    @field_validator("volume", mode="after")
    @classmethod
    def positive_volume(cls, volume: int):
        if (volume < 0):
            raise ValueError("volume is negative.")
        return volume
    @model_validator(mode="after")
    def coherent_low_close_high(self):
        problems = []
        if (self.high < self.low):
            problems.append("high field is lower than low field")
        if (self.close < self.low):
            problems.append("close field is lower than low field")
        if (self.close > self.high):
            problems.append("close field is higher than high field")
        if problems:
            raise ValueError("; ".join(problems))
        return self
    

def validate():
    raw_data = extract.get_dataframe(config.ticker_list)
    # [{'ticker': 'XXXX', 'date': datetime.date_object, 'open': X.XX, ...}, {...} ...]
    rows = raw_data.to_dict(orient="records")

    raw_prices_list = []
    rejected_list = []

    for row in rows:
        try:
            pydantic_row = PriceRecord(**row) # same as ticker=row['ticker'], date=row['date'], open=row['open'], high=row['high'], low=row['low'], close=row['close'], volume=row['volume']
            # one pydantic_row entry: ticker='AI' date=datetime.date(2021, 9, 22) open=99.246118 high=99.698113 low=98.807823 close=99.054367 volume=791527
            raw_prices_list.append(pydantic_row)
        except ValidationError as reason:
            rejected_list.append((row, reason))


if __name__ == "__main__":
    validate()