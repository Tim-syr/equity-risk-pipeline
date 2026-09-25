CREATE TABLE rejected_rows(
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- auto generated id, replaces the older SERIAL
    source TEXT NOT NULL,
    raw_data JSONB NOT NULL,
    rejection_reason TEXT NOT NULL,
    times_seen INT NOT NULL DEFAULT 1,
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, raw_data)
);

-- this is not run on the database yet, will do once the whole rejected rows scripts will be in place