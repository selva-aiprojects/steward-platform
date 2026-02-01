from typing import Dict, Any
from app.strategies.base import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    """
    RSI-based Mean Reversion Strategy.
    Target Regime: SIDEWAYS / RANGING.
    """
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        indicators = market_data.get("indicators", {})
        rsi = indicators.get("rsi_14", 50.0) # Mock default
        
        if rsi < 30:
            return {
                "signal": "BUY",
                "confidence": 0.70,
                "rationale": f"Oversold: RSI ({rsi}) < 30."
            }
        elif rsi > 70:
            return {
                "signal": "SELL",
                "confidence": 0.70,
                "rationale": f"Overbought: RSI ({rsi}) > 70."
            }
            
        return {
            "signal": "HOLD",
            "confidence": 0.50,
            "rationale": f"Neutral RSI ({rsi})."
        }
