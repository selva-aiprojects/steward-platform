-- Create trade_events table for persistent order lifecycle event tracking.
-- Safe to run multiple times.

CREATE TABLE IF NOT EXISTS trade_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    approval_id INTEGER REFERENCES trade_approvals(id),
    event_type VARCHAR(64) NOT NULL,
    payload TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_trade_events_user_id ON trade_events(user_id);
CREATE INDEX IF NOT EXISTS ix_trade_events_approval_id ON trade_events(approval_id);
CREATE INDEX IF NOT EXISTS ix_trade_events_event_type ON trade_events(event_type);
CREATE INDEX IF NOT EXISTS ix_trade_events_created_at ON trade_events(created_at);

