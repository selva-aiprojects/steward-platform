-- Week 1 compliance gates

-- 1) User policy fields
ALTER TABLE users
  ADD COLUMN trading_suspended BOOLEAN DEFAULT FALSE,
  ADD COLUMN approval_threshold DOUBLE PRECISION,
  ADD COLUMN confidence_threshold DOUBLE PRECISION;

-- 1b) User role column
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS role VARCHAR(32) DEFAULT 'TRADER';

-- 2) Trade approvals queue
CREATE TABLE IF NOT EXISTS trade_approvals (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  status VARCHAR(32) DEFAULT 'PENDING',
  trade_payload TEXT NOT NULL,
  reason VARCHAR(255),
  approver_id INTEGER REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_trade_approvals_user_id ON trade_approvals (user_id);
CREATE INDEX IF NOT EXISTS ix_trade_approvals_status ON trade_approvals (status);
