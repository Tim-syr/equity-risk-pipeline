CREATE TABLE dim_asset(
    asset_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL CHECK (ticker != ''),
    isin VARCHAR(12) CHECK (LENGTH(isin) = 12),
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    country VARCHAR(2) CHECK (LENGTH(country) = 2),
    currency VARCHAR(3) NOT NULL
);

INSERT INTO dim_asset (asset_id, ticker, isin, company_name, sector, country, currency) OVERRIDING SYSTEM VALUE VALUES (-1, 'UNKNOWN', NULL, 'unknown', 'unknown', NULL, 'EUR');