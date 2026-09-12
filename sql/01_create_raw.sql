CREATE TABLE raw_prices (
    ticker VARCHAR(10), -- primary keys, not null by default
    date DATE,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume BIGINT NOT NULL,
    ingested_at TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (ticker, date)
);