from typing import Any, Dict
from app.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

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
        from app.core.state import find_price_by_symbol
        import yfinance as yf
        import asyncio
        
        symbol = context.get("symbol", "RELIANCE").upper()
        # Standardize symbol for lookups
        if not symbol.endswith(".NS") and not symbol.endswith(".BO") and not any(x in symbol for x in ["^", "=X", "=F"]):
            lookup_symbol = f"{symbol}.NS"
        else:
            lookup_symbol = symbol

        exchange = context.get("exchange", "NSE")
        mode = context.get("execution_mode") or settings.EXECUTION_MODE
        
        # 1. Check Global Cache First (Fastest)
        cached_data = find_price_by_symbol(lookup_symbol)
        if cached_data:
            return {
                "market_data": {
                    "symbol": symbol,
                    "exchange": exchange,
                    "current_price": cached_data.get("price"),
                    "change_pct": cached_data.get("change"),
                    "source": "StockSteward Global State (Live)"
                }
            }

        # 2. Attempt real fetch from Kite in LIVE mode
        if mode == "LIVE_TRADING" and settings.ZERODHA_ACCESS_TOKEN:
            try:
                quote = kite_service.get_quote(symbol, exchange)
                if quote and quote.get("last_price"):
                    return {
                        "market_data": {
                            "symbol": symbol,
                            "exchange": exchange,
                            "current_price": quote.get("last_price"),
                            "volume": quote.get("volume"),
                            "change_pct": (quote.get("last_price") - quote.get("ohlc", {}).get("close", 0)) / quote.get("ohlc", {}).get("close", 1) * 100 if quote.get("ohlc") else 0,
                            "source": "Zerodha KiteConnect Live"
                        }
                    }
            except Exception as e:
                logger.warning(f"Kite quote failed for {symbol}: {e}")

        # 3. Last Resort: Live fetch via yfinance
        try:
            ticker = yf.Ticker(lookup_symbol)
            # Use fast_info for minimal latency
            info = ticker.fast_info
            current_price = info.get("last_price") or info.get("lastPrice")
            
            if current_price:
                return {
                    "market_data": {
                        "symbol": symbol,
                        "current_price": float(current_price),
                        "change_pct": float(info.get("day_change_percent", 0)),
                        "source": "yfinance Real-time Fallback"
                    }
                }
        except Exception as e:
            logger.error(f"MarketDataAgent live fallback failed: {e}")

        # 4. Final Absolute Fallback - ONLY if all real sources fail
        return {
            "market_data": {
                "symbol": symbol,
                "current_price": 0.0,
                "trend": "DATA_UNAVAILABLE",
                "source": "SYSTEM_ERROR_FALLBACK"
            }
        }
