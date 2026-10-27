import pandas
import config
from pathlib import Path
from pydantic import BaseModel, field_validator, ValidationError
import re

ISIN_RE = re.compile(r"[A-Z]{2}[A-Z0-9]{9}[0-9]")


class CsvData(BaseModel):

    ticker: str
    company_name: str 
    sector: str 
    isin: str | None = None # kind of an optional field anyway, so we won't reject a valuable row just because the isin isn't there
    # There will be a warning in the logging for a missing isin

    @field_validator("ticker", mode="before")
    @classmethod
    def ticker_in_ticker_list(cls, ticker: str):
        if ticker is None:
            raise ValueError("invalid ticker name: ticker is empty.")
        if not(ticker in config.TICKER_LIST):
            raise ValueError("invalid ticker name: ticker is not in the ticker list from config.")
        return ticker

    @field_validator("company_name", mode="before") # we use before so that a None value doesn't get rejected (and lets us use our custom message)
    @classmethod
    def is_not_empty_company_name(cls, company_name: str):
        if (company_name is None): # converted to None beginning split_dataframe
            raise ValueError("company name missing")
        return company_name

    @field_validator("sector", mode="before")
    @classmethod
    def is_not_empty_sector(cls, sector: str):
        if (sector is None):
            raise ValueError("unknown sector label")
        return sector

    @field_validator("isin", mode="before")
    @classmethod
    def is_isin(cls, isin: str):
        if not(isin is None):
            if not ISIN_RE.fullmatch(isin):
                raise ValueError("ISIN format is not valid")
        return isin






def get_dataframe_from_csv(csv_path):
    return pandas.read_csv(csv_path)

def normalise_dataframe(raw_dataframe):
    """
    Takes a pandas dataframe from a pandas.read_csv with following fields: ticker,company_name,sector,isin
    Returns a cleaned dataframe after applying basic data cleaning on each field
    """
    clean_dataframe = raw_dataframe.copy()
    
    # ticker
    clean_dataframe["ticker"] = clean_dataframe["ticker"].str.upper()
    clean_dataframe["ticker"] = clean_dataframe["ticker"].str.strip()
    for suffix in config.TICKER_SUFFIXE_LIST:
        for separator in [".", " "]:
            clean_dataframe["ticker"] = clean_dataframe["ticker"].str.removesuffix(f"{separator}{suffix}")
    
    # company_name
    clean_dataframe["company_name"] = clean_dataframe["company_name"].str.strip()
    # we will not remove suffixes, company_name isn't a key (the ticker is), the company name is only for human reading.

    # sector
    clean_dataframe["sector"] = clean_dataframe["sector"].str.strip()
    clean_dataframe["sector"] = clean_dataframe["sector"].str.lower()
    clean_dataframe["sector"] = clean_dataframe["sector"].str.normalize("NFKD") # separate the accents
    clean_dataframe["sector"] = clean_dataframe["sector"].str.encode("ascii", errors="ignore") # drops the accents 
    clean_dataframe["sector"] = clean_dataframe["sector"].str.decode("ascii") # decodes back to text
    clean_dataframe["sector"] = clean_dataframe["sector"].map(config.SECTOR_MAPPING)

    # isin
    clean_dataframe["isin"] = clean_dataframe["isin"].str.strip()
    clean_dataframe["isin"] = clean_dataframe["isin"].str.upper()
    
    
    return clean_dataframe

def split_dataframes(clean_dataframe, raw_dataframe):
    clean_dataframe = clean_dataframe.astype(object).where(clean_dataframe.notna(), None) # replaces the False from the notna by None value, for conversion purposes
    raw_dataframe = raw_dataframe.astype(object).where(raw_dataframe.notna(), None)

    clean_rows = clean_dataframe.to_dict(orient="records")
    # [{'ticker': 'XXXX', 'company_name': 'blablabla'
    raw_rows = raw_dataframe.to_dict(orient="records")

    accepted_data_list = []
    rejected_data_list = []

    for i in range(len(clean_rows)):
        try:
            pydantic_row = CsvData(**clean_rows[i])
            accepted_data_list.append(pydantic_row)
        except ValidationError as reason:
            rejected_data_list.append((raw_rows[i], reason))
    return (accepted_data_list, rejected_data_list)

if __name__ == "__main__":
    dataframe = get_dataframe_from_csv(Path(__file__).resolve().parent.parent / "data" / "reference_assets.csv")
    print("csv extraction:")
    print(dataframe)
    clean_dataframe = normalise_dataframe(dataframe)
    print("\n\nnormalised dataframe:")
    print(clean_dataframe)

    accepted_data_list, rejected_data_list = split_dataframes(clean_dataframe, dataframe)

    print("\n\n\n")
    print("Accepted data:")
    print(accepted_data_list)
    print("Rejected data:")
    print(rejected_data_list)