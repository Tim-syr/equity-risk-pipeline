# Week 1
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