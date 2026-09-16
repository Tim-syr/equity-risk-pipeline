# Week 1

### MISSING THE YFINANCE PRICE ADJUSTMENT HANDLING
Initial plan only included ingested_at column. It was getting updated only once, at ingestion. However, if a value gets updated, we loose track of when it was changed comparing to the first ingestion. \
-> Added a updated_at column to store the timestamp of that last update.

Yfinance returns floats with many decimals. The python's double precision (float) type is about 17 significant digits. When psycopg transitions from python to the postgresql database and converts to numeric sql type, it handles 15 significant digits. This was making price changes when none occured.
->Automatically rounded all floats to the 6th decimal, more than enough for a price. Leaves the room for tickers worth up to 999 Millions. However, there was a minor drift still of around 1e-7.
->Changed the sql querry to upsert only when a float moves by more than a 1e-6 of the last recorded value because yfinance actually has a drift of 1e-7 on its prices.