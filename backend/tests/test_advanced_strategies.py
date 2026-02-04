"""
Test suite for advanced trading strategies
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.strategies.advanced_strategies import AdvancedStrategies, EnsembleStrategy
from app.utils.technical_analysis import calculate_indicators


def create_sample_data():
    """
    Create sample market data for testing
    """
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    # Generate realistic OHLCV data
    returns = np.random.normal(0.0005, 0.02, len(dates))
    prices = [100]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    volumes = np.random.randint(1000000, 5000000, len(dates))
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': volumes
    })
    
    # Calculate indicators
    df = calculate_indicators(df)
    
    return df


def test_macd_strategy():
    """
    Test MACD strategy implementation
    """
    df = create_sample_data()
    
    # Test with the last row of data
    sample_row = df.iloc[-1]
    positions = {}
    cash = 100000
    
    signal = AdvancedStrategies.macd_strategy(sample_row, positions, cash)
    
    # The signal might be None depending on the data, but the function should not crash
    assert signal is None or hasattr(signal, 'symbol')


def test_stochastic_strategy():
    """
    Test Stochastic Oscillator strategy
    """
    df = create_sample_data()
    
    # Test with the last row of data
    sample_row = df.iloc[-1]
    positions = {}
    cash = 100000
    
    signal = AdvancedStrategies.stochastic_oscillator_strategy(sample_row, positions, cash)
    
    # The signal might be None depending on the data, but the function should not crash
    assert signal is None or hasattr(signal, 'symbol')


def test_bollinger_bands_strategy():
    """
    Test Bollinger Bands strategy
    """
    df = create_sample_data()
    
    # Test with the last row of data
    sample_row = df.iloc[-1]
    positions = {}
    cash = 100000
    
    signal = AdvancedStrategies.bollinger_bands_strategy(sample_row, positions, cash)
    
    # The signal might be None depending on the data, but the function should not crash
    assert signal is None or hasattr(signal, 'symbol')


def test_ensemble_strategy():
    """
    Test ensemble strategy combining multiple approaches
    """
    df = create_sample_data()
    
    # Test with the last row of data
    sample_row = df.iloc[-1]
    positions = {}
    cash = 100000
    
    ensemble = EnsembleStrategy()
    signal = ensemble.generate_signal(sample_row, positions, cash)
    
    # The signal might be None depending on the data, but the function should not crash
    assert signal is None or hasattr(signal, 'symbol')


def test_technical_indicator_calculation():
    """
    Test technical indicator calculation
    """
    df = create_sample_data()
    
    # Verify that indicators were calculated
    required_indicators = [
        'sma_10', 'sma_20', 'sma_50', 'sma_200',
        'ema_12', 'ema_26',
        'rsi_14', 'rsi_7',
        'bb_upper', 'bb_middle', 'bb_lower',
        'atr_14', 'adx'
    ]
    
    for indicator in required_indicators:
        assert indicator in df.columns, f"Missing indicator: {indicator}"
    
    # Verify that values are not all NaN
    for indicator in required_indicators:
        assert not df[indicator].isna().all(), f"All NaN values for indicator: {indicator}"


def test_risk_position_sizing():
    """
    Test risk-adjusted position sizing
    """
    from app.strategies.advanced_strategies import calculate_position_size
    
    # Test with realistic parameters
    account_value = 100000
    risk_percentage = 0.02  # 2% risk
    entry_price = 100
    stop_loss = 95  # 5% stop loss
    
    position_size = calculate_position_size(account_value, risk_percentage, entry_price, stop_loss)
    
    # Should be a positive integer
    assert isinstance(position_size, int)
    assert position_size >= 0
    
    # With 2% risk on $100,000 account, $5 risk per share, should get ~400 shares
    expected_size = (account_value * risk_percentage) / abs(entry_price - stop_loss)
    assert abs(position_size - expected_size) <= 1  # Allow for rounding


def test_calculate_atr():
    """
    Test ATR calculation
    """
    from app.strategies.advanced_strategies import calculate_atr
    
    # Create sample data
    dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
    high = pd.Series(np.random.uniform(105, 110, len(dates)))
    low = pd.Series(np.random.uniform(95, 100, len(dates)))
    close = pd.Series(np.random.uniform(100, 105, len(dates)))
    
    atr = calculate_atr(high, low, close)
    
    # Should have same length as input
    assert len(atr) == len(dates)
    
    # Should not be all NaN after the initial period
    assert not atr.isna().all()
    
    # Should be positive values
    assert (atr.dropna() >= 0).all()


def test_calculate_bollinger_bands():
    """
    Test Bollinger Bands calculation
    """
    from app.strategies.advanced_strategies import calculate_bollinger_bands
    
    # Create sample data
    dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
    close = pd.Series(np.random.uniform(100, 110, len(dates)))
    
    upper, lower, middle = calculate_bollinger_bands(close)
    
    # Should have same length as input
    assert len(upper) == len(dates)
    assert len(lower) == len(dates)
    assert len(middle) == len(dates)
    
    # Upper should be >= middle >= lower
    for u, m, l in zip(upper.dropna(), middle.dropna(), lower.dropna()):
        assert u >= m >= l


def test_calculate_macd():
    """
    Test MACD calculation
    """
    from app.strategies.advanced_strategies import calculate_macd
    
    # Create sample data
    dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
    close = pd.Series(np.random.uniform(100, 110, len(dates)))
    
    macd_line, signal_line, histogram = calculate_macd(close)
    
    # Should have same length as input
    assert len(macd_line) == len(dates)
    assert len(signal_line) == len(dates)
    assert len(histogram) == len(dates)
    
    # Should not be all NaN after the initial period
    assert not macd_line.isna().all()
    assert not signal_line.isna().all()
    assert not histogram.isna().all()


if __name__ == "__main__":
    pytest.main([__file__])