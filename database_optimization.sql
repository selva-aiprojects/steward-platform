-- Database Optimization Script for StockSteward AI
-- This script creates indexes and optimizations to improve database performance

-- 1. Create indexes for frequently queried fields in the users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- 2. Create indexes for the trades table
CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_portfolio_id ON trades(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);

-- 3. Create indexes for the portfolios table
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);

-- 4. Create indexes for the holdings table
CREATE INDEX IF NOT EXISTS idx_holdings_portfolio_id ON holdings(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_holdings_symbol ON holdings(symbol);

-- 5. Create composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_trades_user_status ON trades(user_id, status);
CREATE INDEX IF NOT EXISTS idx_trades_symbol_timestamp ON trades(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_holdings_portfolio_symbol ON holdings(portfolio_id, symbol);

-- 6. Create indexes for audit logs if they exist
CREATE INDEX IF NOT EXISTS idx_audit_logs_admin_id ON audit_log(admin_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_log(timestamp);

-- 7. Optimize for common portfolio queries
CREATE INDEX IF NOT EXISTS idx_portfolios_user_cash ON portfolios(user_id, cash_balance);

-- 8. Add foreign key constraints if not present (ensuring data integrity)
-- These are typically handled by SQLAlchemy but adding for completeness
-- ALTER TABLE trades ADD CONSTRAINT fk_trades_user_id FOREIGN KEY (user_id) REFERENCES users(id);
-- ALTER TABLE trades ADD CONSTRAINT fk_trades_portfolio_id FOREIGN KEY (portfolio_id) REFERENCES portfolios(id);
-- ALTER TABLE holdings ADD CONSTRAINT fk_holdings_portfolio_id FOREIGN KEY (portfolio_id) REFERENCES portfolios(id);

-- 9. Create materialized view for frequently accessed aggregated data
-- This can significantly speed up dashboard queries
CREATE MATERIALIZED VIEW IF NOT EXISTS user_portfolio_summary AS
SELECT 
    u.id as user_id,
    u.full_name,
    u.role,
    p.id as portfolio_id,
    p.name as portfolio_name,
    p.cash_balance,
    p.invested_amount,
    COUNT(h.id) as holding_count,
    SUM(h.quantity * h.current_price) as current_value
FROM users u
JOIN portfolios p ON u.id = p.user_id
LEFT JOIN holdings h ON p.id = h.portfolio_id
GROUP BY u.id, u.full_name, u.role, p.id, p.name, p.cash_balance, p.invested_amount;

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW user_portfolio_summary;

-- 10. Create indexes on the materialized view
CREATE INDEX IF NOT EXISTS idx_user_portfolio_summary_user_id ON user_portfolio_summary(user_id);
CREATE INDEX IF NOT EXISTS idx_user_portfolio_summary_role ON user_portfolio_summary(role);

-- 11. Optimize for common trade analysis queries
CREATE INDEX IF NOT EXISTS idx_trades_user_symbol_action ON trades(user_id, symbol, action);
CREATE INDEX IF NOT EXISTS idx_trades_status_timestamp ON trades(status, timestamp);

-- 12. Add partial indexes for common filtered queries
CREATE INDEX IF NOT EXISTS idx_active_users ON users(id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_executed_trades ON trades(id) WHERE status = 'EXECUTED';

-- 13. Optimize for real-time market data queries
-- Create index for recent trades (common in market analysis)
CREATE INDEX IF NOT EXISTS idx_recent_trades ON trades(timestamp DESC) WHERE timestamp > NOW() - INTERVAL '7 days';

-- 14. Optimize for portfolio performance queries
CREATE INDEX IF NOT EXISTS idx_holdings_pnl ON holdings(pnl, pnl_pct);

-- 15. Add statistics for query planner (PostgreSQL specific)
ANALYZE users;
ANALYZE trades;
ANALYZE portfolios;
ANALYZE holdings;