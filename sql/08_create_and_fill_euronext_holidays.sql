CREATE TABLE euronext_holidays(
    date DATE PRIMARY KEY,
    name TEXT NOT NULL CHECK (name != '')
);
INSERT INTO euronext_holidays VALUES
    (DATE '2026-01-01', 'New Year''s Day'),
    (DATE '2026-04-03', 'Good Friday'),
    (DATE '2026-04-06', 'Easter Monday'),
    (DATE '2026-05-01', 'Labour Day'),
    (DATE '2026-12-25', 'Christmas Day'),
    (DATE '2026-12-26', 'Boxing Day');