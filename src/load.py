import psycopg
import os
from dotenv import load_dotenv
import extract
import config
import validate


def load_data(raw_prices_list, rejected_list):
    """
    Pushes the retrieved lists from the dataframe from local to the database using psycopg
    Cleaned and correct data goes into the raw_prices table, 
    rows with issues are pushed to rejected_rows table. (not yet implemented)
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

if __name__ == "__main__":
    load_data(*(validate.validate(extract.get_dataframe(config.ticker_list))))