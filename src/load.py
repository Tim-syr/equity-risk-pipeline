import psycopg
import os
from dotenv import load_dotenv
import extract
import config


def load_data():
    """
    Pushes the dataframe from local to the database using psycopg
    """
    load_dotenv()
    
    connection_string = os.getenv("DATABASE_URL")

    raw_data = extract.get_dataframe(config.ticker_list) # before the connection, to make sure we have the data and don't open a connection for nothing
    with psycopg.connect(connection_string) as connection:
        with connection.cursor() as cursor:
            # the whole abs line basically makes us consider the upsert only if the price has changed by more than a millionth
            cursor.executemany("INSERT INTO raw_prices (ticker, date, open, high, low, close, volume) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s) \
                            ON CONFLICT (ticker, date) DO UPDATE SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, close = EXCLUDED.close, volume = EXCLUDED.volume, updated_at = now() \
                               WHERE raw_prices.volume IS DISTINCT FROM EXCLUDED.volume\
                               OR abs(raw_prices.high - EXCLUDED.high) > abs(raw_prices.high)*1e-6 \
                               OR abs(raw_prices.low - EXCLUDED.low) > abs(raw_prices.low)*1e-6\
                               OR abs(raw_prices.close - EXCLUDED.close) > abs(raw_prices.close)*1e-6\
                               OR abs(raw_prices.open - EXCLUDED.open) > abs(raw_prices.open)*1e-6",
                            raw_data.itertuples(index=False)) # safety net, there should not be any index

if __name__ == "__main__":
    load_data()