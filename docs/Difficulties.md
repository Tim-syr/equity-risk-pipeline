# Step 1: Database foundation, idempotent ingestion

### MISSING THE YFINANCE PRICE ADJUSTMENT HANDLING
Initial plan only included ingested_at column. It was getting updated only once, at ingestion. However, if a value gets updated, we loose track of when it was changed comparing to the first ingestion. \
-> Added a updated_at column to store the timestamp of that last update.

Yfinance returns floats with many decimals. The python's double precision (float) type is about 17 significant digits. When psycopg transitions from python to the postgresql database and converts to numeric sql type, it handles 15 significant digits. This was making price changes when none occured.
->Automatically rounded all floats to the 6th decimal, more than enough for a price. Leaves the room for tickers worth up to 999 Millions. However, there was a minor drift still of around 1e-7.
->Changed the sql querry to upsert only when a float moves by more than a 1e-6 of the last recorded value because yfinance actually has a drift of 1e-7 on its prices.

Rest wasn't much of a trouble.

# Step 2: Data quality, rejects, reference file reconciliation

### REJECTED DATA MANAGEMENT
I wanted to store the rows that aren't valid. Mainly done in validate.py, I had to process a ton of information about how pydantic really works and the type of data used. A lot of struggle to pass around the correct types and structures, but the result in validate.py looks clean. 

# Step 3: Financial indicators and tests

### Role decision
It was a bit complicated to assign a role to each file: who will run the connection? Who calls who? Why would a function be here and not in an other file? In the end, reffering to the names is what helped me the most, and made the pipeline split easier. 

