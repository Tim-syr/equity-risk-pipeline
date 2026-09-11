# Week 1
**Where do I keep my database?** \
-> Neon, most heard of, and promise of a sandbox with easy to backup databases. Avoids rebuilding it everytime (locally) and stays in PostgreSQL (therefor SQL interactions)

**Which tickers are we using?** \
-> I chose 10 tickers from CAC 40 (AIR LIQUIDE, AIRBUS, BNP PARIBAS, CAPGEMINI, CARREFOUR, DANONE, ENGIE, LVMH, MICHELIN, ORANGE) \
[AI, AIR, BNP, CAP, CA, BN, ENGI, MC, ML, ORA] \

**`/!\`** They are all on the **.Pa market**, meaning that if we want to add tickers that aren't on that market, we need to change the data fecthing (which is currently adding .Pa to each ticker to run the yfinance smoothly) **`/!\`**

**Claude Code usage**\
-> I decided to get Claude to work as my tutor. I generated guardrails for it in CLAUDE.md so it lets me learn and write everything by myself.

**How to handle price corrections such as dividends?**\
-> Handled by yfinance, with .history, wich defaults to auto_adjust=True, so the close is adjusted for splits and dividends and past closes change after a corporate action.