from typing import Any, Dict
from app.agents.base import BaseAgent

class MarketDataAgent(BaseAgent):
    """
    Responsible for fetching Real-Time and Historical Market Data.
    
    Responsibilities:
    - Fetch current price for a symbol.
    - Fetch volume, moving averages, etc.
    - Normalize data for Strategy consumption.
    """
    
    def __init__(self):
        super().__init__(name="MarketDataAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        symbol = context.get("symbol")
        
        # Placeholder: Mock data
        # In real impl, would call Yahoo Finance / AlphaVantage / Bloomberg
        return {
            "market_data": {
                "symbol": symbol,
                "current_price": 150.00,
                "volume": 1000000,
                "trend": "NEUTRAL"
            }
        }
