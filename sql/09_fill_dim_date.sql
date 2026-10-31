
INSERT INTO dim_date (date_id, full_date, year, quarter, month, day_of_week, is_trading_day)
SELECT 
    TO_CHAR(d, 'YYYYMMDD')::int,
    d::date,
    EXTRACT(YEAR FROM d),
    EXTRACT(QUARTER FROM d),
    EXTRACT(MONTH FROM d),
    EXTRACT(ISODOW FROM d),
    EXTRACT(ISODOW FROM d) <6
FROM generate_series(DATE '2021-01-01', DATE '2035-12-31', INTERVAL '1 day') AS d
ON CONFLICT (date_id) DO UPDATE SET is_trading_day = EXCLUDED.is_trading_day;