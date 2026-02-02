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
        from app.services.kite_service import kite_service
        
        symbol = context.get("symbol")
        exchange = context.get("exchange", "NSE")
        
        # 1. Attempt to fetch real data from Zerodha Kite
        quote = kite_service.get_quote(symbol, exchange)
        
        if quote:
            return {
                "market_data": {
                    "symbol": symbol,
                    "exchange": exchange,
                    "current_price": quote.get("last_price"),
                    "volume": quote.get("volume"),
                    "ohlc": quote.get("ohlc"),
                    "trend": "NEUTRAL", # TODO: Derive from price action
                    "source": "Zerodha KiteConnect"
                }
            }
        
        # 2. Fallback: Simulated/Mock data
        return {
            "market_data": {
                "symbol": symbol,
                "current_price": 150.00,
                "volume": 1000000,
                "trend": "NEUTRAL",
                "source": "MOCK_BACKUP"
            }
        }
