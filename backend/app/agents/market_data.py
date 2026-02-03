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
        from app.core.config import settings
        
        symbol = context.get("symbol")
        exchange = context.get("exchange", "NSE")
        mode = context.get("execution_mode") or settings.EXECUTION_MODE
        
        # 1. Attempt to fetch real data from Zerodha Kite (NSE) only in LIVE_TRADING
        quote = None
        if mode == "LIVE_TRADING":
            quote = kite_service.get_quote(symbol, exchange)
        
        if quote:
            return {
                "market_data": {
                    "symbol": symbol,
                    "exchange": exchange,
                    "current_price": quote.get("last_price"),
                    "volume": quote.get("volume"),
                    "change_pct": (quote.get("last_price") - quote.get("ohlc", {}).get("close", 0)) / quote.get("ohlc", {}).get("close", 1) * 100 if quote.get("ohlc") else 0,
                    "ohlc": quote.get("ohlc"),
                    "trend": "BULLISH" if quote.get("last_price") > quote.get("ohlc", {}).get("open", 0) else "BEARISH" if quote.get("ohlc") else "NEUTRAL",
                    "source": "Zerodha KiteConnect Live"
                }
            }
        
        # 2. Fallback: Simulated/Mock data
        return {
            "market_data": {
                "symbol": symbol,
                "current_price": 2450.00,
                "volume": 1000000,
                "trend": "NEUTRAL",
                "source": "MOCK_BACKUP"
            }
        }
