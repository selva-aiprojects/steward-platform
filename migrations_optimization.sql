-- Migration for portfolio optimization results

-- Create portfolio_optimization_results table
CREATE TABLE IF NOT EXISTS portfolio_optimization_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    strategy_name VARCHAR(255),
    symbol VARCHAR(20),
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    optimization_method VARCHAR(100),
    objective_metric VARCHAR(100),
    best_parameters JSONB,
    best_score DOUBLE PRECISION,
    execution_time DOUBLE PRECISION,
    status VARCHAR(50) DEFAULT 'COMPLETED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create strategy_optimization_results table
CREATE TABLE IF NOT EXISTS strategy_optimization_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    strategy_name VARCHAR(255),
    symbol VARCHAR(20),
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    parameter_space JSONB,
    best_parameters JSONB,
    best_score DOUBLE PRECISION,
    optimization_trace JSONB,
    execution_time DOUBLE PRECISION,
    status VARCHAR(50) DEFAULT 'COMPLETED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_portfolio_optimization_results_user_id ON portfolio_optimization_results(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_optimization_results_strategy ON portfolio_optimization_results(strategy_name);
CREATE INDEX IF NOT EXISTS idx_portfolio_optimization_results_symbol ON portfolio_optimization_results(symbol);
CREATE INDEX IF NOT EXISTS idx_portfolio_optimization_results_created_at ON portfolio_optimization_results(created_at);

CREATE INDEX IF NOT EXISTS idx_strategy_optimization_results_user_id ON strategy_optimization_results(user_id);
CREATE INDEX IF NOT EXISTS idx_strategy_optimization_results_strategy ON strategy_optimization_results(strategy_name);
CREATE INDEX IF NOT EXISTS idx_strategy_optimization_results_symbol ON strategy_optimization_results(symbol);
CREATE INDEX IF NOT EXISTS idx_strategy_optimization_results_created_at ON strategy_optimization_results(created_at);