"""
Pydantic schemas for backtesting functionality
"""
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, List, Optional


class StrategyType(str, Enum):
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    ARBITRAGE = "arbitrage"


class BacktestRequest(BaseModel):
    """
    Request schema for backtesting
    """
    symbol: str = Field(..., description="Symbol to backtest on")
    strategy_name: str = Field(..., description="Name of the strategy to use")
    start_date: datetime = Field(..., description="Start date for backtest")
    end_date: datetime = Field(..., description="End date for backtest")
    initial_capital: float = Field(100000.0, ge=1000.0, description="Initial capital for backtest")
    commission_rate: float = Field(0.001, ge=0.0, le=0.05, description="Commission rate (0.001 = 0.1%)")
    slippage_rate: float = Field(0.0005, ge=0.0, le=0.01, description="Slippage rate (0.0005 = 0.05%)")
    risk_per_trade: float = Field(0.02, ge=0.001, le=0.1, description="Risk per trade (0.02 = 2%)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Strategy-specific parameters")


class PerformanceMetrics(BaseModel):
    """
    Performance metrics for backtesting results
    """
    total_return: float = Field(..., description="Total return over the period")
    annualized_return: float = Field(..., description="Annualized return")
    volatility: float = Field(..., description="Annualized volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    win_rate: float = Field(..., description="Win rate percentage")
    profit_factor: float = Field(..., description="Profit factor")
    total_trades: int = Field(..., description="Total number of trades")
    avg_win: float = Field(..., description="Average winning trade")
    avg_loss: float = Field(..., description="Average losing trade")
    best_trade: float = Field(..., description="Best single trade return")
    worst_trade: float = Field(..., description="Worst single trade return")


class TradeRecord(BaseModel):
    """
    Individual trade record from backtest
    """
    symbol: str
    side: str  # BUY or SELL
    quantity: int
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_pct: float


class PortfolioHistoryPoint(BaseModel):
    """
    Single point in portfolio history
    """
    timestamp: datetime
    total_value: float
    cash: float
    unrealized_pnl: float


class BacktestResults(BaseModel):
    """
    Results of a backtest run
    """
    initial_capital: float
    final_value: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    metrics: PerformanceMetrics
    trades: List[TradeRecord]
    portfolio_history: List[PortfolioHistoryPoint]
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime


class BacktestResponse(BaseModel):
    """
    Response schema for backtesting API
    """
    success: bool = Field(..., description="Whether the backtest was successful")
    results: BacktestResults = Field(..., description="Backtest results")
    strategy_name: str = Field(..., description="Name of the strategy used")
    symbol: str = Field(..., description="Symbol that was tested")
    start_date: datetime = Field(..., description="Start date of the test")
    end_date: datetime = Field(..., description="End date of the test")
    initial_capital: float = Field(..., description="Initial capital used for the test")


class OptimizationRequest(BaseModel):
    """
    Request schema for strategy parameter optimization
    """
    symbol: str = Field(..., description="Symbol to optimize for")
    strategy_name: str = Field(..., description="Name of strategy to optimize")
    start_date: datetime = Field(..., description="Start date for optimization period")
    end_date: datetime = Field(..., description="End date for optimization period")
    parameter_space: Dict[str, List[Any]] = Field(..., description="Parameter space to search")
    objective_metric: str = Field("sharpe_ratio", description="Metric to optimize for")
    optimization_method: str = Field("grid_search", description="Optimization method to use")


class OptimizationResult(BaseModel):
    """
    Result schema for parameter optimization
    """
    best_parameters: Dict[str, Any] = Field(..., description="Best parameters found")
    best_score: float = Field(..., description="Best score achieved")
    best_strategy: str = Field(..., description="Best strategy name")
    optimization_trace: List[Dict[str, Any]] = Field(..., description="Trace of optimization steps")
    execution_time: float = Field(..., description="Time taken for optimization in seconds")


class StrategyMetadata(BaseModel):
    """
    Metadata about a trading strategy
    """
    name: str = Field(..., description="Unique name of the strategy")
    description: str = Field(..., description="Description of the strategy")
    type: StrategyType = Field(..., description="Type of strategy")
    parameters: List[Dict[str, Any]] = Field(..., description="Expected parameters")
    required_data: List[str] = Field(..., description="Required market data fields")
    risk_level: str = Field(..., description="Risk level (LOW, MEDIUM, HIGH)")


class LiveStrategyRequest(BaseModel):
    """
    Request to deploy a strategy in live trading
    """
    strategy_name: str = Field(..., description="Name of strategy to deploy")
    symbol: str = Field(..., description="Symbol to trade")
    initial_capital: float = Field(..., gt=0, description="Capital to allocate")
    risk_per_trade: float = Field(0.02, gt=0, le=0.1, description="Risk per trade")
    max_position_size: float = Field(0.1, gt=0, le=1.0, description="Max position size as % of capital")
    stop_loss: float = Field(0.05, gt=0, le=0.2, description="Stop loss as % of entry price")
    take_profit: float = Field(0.1, gt=0, le=0.5, description="Take profit as % of entry price")
    paper_trading: bool = Field(True, description="Whether to run in paper trading mode")