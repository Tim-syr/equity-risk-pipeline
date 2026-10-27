# Step 1: Database foundation, idempotent ingestion
**Where do I keep my database?** \
-> Neon, most heard of, and promise of a sandbox with easy to backup databases. Avoids rebuilding it everytime (locally) and stays in PostgreSQL (therefor SQL interactions)

**Which tickers are we using?** \
-> I chose 10 tickers from CAC 40 (AIR LIQUIDE, AIRBUS, BNP PARIBAS, CAPGEMINI, CARREFOUR, DANONE, ENGIE, LVMH, MICHELIN, ORANGE) \
[AI, AIR, BNP, CAP, CA, BN, ENGI, MC, ML, ORA] \
They can be changed in src/config.py \

**`/!\`** They are all on the **.PA market**, meaning that if we want to add tickers that aren't on that market, we need to change the data fecthing (which is currently adding .PA to each ticker to run the yfinance smoothly) **`/!\`**

**Claude Code usage**\
-> I decided to get Claude to work as my tutor. I generated guardrails for it in CLAUDE.md so it lets me learn and write everything by myself.

**What are we using as a primary key?**\
->(ticker, date) couple. Ticker alone has many entries, date alone has many entries across the different tickers. \
Naturally, you set the primary key as a couple, allowing you to distinguish every entry. 

**What type to store main raw values?**\
->Numeric, to have base 10 exact decimals, corresponding to the actual price. A float wouldn't represent money in base 10 accurately, and on operations could stack up inacurracy.

**How to handle price corrections such as dividends?**\
-> Handled by yfinance, with .history, wich defaults to auto_adjust=True, so the close is adjusted for splits and dividends and past closes change after a corporate action.\
-> Added a column updated_at for transparancy whenever it occures.
-> Considering a price change whenever it changes by more than a millionth to its original price, because yfinance actually has a drift of about 1e-7 on its prices. 

# Step 2: Data quality, rejects, reference file reconciliation

**How should we organise bad rejected rows?**\
->We use a new table, rejected_rows, that contains an id, a source, the raw data rejected as a json, the rejection reason, the time it was rejected at, and how many times it was rejected (source + row content as identifier) (in case we run at 2 different days with the same issue, prevents a duplicate line on every daily run while still recording that the problem came back). However it is worth noting that if yfinance adjusts a price, then we would get a new id for a new rejection since the prices won't match. That is intended, the table acts as a backlog, so it's fine. A counter keeps up with the amount of times we got the same rejected_row. The time it was rejected keeps the first instance of rejection.

**How to handle the source?**\
-> I decided to add an other table with all the possible sources, with a source_name field that will be a foreign key for the rejected_rows table. That way, we ensure we won't have multiple rejected_rows that will have same source but differently named source.

**Insertion**\
-> Decided to insert valid rows, commit, and then insert invalid rows. Risk is that we may have valid rows updated while the invalid ones haven't gotten through. Advantage is that valid rows will be updated even if a part of the bad ones is broken. 

**Company names**\
-> Decided to keep suffixes in the company names: they aren't the key, the ticker is, the company name is only for a human to read. A suffixe is therefor harmless. Saves a tiny bit of runtime too. 