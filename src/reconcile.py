import pandas
import config
from pathlib import Path

def get_dataframe_from_csv(csv_path):
    return pandas.read_csv(csv_path)

def normalise_dataframe(raw_dataframe):
    clean_dataframe = raw_dataframe.copy()
    
    # ticker
    clean_dataframe["ticker"] = clean_dataframe["ticker"].str.upper()
    clean_dataframe["ticker"] = clean_dataframe["ticker"].str.strip()
    for suffix in config.TICKER_SUFFIXE_LIST:
        for separator in [".", " "]:
            clean_dataframe["ticker"] = clean_dataframe["ticker"].str.removesuffix(f"{separator}{suffix}")
    empty_ticker_mask = (clean_dataframe["ticker"].isna()) | (clean_dataframe["ticker"] == "")

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
    correct_format_isin_mask = (clean_dataframe["isin"] == "") | (clean_dataframe["isin"].str.fullmatch(r"[A-Z]{2}[A-Z0-9]{9}[0-9]{1}")) | (clean_dataframe["isin"].isna())
    return clean_dataframe

def split_dataframes(clean_dataframe, raw_dataframe):
    pass

if __name__ == "__main__":
    dataframe = get_dataframe_from_csv(Path(__file__).resolve().parent.parent / "data" / "reference_assets.csv")
    print(dataframe)
    clean_dataframe = normalise_dataframe(dataframe)
    print(clean_dataframe)