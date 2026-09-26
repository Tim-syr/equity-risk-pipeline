import config
import extract
import validate
import load

def call_pipeline(ticker_list: list):
    """
    takes a list of strings as an argument, representing ticker names. Calls them on the .PA market. 
    rest will be written as the function will expand.
    """
    dataframe = extract.get_dataframe(ticker_list)
    raw_prices_list, rejected_list = validate.validate(dataframe)
    load.load_data(raw_prices_list, rejected_list)


if __name__ == "__main__":
    call_pipeline(config.TICKER_LIST)