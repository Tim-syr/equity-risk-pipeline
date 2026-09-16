ALTER TABLE raw_prices
ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT now();
UPDATE raw_prices SET updated_at=ingested_at;