# Known issues

Problems identified but deliberately postponed until the mandatory steps are done.

### All tickers return an empty DataFrame: the run crashes
If yfinance returns no data for every ticker (yfinance down or blocking requests, or a
wrong `TICKER_LIST`), `normalise_historical_data` in `src/extract.py` fails with
`KeyError: "['Dividends', 'Stock Splits'] not found in axis"`: an empty DataFrame from
`history()` has none of the expected columns. The crash happens before `load`, so the
failed tickers are never recorded in `rejected_rows`.
Related: empty DataFrames are still stored in `ticker_historical_data`; removing them
would make `pd.concat` fail with `No objects to concatenate` in the same situation.
Confirmed with yfinance 1.7.0: a network outage does not raise an exception, `history()`
returns an empty DataFrame, exactly as for a delisted ticker. The retry
(`MAX_RETRIES` in `src/config.py`) absorbs short outages, but during a longer one every
ticker comes back empty and the run hits this crash, with nothing recorded.

### Gaps in price history are not detected
A gap is a day on which the other tickers have a price and one ticker has none (the row
does not exist, so there is no NULL to look for). Weekends and market holidays are not
gaps: no ticker has a price on those days. Planned as a data quality check in Power BI.

### Renamed tickers have to be manually updated in dim_asset
The machinery isn't built because for tickers from CAC 40, it's very rare and would take 2 single lines of UPDATE whenever it happens. 

### Every ticker in TICKER_LIST needs a valid reference row, except one at most
A ticker whose reference row is missing or rejected is loaded under the unknown member (asset_id = -1). If two such tickers have a price on the same day, they produce the same key (date_id, -1) and the fact load fails with "ON CONFLICT DO UPDATE command cannot affect row a second time". Today only CA (Carrefour, empty ticker in the reference file) is in this case. Fix: correct the reference file and rerun upsert_reference_assets.
