CREATE TABLE sources(
    source_name TEXT PRIMARY KEY
);
INSERT INTO sources (source_name) VALUES ('yfinance');
INSERT INTO sources (source_name) VALUES ('reference_assets');

-- this is not run on the database yet, will do once the whole rejected rows scripts will be in place