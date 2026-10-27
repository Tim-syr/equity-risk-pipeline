CREATE TABLE company_information (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    isin VARCHAR(12) CHECK (LENGTH(isin) = 12),
    ingested_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);