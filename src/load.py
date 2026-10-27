import psycopg
import os
from dotenv import load_dotenv
import extract
import config
import validate
from psycopg.types.json import Jsonb
import logging

logger = logging.getLogger(__name__)

def insert_invalid_rows(cursor, rejected_list, source):
    '''
    Takes psycopg cursor, rejected_list a list of tuples containing (dataframe_row, reason_of_rejection) and the source as a string
    Inserts it all in rejected_rows table
    '''
    iterable_rejected_rows = []
    for row, reason in rejected_list:
        new_row = {}
        new_row['source'] = source
        new_row['rejection_reason']= str(reason) # reason comes from an except ValidationError as reason
        new_row['raw_data'] = Jsonb(row)
        iterable_rejected_rows.append(new_row)
    
    cursor.executemany("INSERT INTO rejected_rows (source, raw_data, rejection_reason) \
                        VALUES (%(source)s, %(raw_data)s, %(rejection_reason)s) \
                        ON CONFLICT (source, raw_data) DO UPDATE SET times_seen = rejected_rows.times_seen+1", 
                    iterable_rejected_rows)
    logger.info("%d rows from %s written on rejected_rows", cursor.rowcount, source)

def load_data(raw_prices_list, rejected_list, failed_ticker_list):
    """
    Pushes the retrieved lists from the dataframe from local to the database using psycopg
    Cleaned and correct data goes into the raw_prices table, 
    rows with issues are pushed to rejected_rows table.
    """
    load_dotenv()
    
    connection_string = os.getenv("DATABASE_URL")

    with psycopg.connect(connection_string) as connection:
        with connection.cursor() as cursor:
            # the whole abs line basically makes us consider the upsert only if the price has changed by more than a millionth
            cursor.executemany("INSERT INTO raw_prices (ticker, date, open, high, low, close, volume) \
                            VALUES (%(ticker)s, %(date)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s) \
                            ON CONFLICT (ticker, date) DO UPDATE SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, close = EXCLUDED.close, volume = EXCLUDED.volume, updated_at = now() \
                               WHERE raw_prices.volume IS DISTINCT FROM EXCLUDED.volume\
                               OR abs(raw_prices.high - EXCLUDED.high) > abs(raw_prices.high)*1e-6 \
                               OR abs(raw_prices.low - EXCLUDED.low) > abs(raw_prices.low)*1e-6\
                               OR abs(raw_prices.close - EXCLUDED.close) > abs(raw_prices.close)*1e-6\
                               OR abs(raw_prices.open - EXCLUDED.open) > abs(raw_prices.open)*1e-6",
                            [row.model_dump() for row in raw_prices_list])
                            # {'ticker': str_value, ...}

            logger.info("%d rows written on raw_prices", cursor.rowcount)

            connection.commit()

            insert_invalid_rows(cursor, rejected_list, config.MAIN_API_SOURCE)
            failed_ticker_rows = []
            for ticker in failed_ticker_list:
                failed_ticker_rows.append(({"ticker": ticker}, f"{ticker} was not found and could not be included in the dataframe."))
            insert_invalid_rows(cursor, failed_ticker_rows, config.MAIN_API_SOURCE)

def load_company_information_data(correct_information_list: list, rejected_list: list):
    """
    Pushes the retrieved lists from the dataframe from local to the database using psycopg
    Cleaned and correct data goes into the company_information table, 
    rows with issues are pushed to rejected_rows table.
    """
    load_dotenv()
    
    connection_string = os.getenv("DATABASE_URL")

    with psycopg.connect(connection_string) as connection:
        with connection.cursor() as cursor:

            cursor.executemany("""INSERT INTO company_information (ticker, company_name, sector, isin) \
                            VALUES (%(ticker)s, %(company_name)s, %(sector)s, %(isin)s) \
                            ON CONFLICT (ticker) DO UPDATE SET company_name = EXCLUDED.company_name, sector = EXCLUDED.sector, isin = EXCLUDED.isin, updated_at = now() \
                               WHERE company_information.company_name IS DISTINCT FROM EXCLUDED.company_name\
                               OR company_information.sector IS DISTINCT FROM EXCLUDED.sector\
                               OR company_information.isin IS DISTINCT FROM EXCLUDED.isin""",
                            [row.model_dump() for row in correct_information_list])
                            # {'ticker': str_value, ...}

            logger.info("%d rows written on company_information", cursor.rowcount)
            connection.commit()

            insert_invalid_rows(cursor, rejected_list, "reference_assets")


if __name__ == "__main__":
    dataframe, failed_ticker_list = extract.get_dataframe(config.TICKER_LIST)
    raw_prices_list, rejected_list = validate.validate(dataframe)
    load_data(raw_prices_list, rejected_list, failed_ticker_list)