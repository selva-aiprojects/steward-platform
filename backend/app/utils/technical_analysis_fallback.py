"""
Pure Python Technical Analysis Indicators (Fallback without TA-Lib)
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats


def sma(close: pd.Series, timeperiod: int) -> pd.Series:
    """Simple Moving Average"""
    return close.rolling(window=timeperiod).mean()


def ema(close: pd.Series, timeperiod: int) -> pd.Series:
    """Exponential Moving Average"""
    return close.ewm(span=timeperiod).mean()


def macd(close: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Moving Average Convergence Divergence"""
    exp1 = close.ewm(span=12).mean()
    exp2 = close.ewm(span=26).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=9).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def rsi(close: pd.Series, timeperiod: int = 14) -> pd.Series:
    """Relative Strength Index"""
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=timeperiod).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=timeperiod).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def bbands(close: pd.Series, timeperiod: int = 5, nbdevup: float = 2.0, nbdevdn: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands"""
    ma = close.rolling(window=timeperiod).mean()
    std = close.rolling(window=timeperiod).std()
    upper = ma + (std * nbdevup)
    middle = ma
    lower = ma - (std * nbdevdn)
    return upper, middle, lower


def stoch(high: pd.Series, low: pd.Series, close: pd.Series, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator"""
    lowest_low = low.rolling(window=fastk_period).min()
    highest_high = high.rolling(window=fastk_period).max()
    fastk = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    slowk = fastk.rolling(window=slowk_period).mean()
    slowd = slowk.rolling(window=slowd_period).mean()
    return slowk, slowd


def atr(high: pd.Series, low: pd.Series, close: pd.Series, timeperiod: int = 14) -> pd.Series:
    """Average True Range"""
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    tr = np.maximum(np.maximum(high_low, high_close), low_close)
    atr = tr.rolling(window=timeperiod).mean()
    return atr


def adx(high: pd.Series, low: pd.Series, close: pd.Series, timeperiod: int = 14) -> pd.Series:
    """Average Directional Index"""
    # Calculate True Range
    tr = atr(high, low, close, 1)  # Just get the TR calculation
    
    # Calculate directional movements
    plus_dm = high - high.shift(1)
    minus_dm = low.shift(1) - low
    
    # Clean directional movements
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    
    # Smooth the DM values
    plus_di = 100 * (plus_dm.rolling(window=timeperiod).mean() / tr.rolling(window=timeperiod).mean())
    minus_di = 100 * (minus_dm.rolling(window=timeperiod).mean() / tr.rolling(window=timeperiod).mean())
    
    # Calculate DX and ADX
    dx = 100 * (np.abs(plus_di - minus_di) / (plus_di + minus_di))
    adx = dx.rolling(window=timeperiod).mean()
    
    return adx


def sar(high: pd.Series, low: pd.Series, acceleration: float = 0.02, maximum: float = 0.2) -> pd.Series:
    """Parabolic SAR - simplified but functional implementation."""
    if len(high) == 0:
        return pd.Series(dtype=float)

    highs = high.to_numpy()
    lows = low.to_numpy()
    sar_values = np.full(len(highs), np.nan, dtype=float)

    # Initialize trend based on first two bars if available
    if len(highs) > 1 and highs[1] >= highs[0]:
        uptrend = True
        ep = highs[0]
        sar = lows[0]
    else:
        uptrend = False
        ep = lows[0]
        sar = highs[0]

    af = acceleration
    sar_values[0] = sar

    for i in range(1, len(highs)):
        # Project SAR
        sar = sar + af * (ep - sar)

        # Clamp SAR to prior extremes
        if uptrend:
            prior_low = lows[i - 1]
            if i > 1:
                prior_low = min(prior_low, lows[i - 2])
            sar = min(sar, prior_low)
        else:
            prior_high = highs[i - 1]
            if i > 1:
                prior_high = max(prior_high, highs[i - 2])
            sar = max(sar, prior_high)

        # Check for reversal
        if uptrend:
            if lows[i] < sar:
                uptrend = False
                sar = ep
                ep = lows[i]
                af = acceleration
            else:
                if highs[i] > ep:
                    ep = highs[i]
                    af = min(af + acceleration, maximum)
        else:
            if highs[i] > sar:
                uptrend = True
                sar = ep
                ep = highs[i]
                af = acceleration
            else:
                if lows[i] < ep:
                    ep = lows[i]
                    af = min(af + acceleration, maximum)

        sar_values[i] = sar

    return pd.Series(sar_values, index=high.index)


def willr(high: pd.Series, low: pd.Series, close: pd.Series, timeperiod: int = 14) -> pd.Series:
    """Williams %R"""
    highest_high = high.rolling(window=timeperiod).max()
    lowest_low = low.rolling(window=timeperiod).min()
    willr = (highest_high - close) / (highest_high - lowest_low) * -100
    return willr


def cci(high: pd.Series, low: pd.Series, close: pd.Series, timeperiod: int = 14) -> pd.Series:
    """Commodity Channel Index"""
    typical_price = (high + low + close) / 3
    ma_tp = typical_price.rolling(window=timeperiod).mean()
    mean_dev = typical_price.rolling(window=timeperiod).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    cci = (typical_price - ma_tp) / (0.015 * mean_dev)
    return cci


def roc(close: pd.Series, timeperiod: int = 10) -> pd.Series:
    """Rate of Change"""
    return ((close - close.shift(timeperiod)) / close.shift(timeperiod)) * 100


def mom(close: pd.Series, timeperiod: int = 10) -> pd.Series:
    """Momentum"""
    return close - close.shift(timeperiod)


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On Balance Volume"""
    obv = pd.Series(index=close.index, dtype=float)
    obv.iloc[0] = volume.iloc[0]
    
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    return obv
