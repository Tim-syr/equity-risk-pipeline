CREATE TABLE daily_metrics(
    ticker VARCHAR(10),
    date DATE,
    log_change DOUBLE PRECISION, -- calculated value by python floats, not exact like a numeric value
    volatility_21 DOUBLE PRECISION,
    drawdown DOUBLE PRECISION,
    ingested_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (ticker, date)
);