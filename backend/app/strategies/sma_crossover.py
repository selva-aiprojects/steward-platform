from typing import Dict, Any
from app.strategies.base import BaseStrategy

class SMACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy.
    Target Regime: TRENDING (BULL or BEAR).
    """
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        current_price = market_data.get("current_price", 0.0)
        # In a real impl, we'd need historical data to calc MA.
        # Here we assume pre-calculated indicators from MarketDataAgent or we simulate it.
        indicators = market_data.get("indicators", {})
        sma_short = indicators.get("sma_50", current_price * 0.95) # Mock: Default to bullish pattern
        sma_long = indicators.get("sma_200", current_price * 0.90) 
        
        # Logic: Golden Cross
        if sma_short > sma_long and current_price > sma_short:
             return {
                "signal": "BUY",
                "confidence": 0.85,
                "rationale": f"Bullish Golden Cross: SMA50 ({sma_short}) > SMA200 ({sma_long}) and Price > SMA50."
            }
        
        # Logic: Death Cross
        elif sma_short < sma_long and current_price < sma_short:
             return {
                "signal": "SELL",
                "confidence": 0.80,
                "rationale": f"Bearish Death Cross: SMA50 ({sma_short}) < SMA200 ({sma_long})."
            }
            
        return {
            "signal": "HOLD",
            "confidence": 0.50,
            "rationale": "No clear trend signal."
        }
