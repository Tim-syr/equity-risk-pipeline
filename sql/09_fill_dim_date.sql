
INSERT INTO dim_date (date_id, full_date, year, quarter, month, day_of_week, is_trading_day)
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::int AS date_id,
    d::date AS full_date,
    EXTRACT(YEAR FROM d) AS year,
    EXTRACT(QUARTER FROM d) AS quarter,
    EXTRACT(MONTH FROM d) AS month,
    EXTRACT(ISODOW FROM d) AS day_of_week,
    EXTRACT(ISODOW FROM d) <6 AND d::date NOT IN (SELECT date FROM euronext_holidays) AS is_trading_day
FROM generate_series(DATE '2021-01-01', DATE '2035-12-31', INTERVAL '1 day') AS d
ON CONFLICT (date_id) DO UPDATE SET is_trading_day = EXCLUDED.is_trading_day;