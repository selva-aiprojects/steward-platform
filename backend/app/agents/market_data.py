from typing import Any, Dict
from app.agents.base import BaseAgent
import logging
import asyncio
import httpx

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
                quote = await asyncio.wait_for(
                    asyncio.to_thread(kite_service.get_quote, symbol, exchange),
                    timeout=2.5
                )
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

        # 3. Fast HTTP fallback against Yahoo chart endpoint
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(2.0), headers={"User-Agent": "Mozilla/5.0"}) as client:
                response = await client.get(
                    f"https://query1.finance.yahoo.com/v8/finance/chart/{lookup_symbol}",
                    params={"range": "5d", "interval": "1d"}
                )
                response.raise_for_status()
                payload = response.json() or {}
                result = ((payload.get("chart") or {}).get("result") or [None])[0]
                if result:
                    closes = ((((result.get("indicators") or {}).get("quote") or [{}])[0]).get("close") or [])
                    valid = []
                    for value in closes:
                        try:
                            if value is not None:
                                valid.append(float(value))
                        except Exception:
                            continue
                    if valid:
                        current_price = valid[-1]
                        previous_close = valid[-2] if len(valid) > 1 else current_price
                        change_pct = 0.0 if previous_close == 0 else ((current_price - previous_close) / previous_close) * 100
                        return {
                            "market_data": {
                                "symbol": symbol,
                                "current_price": round(current_price, 4),
                                "change_pct": round(change_pct, 4),
                                "source": "Yahoo Chart API Fallback"
                            }
                        }
        except Exception as e:
            logger.warning(f"Yahoo chart fallback failed for {symbol}: {e}")

        # 4. Last resort: yfinance with hard timeout
        try:
            info = await asyncio.wait_for(
                asyncio.to_thread(lambda: yf.Ticker(lookup_symbol).fast_info),
                timeout=2.5
            )
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

        # 5. Final absolute fallback
        return {
            "market_data": {
                "symbol": symbol,
                "current_price": 0.0,
                "trend": "DATA_UNAVAILABLE",
                "source": "SYSTEM_ERROR_FALLBACK"
            }
        }
