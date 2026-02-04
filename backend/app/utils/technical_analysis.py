"""
Technical Analysis Utilities for Algorithmic Trading
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats

# Try to import TA-Lib, fall back to pure Python implementation if not available
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    from .technical_analysis_fallback import (
        sma, ema, macd, rsi, bbands, stoch, atr, adx, sar,
        willr, cci, roc, mom, obv
    )


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate comprehensive technical indicators for trading strategies
    """
    # Ensure we have the required columns
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    if TALIB_AVAILABLE:
        # Use TA-Lib implementation when available
        df['sma_10'] = talib.SMA(df['close'], timeperiod=10)
        df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
        df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
        df['sma_200'] = talib.SMA(df['close'], timeperiod=200)

        df['ema_12'] = talib.EMA(df['close'], timeperiod=12)
        df['ema_26'] = talib.EMA(df['close'], timeperiod=26)

        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'])

        # RSI
        df['rsi_14'] = talib.RSI(df['close'], timeperiod=14)
        df['rsi_7'] = talib.RSI(df['close'], timeperiod=7)

        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(df['close'])

        # Stochastic Oscillator
        df['stoch_k'], df['stoch_d'] = talib.STOCH(df['high'], df['low'], df['close'])

        # ATR (Average True Range)
        df['atr_14'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)

        # ADX (Average Directional Index)
        df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)

        # Parabolic SAR
        df['sar'] = talib.SAR(df['high'], df['low'], acceleration=0.02, maximum=0.2)

        # Williams %R
        df['williams_r'] = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=14)

        # Commodity Channel Index
        df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)

        # Rate of Change
        df['roc_10'] = talib.ROC(df['close'], timeperiod=10)

        # Momentum
        df['momentum_10'] = talib.MOM(df['close'], timeperiod=10)

        # Volume indicators
        df['vwap'] = calculate_vwap(df)
        df['obv'] = talib.OBV(df['close'], df['volume'])
    else:
        # Use pure Python fallback implementation
        df['sma_10'] = sma(df['close'], 10)
        df['sma_20'] = sma(df['close'], 20)
        df['sma_50'] = sma(df['close'], 50)
        df['sma_200'] = sma(df['close'], 200)

        df['ema_12'] = ema(df['close'], 12)
        df['ema_26'] = ema(df['close'], 26)

        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = macd(df['close'])

        # RSI
        df['rsi_14'] = rsi(df['close'], 14)
        df['rsi_7'] = rsi(df['close'], 7)

        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = bbands(df['close'])

        # Stochastic Oscillator
        df['stoch_k'], df['stoch_d'] = stoch(df['high'], df['low'], df['close'])

        # ATR (Average True Range)
        df['atr_14'] = atr(df['high'], df['low'], df['close'], 14)

        # ADX (Average Directional Index)
        df['adx'] = adx(df['high'], df['low'], df['close'], 14)

        # Parabolic SAR
        df['sar'] = sar(df['high'], df['low'])

        # Williams %R
        df['williams_r'] = willr(df['high'], df['low'], df['close'], 14)

        # Commodity Channel Index
        df['cci'] = cci(df['high'], df['low'], df['close'], 14)

        # Rate of Change
        df['roc_10'] = roc(df['close'], 10)

        # Momentum
        df['momentum_10'] = mom(df['close'], 10)

        # Volume indicators
        df['vwap'] = calculate_vwap(df)
        df['obv'] = obv(df['close'], df['volume'])

    # Volume-weighted indicators
    df['vwma_20'] = calculate_vwma(df['close'], df['volume'], 20)

    # Volatility
    df['volatility_20'] = df['close'].rolling(20).std()

    # Correlation with market index (if available)
    if 'nifty_close' in df.columns:
        df['corr_nifty_20'] = df['close'].rolling(20).corr(df['nifty_close'])

    # Previous values for crossover detection
    df['sma_20_prev'] = df['sma_20'].shift(1)
    df['sma_50_prev'] = df['sma_50'].shift(1)
    df['rsi_14_prev'] = df['rsi_14'].shift(1)
    df['macd_prev'] = df['macd'].shift(1)
    df['macd_signal_prev'] = df['macd_signal'].shift(1)

    return df


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Calculate Volume Weighted Average Price
    """
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    tpv = typical_price * df['volume']
    return tpv.cumsum() / df['volume'].cumsum()


def calculate_vwma(prices: pd.Series, volumes: pd.Series, period: int) -> pd.Series:
    """
    Calculate Volume Weighted Moving Average
    """
    pv = prices * volumes
    vwma = pv.rolling(window=period).sum() / volumes.rolling(window=period).sum()
    return vwma


def calculate_correlation_matrix(data: Dict[str, pd.Series]) -> pd.DataFrame:
    """
    Calculate correlation matrix between different assets
    """
    df = pd.DataFrame(data)
    return df.corr()


def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> float:
    """
    Calculate beta of a stock relative to market
    """
    # Remove NaN values
    combined = pd.concat([stock_returns, market_returns], axis=1).dropna()
    if len(combined) < 2:
        return 0.0
    
    cov_matrix = np.cov(combined.iloc[:, 0], combined.iloc[:, 1])
    stock_variance = cov_matrix[0, 0]
    covariance = cov_matrix[0, 1]
    
    if stock_variance == 0:
        return 0.0
    
    return covariance / stock_variance


def calculate_alpha(stock_returns: pd.Series, market_returns: pd.Series, risk_free_rate: float = 0.05) -> float:
    """
    Calculate alpha of a stock relative to market
    """
    if len(stock_returns) < 2 or len(market_returns) < 2:
        return 0.0
    
    avg_stock_return = stock_returns.mean() * 252  # Annualize
    avg_market_return = market_returns.mean() * 252  # Annualize
    
    beta = calculate_beta(stock_returns, market_returns)
    
    # CAPM: Expected return = risk_free_rate + beta * (market_return - risk_free_rate)
    expected_return = risk_free_rate + beta * (avg_market_return - risk_free_rate)
    
    # Alpha = actual return - expected return
    alpha = avg_stock_return - expected_return
    return alpha


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.05) -> float:
    """
    Calculate Sharpe ratio
    """
    if len(returns) < 2:
        return 0.0
    
    excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
    avg_excess_return = excess_returns.mean()
    volatility = returns.std()
    
    if volatility == 0:
        return 0.0
    
    return avg_excess_return / volatility * np.sqrt(252)  # Annualize


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.05) -> float:
    """
    Calculate Sortino ratio (uses downside deviation)
    """
    if len(returns) < 2:
        return 0.0
    
    excess_returns = returns - risk_free_rate/252
    avg_excess_return = excess_returns.mean()
    
    # Downside deviation (only negative returns)
    negative_returns = returns[returns < 0]
    if len(negative_returns) == 0:
        return float('inf') if avg_excess_return > 0 else 0.0
    
    downside_deviation = negative_returns.std()
    
    if downside_deviation == 0:
        return 0.0
    
    return avg_excess_return / downside_deviation * np.sqrt(252)  # Annualize


def calculate_max_drawdown(returns: pd.Series) -> float:
    """
    Calculate maximum drawdown
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def calculate_var(returns: pd.Series, confidence_level: float = 0.05) -> float:
    """
    Calculate Value at Risk
    """
    if len(returns) < 10:
        return 0.0
    
    return returns.quantile(confidence_level)


def calculate_expected_shortfall(returns: pd.Series, confidence_level: float = 0.05) -> float:
    """
    Calculate Expected Shortfall (Conditional VaR)
    """
    if len(returns) < 10:
        return 0.0
    
    var = calculate_var(returns, confidence_level)
    worst_returns = returns[returns <= var]
    return worst_returns.mean()


def detect_regime_changes(prices: pd.Series, window: int = 20) -> pd.Series:
    """
    Detect market regime changes using volatility and trend
    """
    returns = prices.pct_change()
    
    # Rolling volatility
    vol = returns.rolling(window).std()
    
    # Rolling trend (slope of linear regression)
    def rolling_slope(series):
        if len(series.dropna()) < 5:
            return 0
        x = np.arange(len(series))
        slope, _, _, _, _ = stats.linregress(x, series)
        return slope
    
    trend = returns.rolling(window).apply(rolling_slope)
    
    # Regime classification
    regime = pd.Series(index=prices.index, dtype=str)
    regime[:] = 'NORMAL'
    
    high_vol_mask = vol > vol.rolling(252).quantile(0.8)  # High volatility periods
    regime.loc[high_vol_mask] = 'VOLATILE'
    
    strong_trend_mask = abs(trend) > trend.rolling(252).quantile(0.8)  # Strong trends
    regime.loc[strong_trend_mask & high_vol_mask] = 'TRENDING_VOLATILE'
    regime.loc[strong_trend_mask & ~high_vol_mask] = 'TRENDING'
    
    return regime


def calculate_support_resistance(high: pd.Series, low: pd.Series, period: int = 20) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate dynamic support and resistance levels
    """
    resistance = high.rolling(period).max()
    support = low.rolling(period).min()
    return resistance, support


def calculate_volume_profile(df: pd.DataFrame, bins: int = 20) -> pd.Series:
    """
    Calculate volume profile
    """
    price_range = df['high'].max() - df['low'].min()
    bin_size = price_range / bins
    
    # Create price bins
    df['price_bin'] = ((df['close'] - df['low'].min()) / bin_size).astype(int)
    
    # Calculate volume per bin
    volume_profile = df.groupby('price_bin')['volume'].sum()
    
    return volume_profile


def calculate_market_regime_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate market regime indicators
    """
    # Volatility regime
    df['vol_regime'] = df['close'].pct_change().rolling(20).std()
    df['vol_regime_zscore'] = (df['vol_regime'] - df['vol_regime'].rolling(252).mean()) / df['vol_regime'].rolling(252).std()
    
    # Trend regime
    df['trend_regime'] = (df['close'] - df['close'].rolling(50).mean()) / df['close'].rolling(50).mean()
    
    # Momentum regime
    df['mom_regime'] = df['close'].pct_change(10)
    
    # Market breadth (if multiple assets are available)
    # This would typically be calculated across an index of stocks
    
    return df


def calculate_risk_metrics(returns: pd.Series, benchmark_returns: pd.Series = None) -> Dict[str, float]:
    """
    Calculate comprehensive risk metrics
    """
    metrics = {}
    
    # Basic metrics
    metrics['volatility'] = returns.std() * np.sqrt(252)
    metrics['sharpe_ratio'] = calculate_sharpe_ratio(returns)
    metrics['sortino_ratio'] = calculate_sortino_ratio(returns)
    metrics['max_drawdown'] = calculate_max_drawdown(returns)
    metrics['var_95'] = calculate_var(returns, 0.05)
    metrics['expected_shortfall'] = calculate_expected_shortfall(returns, 0.05)
    
    # Skewness and Kurtosis
    metrics['skewness'] = returns.skew()
    metrics['kurtosis'] = returns.kurtosis()
    
    # If benchmark is provided, calculate additional metrics
    if benchmark_returns is not None and len(benchmark_returns) == len(returns):
        # Beta
        metrics['beta'] = calculate_beta(returns, benchmark_returns)
        
        # Alpha
        metrics['alpha'] = calculate_alpha(returns, benchmark_returns)
        
        # Information Ratio
        excess_returns = returns - benchmark_returns
        tracking_error = excess_returns.std()
        if tracking_error != 0:
            metrics['information_ratio'] = excess_returns.mean() / tracking_error * np.sqrt(252)
        else:
            metrics['information_ratio'] = 0.0
    
    return metrics