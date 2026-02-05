"""
Advanced Algorithmic Trading Strategies
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Signal:
    """
    Trading signal with confidence and rationale
    """
    symbol: str
    side: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0.0 to 1.0
    strength: float  # -1.0 to 1.0, negative for SELL
    rationale: str
    quantity: Optional[int] = None
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    def __getitem__(self, item: str):
        return getattr(self, item)

    def get(self, item: str, default: Any = None):
        return getattr(self, item, default)


class AdvancedStrategies:
    """
    Collection of advanced algorithmic trading strategies
    """
    
    @staticmethod
    def sma_crossover_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        SMA crossover strategy (short-term vs long-term)
        """
        if pd.isna(data.get('sma_20')) or pd.isna(data.get('sma_50')):
            return None

        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        price = data.get('close', 0)

        if price <= 0:
            return None

        quantity = max(int(cash * 0.1 / price), 0)

        # Bullish crossover
        if (data['sma_20'] > data['sma_50'] and
                data.get('sma_20_prev', 0) <= data.get('sma_50_prev', 0)):
            if current_qty <= 0 and quantity > 0:
                return Signal(
                    symbol=symbol,
                    side='BUY',
                    quantity=quantity,
                    confidence=0.7,
                    strength=0.6,
                    rationale='SMA bullish crossover',
                    price_target=price * 1.05,
                    stop_loss=price * 0.98
                )

        # Bearish crossover
        if (data['sma_20'] < data['sma_50'] and
                data.get('sma_20_prev', 0) >= data.get('sma_50_prev', 0)):
            if current_qty > 0:
                return Signal(
                    symbol=symbol,
                    side='SELL',
                    quantity=current_qty,
                    confidence=0.7,
                    strength=-0.6,
                    rationale='SMA bearish crossover',
                    price_target=price * 0.95,
                    stop_loss=price * 1.02
                )

        return None

    @staticmethod
    def rsi_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        RSI mean reversion strategy (uses rsi_14 if available)
        """
        rsi = data.get('rsi_14', data.get('rsi'))
        if pd.isna(rsi):
            return None

        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        price = data.get('close', 0)

        if price <= 0:
            return None

        quantity = max(int(cash * 0.05 / price), 0)

        if rsi < 30 and current_qty <= 0 and quantity > 0:
            return Signal(
                symbol=symbol,
                side='BUY',
                quantity=quantity,
                confidence=0.6,
                strength=0.5,
                rationale='RSI oversold mean reversion',
                price_target=price * 1.04,
                stop_loss=price * 0.97
            )
        if rsi > 70 and current_qty > 0:
            return Signal(
                symbol=symbol,
                side='SELL',
                quantity=current_qty,
                confidence=0.6,
                strength=-0.5,
                rationale='RSI overbought mean reversion',
                price_target=price * 0.96,
                stop_loss=price * 1.03
            )

        return None

    @staticmethod
    def macd_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        MACD (Moving Average Convergence Divergence) strategy
        """
        if pd.isna(data.get('macd_line')) or pd.isna(data.get('signal_line')):
            return None
        
        macd = data['macd_line']
        signal = data['signal_line']
        histogram = data.get('macd_histogram', macd - signal)
        
        # Previous values for crossover detection
        prev_macd = data.get('macd_line_prev', 0)
        prev_signal = data.get('signal_line_prev', 0)
        
        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        price = data.get('close', 0)
        quantity = max(int(cash * 0.08 / price), 0) if price > 0 else 0
        
        # Bullish crossover: MACD line crosses above signal line
        if macd > signal and prev_macd <= prev_signal:
            if current_qty <= 0:  # Only enter if not already long
                confidence = min(abs(histogram) * 2, 1.0)  # Higher histogram = higher confidence
                return Signal(
                    symbol=symbol,
                    side='BUY',
                    quantity=quantity,
                    confidence=confidence,
                    strength=abs(histogram),
                    rationale=f'MACD bullish crossover: MACD({macd:.3f}) crossed above Signal({signal:.3f})',
                    price_target=data.get('close') * 1.05,  # 5% target
                    stop_loss=data.get('close') * 0.98  # 2% stop loss
                )
        
        # Bearish crossover: MACD line crosses below signal line
        elif macd < signal and prev_macd >= prev_signal:
            if current_qty > 0:  # Only exit if currently long
                confidence = min(abs(histogram) * 2, 1.0)
                return Signal(
                    symbol=symbol,
                    side='SELL',
                    quantity=current_qty,
                    confidence=confidence,
                    strength=-abs(histogram),
                    rationale=f'MACD bearish crossover: MACD({macd:.3f}) crossed below Signal({signal:.3f})',
                    price_target=data.get('close') * 0.95,  # 5% target down
                    stop_loss=data.get('close') * 1.02  # 2% stop loss (for short)
                )
        
        return None
    
    @staticmethod
    def stochastic_oscillator_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        Stochastic Oscillator mean reversion strategy
        """
        if pd.isna(data.get('stoch_k')) or pd.isna(data.get('stoch_d')):
            return None
        
        k = data['stoch_k']
        d = data['stoch_d']
        
        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        price = data.get('close', 0)
        quantity = max(int(cash * 0.05 / price), 0) if price > 0 else 0
        
        # Oversold condition: Look for long
        if k < 20 and d < 20 and k > d:  # K crosses above D in oversold zone
            if current_qty <= 0:
                confidence = min((30 - k) / 10, 1.0)  # Higher confidence when deeper oversold
                return Signal(
                    symbol=symbol,
                    side='BUY',
                    quantity=quantity,
                    confidence=confidence,
                    strength=(30 - k) / 30,
                    rationale=f'Stochastic oversold bounce: K({k:.2f}) crossed above D({d:.2f}) in oversold zone',
                    price_target=data.get('close') * 1.03,
                    stop_loss=data.get('close') * 0.98
                )
        
        # Overbought condition: Look for short
        elif k > 80 and d > 80 and k < d:  # K crosses below D in overbought zone
            if current_qty > 0:
                confidence = min((k - 70) / 10, 1.0)  # Higher confidence when deeper overbought
                return Signal(
                    symbol=symbol,
                    side='SELL',
                    quantity=current_qty,
                    confidence=confidence,
                    strength=-(k - 70) / 30,
                    rationale=f'Stochastic overbought reversal: K({k:.2f}) crossed below D({d:.2f}) in overbought zone',
                    price_target=data.get('close') * 0.97,
                    stop_loss=data.get('close') * 1.02
                )
        
        return None
    
    @staticmethod
    def bollinger_bands_breakout_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        Bollinger Bands breakout strategy (different from mean reversion)
        """
        if pd.isna(data.get('bb_upper')) or pd.isna(data.get('bb_lower')) or pd.isna(data.get('bb_middle')):
            return None
        
        price = data['close']
        upper_band = data['bb_upper']
        lower_band = data['bb_lower']
        middle_band = data['bb_middle']
        
        # Band width (volatility measure)
        band_width = (upper_band - lower_band) / middle_band
        
        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        quantity = max(int(cash * 0.08 / price), 0) if price > 0 else 0
        
        # Breakout above upper band (bullish)
        if price > upper_band and data.get('close_prev', 0) <= data.get('bb_upper_prev', 0):
            if current_qty <= 0:
                # High confidence if band width is expanding (increasing volatility)
                confidence = min(0.7 + (band_width - data.get('bb_width_prev', band_width)) * 5, 1.0)
                return Signal(
                    symbol=symbol,
                    side='BUY',
                    quantity=quantity,
                    confidence=confidence,
                    strength=0.8,
                    rationale=f'Bollinger Bands breakout: Price({price:.2f}) broke above upper band({upper_band:.2f})',
                    price_target=price * 1.08,
                    stop_loss=middle_band
                )
        
        # Breakdown below lower band (bearish)
        elif price < lower_band and data.get('close_prev', 0) >= data.get('bb_lower_prev', 0):
            if current_qty > 0:
                confidence = min(0.7 + (band_width - data.get('bb_width_prev', band_width)) * 5, 1.0)
                return Signal(
                    symbol=symbol,
                    side='SELL',
                    quantity=current_qty,
                    confidence=confidence,
                    strength=-0.8,
                    rationale=f'Bollinger Bands breakdown: Price({price:.2f}) broke below lower band({lower_band:.2f})',
                    price_target=price * 0.92,
                    stop_loss=middle_band
                )
        
        return None

    @staticmethod
    def bollinger_bands_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        Bollinger Bands mean reversion strategy
        """
        if pd.isna(data.get('bb_upper')) or pd.isna(data.get('bb_lower')):
            return None

        price = data.get('close', 0)
        upper_band = data.get('bb_upper')
        lower_band = data.get('bb_lower')
        middle_band = data.get('bb_middle', (upper_band + lower_band) / 2)

        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        quantity = max(int(cash * 0.05 / price), 0) if price > 0 else 0

        if price < lower_band and current_qty <= 0 and quantity > 0:
            return Signal(
                symbol=symbol,
                side='BUY',
                quantity=quantity,
                confidence=0.6,
                strength=0.5,
                rationale='Bollinger mean reversion: price below lower band',
                price_target=middle_band,
                stop_loss=price * 0.97
            )
        if price > upper_band and current_qty > 0:
            return Signal(
                symbol=symbol,
                side='SELL',
                quantity=current_qty,
                confidence=0.6,
                strength=-0.5,
                rationale='Bollinger mean reversion: price above upper band',
                price_target=middle_band,
                stop_loss=price * 1.03
            )

        return None

    @staticmethod
    def atr_trailing_stop_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        ATR (Average True Range) based trailing stop strategy
        """
        if pd.isna(data.get('atr_14')):
            return None
        
        atr = data['atr_14']
        price = data['close']
        
        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        
        if current_pos and current_pos.get('quantity', 0) > 0:
            # Check if we need to exit based on ATR trailing stop
            entry_price = current_pos.get('avg_price', price)
            stop_distance = atr * 2  # 2x ATR stop distance
            
            if current_pos.get('side') == 'LONG':
                stop_level = entry_price - stop_distance
                if price <= stop_level:
                    return Signal(
                        symbol=symbol,
                        side='SELL',
                        confidence=0.9,
                        strength=-0.9,
                        rationale=f'ATR trailing stop triggered: Price({price:.2f}) below stop({stop_level:.2f}), ATR({atr:.2f})',
                        stop_loss=stop_level
                    )
            elif current_pos.get('side') == 'SHORT':
                stop_level = entry_price + stop_distance
                if price >= stop_level:
                    return Signal(
                        symbol=symbol,
                        side='BUY',  # Cover short
                        confidence=0.9,
                        strength=0.9,
                        rationale=f'ATR trailing stop triggered: Price({price:.2f}) above stop({stop_level:.2f}), ATR({atr:.2f})',
                        stop_loss=stop_level
                    )
        
        return None
    
    @staticmethod
    def ichimoku_cloud_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        Ichimoku Cloud strategy
        """
        required_fields = ['tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b', 'chikou_span']
        if not all(pd.notna(data.get(field)) for field in required_fields):
            return None
        
        price = data['close']
        tenkan = data['tenkan_sen']
        kijun = data['kijun_sen']
        senkou_a = data['senkou_span_a']
        senkou_b = data['senkou_span_b']
        chikou = data.get('chikou_span', price)  # Usually current price shifted back
        
        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        
        # Check if price is above/below cloud
        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)
        
        # Bullish conditions
        bullish_signals = [
            price > cloud_top,  # Price above cloud
            tenkan > kijun,     # Tenkan above Kijun
            price > tenkan,     # Price above Tenkan
            chikou > price      # Lagging span above current price
        ]
        
        # Bearish conditions
        bearish_signals = [
            price < cloud_bottom,  # Price below cloud
            tenkan < kijun,        # Tenkan below Kijun
            price < tenkan,        # Price below Tenkan
            chikou < price         # Lagging span below current price
        ]
        
        # Buy signal: Strong bullish alignment
        if all(bullish_signals) and current_qty <= 0:
            confidence = sum(bullish_signals) / len(bullish_signals) * 0.8
            return Signal(
                symbol=symbol,
                side='BUY',
                confidence=confidence,
                strength=0.8,
                rationale='Ichimoku Cloud bullish alignment: Price above cloud, Tenkan>Kijun, Chikou above price',
                price_target=cloud_top * 1.05,
                stop_loss=cloud_top * 0.98
            )
        
        # Sell signal: Strong bearish alignment
        elif all(bearish_signals) and current_qty > 0:
            confidence = sum(bearish_signals) / len(bearish_signals) * 0.8
            return Signal(
                symbol=symbol,
                side='SELL',
                confidence=confidence,
                strength=-0.8,
                rationale='Ichimoku Cloud bearish alignment: Price below cloud, Tenkan<Kijun, Chikou below price',
                price_target=cloud_bottom * 0.95,
                stop_loss=cloud_bottom * 1.02
            )
        
        return None
    
    @staticmethod
    def vwap_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        VWAP (Volume Weighted Average Price) strategy
        """
        if pd.isna(data.get('vwap')):
            return None
        
        price = data['close']
        vwap = data['vwap']
        
        # Calculate deviation from VWAP
        deviation = (price - vwap) / vwap
        
        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        
        # Buy when price is below VWAP (considered cheap)
        if deviation < -0.01 and current_qty <= 0:  # 1% below VWAP
            confidence = min(abs(deviation) * 2, 0.9)  # Higher confidence with greater deviation
            return Signal(
                symbol=symbol,
                side='BUY',
                confidence=confidence,
                strength=abs(deviation),
                rationale=f'VWAP mean reversion: Price({price:.2f}) {deviation:.2%} below VWAP({vwap:.2f})',
                price_target=vwap,
                stop_loss=price * 0.98
            )
        
        # Sell when price is above VWAP (considered expensive)
        elif deviation > 0.01 and current_qty > 0:  # 1% above VWAP
            confidence = min(deviation * 2, 0.9)
            return Signal(
                symbol=symbol,
                side='SELL',
                confidence=confidence,
                strength=-deviation,
                rationale=f'VWAP mean reversion: Price({price:.2f}) {deviation:.2%} above VWAP({vwap:.2f})',
                price_target=vwap,
                stop_loss=price * 1.02
            )
        
        return None
    
    @staticmethod
    def multi_timeframe_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        Multi-timeframe strategy combining signals from different timeframes
        """
        # This would typically require data from multiple timeframes
        # For simplicity, we'll use different periods of the same indicators
        
        if pd.isna(data.get('sma_20')) or pd.isna(data.get('sma_200')):
            return None
        
        price = data['close']
        sma_20 = data['sma_20']
        sma_200 = data['sma_200']
        
        # Short-term trend (momentum)
        short_trend = 1 if price > sma_20 else -1
        # Long-term trend (direction)
        long_trend = 1 if price > sma_200 else -1
        
        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        
        # Only take trades when short and long trends align
        if short_trend == 1 and long_trend == 1 and current_qty <= 0:  # Bullish alignment
            confidence = 0.8  # High confidence when timeframes align
            return Signal(
                symbol=symbol,
                side='BUY',
                confidence=confidence,
                strength=0.7,
                rationale=f'Multi-timeframe bullish: Price above both SMA20({sma_20:.2f}) and SMA200({sma_200:.2f})',
                price_target=price * 1.06,
                stop_loss=sma_200 * 0.99  # Protect with long-term trend
            )
        
        elif short_trend == -1 and long_trend == -1 and current_qty > 0:  # Bearish alignment
            confidence = 0.8
            return Signal(
                symbol=symbol,
                side='SELL',
                confidence=confidence,
                strength=-0.7,
                rationale=f'Multi-timeframe bearish: Price below both SMA20({sma_20:.2f}) and SMA200({sma_200:.2f})',
                price_target=price * 0.94,
                stop_loss=sma_200 * 1.01  # Protect with long-term trend
            )
        
        return None


# Ensemble strategy that combines multiple strategies
class EnsembleStrategy:
    """
    Combines multiple strategies with weighted voting
    """
    
    def __init__(self, strategy_weights: Dict[str, float] = None):
        self.strategies = {
            'macd': AdvancedStrategies.macd_strategy,
            'stochastic': AdvancedStrategies.stochastic_oscillator_strategy,
            'bollinger_breakout': AdvancedStrategies.bollinger_bands_breakout_strategy,
            'ichimoku': AdvancedStrategies.ichimoku_cloud_strategy,
            'multi_timeframe': AdvancedStrategies.multi_timeframe_strategy
        }
        
        # Default weights - can be adjusted based on backtest performance
        self.weights = strategy_weights or {
            'macd': 0.25,
            'stochastic': 0.20,
            'bollinger_breakout': 0.20,
            'ichimoku': 0.20,
            'multi_timeframe': 0.15
        }
    
    def generate_signal(self, data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        Generate ensemble signal by combining multiple strategies
        """
        signals = []
        
        for strategy_name, strategy_func in self.strategies.items():
            weight = self.weights.get(strategy_name, 0)
            if weight > 0:  # Only consider strategies with positive weight
                try:
                    signal = strategy_func(data, positions, cash)
                    if signal:
                        signals.append((signal, weight))
                except Exception as e:
                    print(f"Error in {strategy_name} strategy: {e}")
        
        if not signals:
            return None
        
        # Calculate weighted average of signals
        total_weight = sum(weight for _, weight in signals)
        if total_weight == 0:
            return None
        
        # Aggregate signals
        weighted_strength = sum(signal.strength * weight for signal, weight in signals)
        avg_confidence = sum(signal.confidence * weight for signal, weight in signals) / total_weight
        
        # Determine overall side based on weighted strength
        if weighted_strength > 0.1:  # Threshold to avoid weak signals
            side = 'BUY'
        elif weighted_strength < -0.1:
            side = 'SELL'
        else:
            return None  # Neutral signal
        
        # Find the strongest contributing signal for rationale
        strongest_signal = max(signals, key=lambda x: abs(x[0].strength * x[1]))
        
        return Signal(
            symbol=strongest_signal[0].symbol,
            side=side,
            confidence=min(avg_confidence, 1.0),
            strength=weighted_strength,
            rationale=f'Ensemble signal ({len(signals)} strategies): Combined weighted strength {weighted_strength:.3f}',
            price_target=strongest_signal[0].price_target,
            stop_loss=strongest_signal[0].stop_loss,
            take_profit=strongest_signal[0].take_profit
        )


# Risk-adjusted position sizing
def calculate_position_size(account_value: float, risk_percentage: float, 
                          entry_price: float, stop_loss: float) -> int:
    """
    Calculate position size based on risk management
    """
    risk_amount = account_value * risk_percentage
    price_risk = abs(entry_price - stop_loss)
    
    if price_risk == 0:
        return 0  # Can't calculate position size without risk
    
    position_size = risk_amount / price_risk
    return int(position_size)


# Utility functions for strategy development
def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range
    """
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR
    atr = true_range.rolling(window=period).mean()
    return atr


def calculate_bollinger_bands(close: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
    """
    Calculate Bollinger Bands
    """
    sma = close.rolling(window=period).mean()
    rolling_std = close.rolling(window=period).std()
    
    upper_band = sma + (rolling_std * std_dev)
    lower_band = sma - (rolling_std * std_dev)
    
    return upper_band, lower_band, sma


def calculate_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """
    Calculate MACD
    """
    exp1 = close.ewm(span=fast).mean()
    exp2 = close.ewm(span=slow).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def sma_crossover_strategy(row: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Dict[str, Any]]:
    """
    Backtesting-friendly SMA crossover strategy returning an order dict.
    """
    signal = AdvancedStrategies.sma_crossover_strategy(row, positions, cash)
    if not signal:
        return None

    @staticmethod
    def bollinger_bands_strategy(data: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Signal]:
        """
        Bollinger Bands mean reversion strategy
        """
        if pd.isna(data.get('bb_upper')) or pd.isna(data.get('bb_lower')):
            return None

        price = data.get('close', 0)
        upper_band = data.get('bb_upper')
        lower_band = data.get('bb_lower')
        middle_band = data.get('bb_middle', (upper_band + lower_band) / 2)

        symbol = data.get('symbol', 'UNKNOWN')
        current_pos = positions.get(symbol, {})
        current_qty = current_pos.get('quantity', 0)
        quantity = max(int(cash * 0.05 / price), 0) if price > 0 else 0

        if price < lower_band and current_qty <= 0 and quantity > 0:
            return Signal(
                symbol=symbol,
                side='BUY',
                quantity=quantity,
                confidence=0.6,
                strength=0.5,
                rationale='Bollinger mean reversion: price below lower band',
                price_target=middle_band,
                stop_loss=price * 0.97
            )
        if price > upper_band and current_qty > 0:
            return Signal(
                symbol=symbol,
                side='SELL',
                quantity=current_qty,
                confidence=0.6,
                strength=-0.5,
                rationale='Bollinger mean reversion: price above upper band',
                price_target=middle_band,
                stop_loss=price * 1.03
            )

        return None
    if signal.quantity is None or signal.quantity <= 0:
        return None
    return {
        'side': signal.side,
        'quantity': signal.quantity,
        'symbol': signal.symbol,
        'order_type': 'MARKET'
    }


def rsi_mean_reversion_strategy(row: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Dict[str, Any]]:
    """
    Backtesting-friendly RSI mean reversion strategy.
    """
    signal = AdvancedStrategies.rsi_strategy(row, positions, cash)
    if not signal:
        return None
    if signal.quantity is None or signal.quantity <= 0:
        return None
    return {
        'side': signal.side,
        'quantity': signal.quantity,
        'symbol': signal.symbol,
        'order_type': 'MARKET'
    }


def macd_strategy(row: pd.Series, positions: Dict[str, Any], cash: float) -> Optional[Dict[str, Any]]:
    """
    Backtesting-friendly MACD strategy.
    """
    signal = AdvancedStrategies.macd_strategy(row, positions, cash)
    if not signal:
        return None
    if signal.quantity is None or signal.quantity <= 0:
        return None
    return {
        'side': signal.side,
        'quantity': signal.quantity,
        'symbol': signal.symbol,
        'order_type': 'MARKET'
    }
