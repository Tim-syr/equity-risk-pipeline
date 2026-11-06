# Portfolio risk monitoring pipeline

A data pipeline that ingests daily equity prices for ten CAC 40 companies, controls their
quality, reconciles them with a deliberately imperfect reference file, and loads everything
into a hosted PostgreSQL database. It then computes daily risk indicators and models
everything as a star schema. Power BI reporting and automation come next.

This is a portfolio project built over a few months while preparing applications for a data
apprenticeship. Every design choice is recorded in [docs/Decisions.md](docs/Decisions.md),
and the problems met along the way in [docs/Difficulties.md](docs/Difficulties.md).

## Stack

- Python 3.13
- PostgreSQL hosted on [Neon](https://neon.tech)
- psycopg 3.3
- pandas 3.0
- Pydantic 2.13
- yfinance 1.7
- pytest 9.2
- Planned: Power BI, GitHub Actions

## How it works

There are three flows. The first two share one `rejected_rows` table.

**Prices**, run by `src/main.py` (`call_pipeline`):

```
yfinance ──► extract.py ──► validate.py ──► load.py ──► raw_prices
             fetch 5 years   Pydantic          upsert
             per ticker      checks per row       │
                  │               │               │
                  └── no data ────┴── invalid ────┴──► rejected_rows
```

**Reference data**, run on demand (`upsert_reference_assets` in `src/main.py`):

```
data/reference_assets.csv ──► reconcile.py ──► load.py ──► company_information ──► dim_asset
                              normalise with    upsert                              upsert (SQL)
                              pandas, validate       │
                              with Pydantic          │
                                   └── invalid ──────┴──► rejected_rows
```

**Indicators and star schema**, run by `src/main.py` after the prices:

```
raw_prices ──► transform.py ──► daily_metrics
               log change, 21-day volatility, drawdown (pandas)

raw_prices + daily_metrics + dim_date + dim_asset ──► fact_daily_prices ──► v_portfolio_overview
                                                      upsert (SQL)           view for Power BI
```

### Design principles

- **Idempotent loads.** Running the pipeline twice inserts nothing new. Every load uses
  `INSERT ... ON CONFLICT DO UPDATE`, and a row is only rewritten (and its `updated_at`
  moved) when a value really changed.
- **Rejected data is traced, never dropped.** Invalid rows are stored as JSON with their
  rejection reason. A recurring problem increments `times_seen` instead of creating a
  duplicate.
- **Raw input is not cleaned by hand.** The reference file stays messy on purpose: the
  pipeline is responsible for normalising it.

## Status

| Steps | Topic | State |
|---|---|---|
| 1 | Database foundation, idempotent ingestion | done |
| 2 | Data quality, rejects, reference file reconciliation | done |
| 3 | Financial indicators and tests | done |
| 4 | Star schema | in progress: tables, loads and view written and tested on a local PostgreSQL, not yet applied on Neon; coherence checks to write |
| 5–6 | Power BI reporting | to do |
| 7 | Automation (GitHub Actions) | to do |
| 8 | Documentation and finalisation | to do |

## Data model

| Table | Content | Key |
|---|---|---|
| `raw_prices` | Daily open, high, low, close, volume (adjusted for splits and dividends) | `(ticker, date)` |
| `company_information` | Company name, sector, ISIN per ticker, from the reference file | `ticker` |
| `rejected_rows` | Any row that failed validation, as JSONB, with reason and `times_seen` | identity `id`, unique `(source, raw_data)` |
| `sources` | Allowed values for `rejected_rows.source` | `source_name` |
| `daily_metrics` | Log change, 21-day annualised volatility and drawdown per ticker and day | `(ticker, date)` |

Prices are stored as `NUMERIC` rather than floating point, so that decimal values are exact.
Calculated indicators are `DOUBLE PRECISION`.

### Star schema (step 4)

Written and tested on a local PostgreSQL, not yet applied on Neon.

| Table | Role | Content | Key |
|---|---|---|---|
| `fact_daily_prices` | fact | Close, volume and the three indicators. Grain: one asset, one day | `(date_id, asset_id)`, foreign keys to both dimensions |
| `dim_date` | dimension | One row per calendar day, 2021 to 2035: year, quarter, month, weekday, `is_trading_day` | `date_id` as `YYYYMMDD` |
| `dim_asset` | dimension | Ticker, ISIN, company name, sector, country, currency. Name changes overwrite the old value (SCD type 1). Unknown member `asset_id = -1`, so a price is never lost for lack of a reference row | identity `asset_id`, unique `ticker` |
| `euronext_holidays` | reference | Euronext Paris closing days, used to compute `is_trading_day` | `date` |
| `v_portfolio_overview` | view | The fact table joined to both dimensions, with readable columns, for Power BI | |

## Data quality rules

**Prices** (`src/validate.py`):
- The ticker isn't empty.
- The date isn't in the future.
- Prices are strictly positive and not NaN.
- The volume isn't negative.
- `low ≤ open, close ≤ high`.
- A ticker for which yfinance returns no data is recorded as a reject.

**Reference file** (`src/reconcile.py`): normalised with pandas, then validated with Pydantic.

| Column | Normalisation | Validation (reject if it fails) |
|---|---|---|
| `ticker` | uppercase, trim, remove the exchange suffix after `.` or a space (`MC.PA`, `AIR FP` → `MC`, `AIR`) | not empty, in the configured ticker list |
| `company_name` | trim only: kept as typed, since the ticker is the key | not empty |
| `sector` | trim, lowercase, remove accents, map to an in-house nomenclature (`Banque`, `banking`, `Services financiers` → `finance`) | label known to the mapping |
| `isin` | trim, uppercase | if present: 2 letters, 9 letters or digits, 1 digit. Missing is allowed (`NULL`) |

Empty cells become `NULL` before validation. A rejected row is stored with its original, un-normalised values.

## Repository layout

```
data/   reference_assets.csv, the hand-typed, deliberately messy reference file
docs/   decisions, difficulties
scripts/ one-off utilities, not part of the pipeline (check_connection.py: database reachability check)
sql/    numbered migration scripts (tables, seed data, view), applied in order
src/    pipeline code (config, extract, validate, reconcile, transform, load, main)
tests/  pytest suite for the financial indicators (transform.py)
```

## Running it locally

1. Create the virtual environment and install the dependencies:
   ```
   python -m venv .venv
   .venv\Scripts\activate          # Windows; use source .venv/bin/activate elsewhere
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set `DATABASE_URL` to your PostgreSQL connection
   string.
3. Run the scripts in `sql/` in numerical order on the database.
4. Load the reference data, from `src/`. Do it first: the fact load needs `dim_asset`
   filled, otherwise every price lands on the unknown member.
   ```
   python -c "import main; main.upsert_reference_assets()"
   ```
5. Load the prices, the indicators and the fact table:
   ```
   python src/main.py
   ```

The tickers, the sector mapping and the data sources are configured in `src/config.py`.

## How this project was built

I used Claude Code as a tutor rather than a code generator: it explains, reviews and asks
questions, under the rules set out in [CLAUDE.md](CLAUDE.md). It writes code only when I
explicitly ask, which is very rare (<1% in the codebase). The aim is to be able to explain and rewrite every part of
this project without assistance.\
 The decision and difficulty logs are written by hand; this README was drafted with Claude and reviewed by me.
