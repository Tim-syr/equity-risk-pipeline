CREATE TABLE fact_daily_prices(
    date_id INTEGER REFERENCES dim_date (date_id),
    asset_id INTEGER REFERENCES dim_asset (asset_id),
    close NUMERIC NOT NULL,
    volume BIGINT NOT NULL,
    log_change DOUBLE PRECISION,
    volatility_21 DOUBLE PRECISION,
    drawdown DOUBLE PRECISION,
    PRIMARY KEY (date_id, asset_id)
);