from typing import Any, Dict
from app.agents.base import BaseAgent

class StrategyAgent(BaseAgent):
    """
    Responsible for pure Technical/Fundamental Analysis logic.
    
    Responsibilities:
    - Analyze market data.
    - Apply trading strategies (e.g., MACD crossover, RSI).
    - output raw signals (BUY_SIGNAL, SELL_SIGNAL, HOLD).
    - DOES NOT DECIDE to trade (that's TradeDecisionAgent).
    """
    
    def __init__(self):
        super().__init__(name="StrategyAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from app.strategies.sma_crossover import SMACrossoverStrategy
        from app.strategies.mean_reversion import MeanReversionStrategy

        market_data = context.get("market_data", {})
        trend = market_data.get("trend", "NEUTRAL") # Provided by MarketDataAgent
        
        # Strategy Selection Logic (Regime Switching)
        if trend in ["BULLISH", "BEARISH"]:
            active_strategy = SMACrossoverStrategy()
            strategy_name = "SMACrossover"
        else:
            active_strategy = MeanReversionStrategy()
            strategy_name = "MeanReversion"
            
        # Execute Analysis
        analysis_result = active_strategy.analyze(market_data)
        
        return {
            "strategy_signal": {
                "strategy_used": strategy_name,
                "signal": analysis_result["signal"],
                "confidence": analysis_result["confidence"],
                "rationale": analysis_result["rationale"],
                "regime_detected": trend
            }
        }
