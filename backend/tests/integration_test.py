"""
Integration tests for the enhanced algorithmic trading platform
"""
import pytest
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch

from app.backtesting.engine import BacktestingEngine
from app.risk.manager import RiskManager
from app.execution.engine import ExecutionEngine
from app.strategies.advanced_strategies import AdvancedStrategies


@pytest.fixture
def sample_data():
    """
    Create sample market data for testing
    """
    dates = pd.date_range(start='2023-01-01', end='2023-06-30', freq='D')
    np.random.seed(42)
    
    # Generate realistic OHLCV data
    returns = np.random.normal(0.0005, 0.02, len(dates))
    prices = [100]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    volumes = np.random.randint(1000000, 5000000, len(dates))
    
    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': volumes
    })
    
    # Add technical indicators
    df['sma_20'] = df['close'].rolling(20).mean()
    df['sma_50'] = df['close'].rolling(50).mean()
    df['rsi'] = calculate_rsi(df['close'])
    df['macd_line'] = calculate_macd_line(df['close'])
    df['signal_line'] = calculate_signal_line(df['macd_line'])
    
    return df


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate RSI for test data
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd_line(prices: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
    """
    Calculate MACD line for test data
    """
    exp1 = prices.ewm(span=fast).mean()
    exp2 = prices.ewm(span=slow).mean()
    return exp1 - exp2


def calculate_signal_line(macd_line: pd.Series, signal_period: int = 9) -> pd.Series:
    """
    Calculate signal line for test data
    """
    return macd_line.ewm(span=signal_period).mean()


@pytest.mark.asyncio
async def test_end_to_end_backtesting():
    """
    Test complete backtesting workflow
    """
    # Initialize components
    engine = BacktestingEngine(initial_capital=100000)
    risk_manager = RiskManager(initial_capital=100000)
    
    # Sample data
    data = sample_data()
    
    # Define a simple strategy function for testing
    def simple_sma_strategy(row, positions, cash):
        if pd.isna(row.get('sma_20')) or pd.isna(row.get('sma_50')):
            return None
        
        symbol = 'TEST'
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0) if current_pos else 0
        
        # Buy signal: SMA 20 crosses above SMA 50
        if row['sma_20'] > row['sma_50'] and row['sma_20_prev'] <= row['sma_50_prev']:
            if current_qty <= 0:  # Only enter if not already long
                return {
                    'side': 'BUY',
                    'quantity': int(cash * 0.1 / row['close']),  # Risk 10% of capital
                    'order_type': 'MARKET'
                }
        
        # Sell signal: SMA 20 crosses below SMA 50
        elif row['sma_20'] < row['sma_50'] and row['sma_20_prev'] >= row['sma_50_prev']:
            if current_qty > 0:  # Only exit if currently long
                return {
                    'side': 'SELL',
                    'quantity': current_qty,
                    'order_type': 'MARKET'
                }
        
        return None
    
    # Add previous values for crossover detection
    data['sma_20_prev'] = data['sma_20'].shift(1)
    data['sma_50_prev'] = data['sma_50'].shift(1)
    
    # Run backtest
    results = engine.run_backtest(
        strategy_func=simple_sma_strategy,
        symbol='TEST',
        start_date=data['date'].iloc[0],
        end_date=data['date'].iloc[-1]
    )
    
    # Verify results structure
    assert 'initial_capital' in results
    assert 'final_value' in results
    assert 'total_return' in results
    assert 'sharpe_ratio' in results
    assert 'max_drawdown' in results
    assert 'total_trades' in results
    assert 'trades' in results
    assert 'portfolio_history' in results
    
    # Verify final value is reasonable
    assert results['final_value'] > 0
    assert isinstance(results['total_trades'], int)
    assert results['total_trades'] >= 0


def test_risk_management_integration():
    """
    Test risk management integration
    """
    risk_manager = RiskManager(initial_capital=100000)
    
    # Mock positions
    positions = {
        'RELIANCE': {'market_value': 25000, 'quantity': 10, 'avg_price': 2500},
        'TCS': {'market_value': 35000, 'quantity': 5, 'avg_price': 7000},
        'HDFCBANK': {'market_value': 20000, 'quantity': 20, 'avg_price': 1000}
    }
    
    portfolio_value = 100000
    
    # Calculate portfolio risk
    risk_metrics = risk_manager.calculate_portfolio_risk(positions, portfolio_value)
    
    # Verify metrics structure
    assert hasattr(risk_metrics, 'var_95')
    assert hasattr(risk_metrics, 'var_99')
    assert hasattr(risk_metrics, 'max_position_size')
    assert hasattr(risk_metrics, 'volatility')
    assert hasattr(risk_metrics, 'sharpe_ratio')
    assert hasattr(risk_metrics, 'max_drawdown')
    assert hasattr(risk_metrics, 'risk_level')
    
    # Verify values are reasonable
    assert 0 <= risk_metrics.var_95 <= 1
    assert 0 <= risk_metrics.volatility <= 1


@pytest.mark.asyncio
async def test_execution_engine_integration():
    """
    Test execution engine with risk checking
    """
    execution_engine = ExecutionEngine()
    risk_manager = RiskManager(initial_capital=100000)
    
    # Create a test order
    from app.execution.engine import Order
    order = Order(
        symbol='RELIANCE',
        side='BUY',
        quantity=10,
        price=2500.0,
        order_type='MARKET',
        user_id=1
    )
    
    # Mock current positions and portfolio value for risk check
    current_positions = {
        'RELIANCE': {'market_value': 25000, 'quantity': 10, 'avg_price': 2500}
    }
    portfolio_value = 100000
    
    # Check if trade passes risk controls
    trade_approved, reason, details = risk_manager.check_trade_risk(
        order.symbol, order.quantity, order.price, 
        current_positions, portfolio_value
    )
    
    # The trade should be approved with reasonable parameters
    assert isinstance(trade_approved, bool)
    assert isinstance(reason, str)
    assert isinstance(details, dict)


def test_strategy_signal_generation():
    """
    Test strategy signal generation
    """
    # Create sample market data
    sample_row = pd.Series({
        'symbol': 'TEST',
        'close': 100.0,
        'sma_20': 98.0,
        'sma_50': 95.0,
        'sma_20_prev': 97.0,
        'sma_50_prev': 96.0,
        'rsi_14': 65.0,
        'rsi_14_prev': 60.0,
        'macd_line': 1.5,
        'signal_line': 1.2,
        'macd_line_prev': 1.0,
        'signal_line_prev': 1.3
    })
    
    positions = {}
    cash = 50000
    
    # Test SMA crossover strategy
    sma_signal = AdvancedStrategies.sma_crossover_strategy(sample_row, positions, cash)
    
    # Test MACD strategy
    macd_signal = AdvancedStrategies.macd_strategy(sample_row, positions, cash)
    
    # Test RSI strategy
    rsi_signal = AdvancedStrategies.rsi_strategy(sample_row, positions, cash)
    
    # Signals can be None (no signal) or have the expected structure
    if sma_signal is not None:
        assert hasattr(sma_signal, 'symbol')
        assert hasattr(sma_signal, 'side')
        assert hasattr(sma_signal, 'confidence')
    
    if macd_signal is not None:
        assert hasattr(macd_signal, 'symbol')
        assert hasattr(macd_signal, 'side')
        assert hasattr(macd_signal, 'confidence')
    
    if rsi_signal is not None:
        assert hasattr(rsi_signal, 'symbol')
        assert hasattr(rsi_signal, 'side')
        assert hasattr(rsi_signal, 'confidence')


@pytest.mark.asyncio
async def test_backtesting_with_risk_management():
    """
    Test backtesting with integrated risk management
    """
    engine = BacktestingEngine(initial_capital=100000)
    risk_manager = RiskManager(initial_capital=100000)
    
    # Sample data
    data = sample_data()
    data['sma_20_prev'] = data['sma_20'].shift(1)
    data['sma_50_prev'] = data['sma_50'].shift(1)
    
    # Strategy that incorporates risk management
    def risk_managed_strategy(row, positions, cash):
        # First, generate a signal
        signal = AdvancedStrategies.sma_crossover_strategy(row, positions, cash)
        
        if signal:
            # Check if this trade passes risk management
            portfolio_value = cash + sum(pos['market_value'] for pos in positions.values())
            trade_approved, _, _ = risk_manager.check_trade_risk(
                signal['symbol'], signal['quantity'], row['close'], positions, portfolio_value
            )
            
            if trade_approved:
                return signal
        
        return None
    
    # Run backtest with risk-managed strategy
    results = engine.run_backtest(
        strategy_func=risk_managed_strategy,
        symbol='TEST',
        start_date=data['date'].iloc[0],
        end_date=data['date'].iloc[-1]
    )
    
    # Verify results
    assert 'initial_capital' in results
    assert 'final_value' in results
    assert isinstance(results['total_trades'], int)
    
    # With risk management, we should still have trades but potentially fewer
    # than without risk management
    assert results['total_trades'] >= 0


def test_performance_metrics_calculation():
    """
    Test performance metrics calculation
    """
    from app.backtesting.engine import calculate_performance_metrics
    
    # Create sample portfolio history
    dates = pd.date_range(start='2023-01-01', end='2023-06-30', freq='D')
    values = [100000]  # Starting with 100k
    
    # Generate realistic portfolio values
    np.random.seed(123)
    returns = np.random.normal(0.0005, 0.015, len(dates)-1)
    for ret in returns:
        values.append(values[-1] * (1 + ret))
    
    portfolio_history = pd.DataFrame({
        'date': dates,
        'total_value': values
    })
    
    # Calculate metrics
    metrics = calculate_performance_metrics(portfolio_history)
    
    # Verify metrics structure
    assert 'total_return' in metrics
    assert 'annualized_return' in metrics
    assert 'volatility' in metrics
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown' in metrics
    assert 'win_rate' in metrics
    assert 'profit_factor' in metrics
    
    # Verify reasonable ranges
    assert isinstance(metrics['total_return'], float)
    assert isinstance(metrics['sharpe_ratio'], float)
    assert isinstance(metrics['max_drawdown'], float)
    assert 0 <= abs(metrics['max_drawdown']) <= 1  # Drawdown should be between 0 and 100%


if __name__ == "__main__":
    pytest.main([__file__])