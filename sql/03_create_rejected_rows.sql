CREATE TABLE rejected_rows(
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    raw_data JSONB NOT NULL,
    rejection_reason TEXT NOT NULL,
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);