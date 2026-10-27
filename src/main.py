import config
import extract
import validate
import load
import reconcile
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def call_pipeline(ticker_list: list):
    """
    takes a list of strings as an argument, representing ticker names. Calls them on the .PA market. 
    rest will be written as the function will expand.
    """
    logger.info("call_pipeline initiated")
    dataframe, failed_ticker_list = extract.get_dataframe(ticker_list)
    raw_prices_list, rejected_list = validate.validate(dataframe)
    load.load_data(raw_prices_list, rejected_list, failed_ticker_list)
    logger.info("call_pipeline ended")

def upsert_reference_assets():
    """
    Takes the reference_assets.csv file and upserts the company_information table.
    Assumes we replace the file whenever we want new information.
    """
    logger.info("upsert of reference_assets initiated")
    dataframe = reconcile.get_dataframe_from_csv(Path(__file__).resolve().parent.parent / "data" / "reference_assets.csv")
    clean_dataframe = reconcile.normalise_dataframe(dataframe)
    accepted_data_list, rejected_data_list = reconcile.split_dataframes(clean_dataframe, dataframe)
    load.load_company_information_data(accepted_data_list, rejected_data_list)
    logger.info("upsert of reference_assets ended")
    

if __name__ == "__main__":
    call_pipeline(config.TICKER_LIST)