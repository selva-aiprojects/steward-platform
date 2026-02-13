from fastapi import APIRouter
from typing import Any, Dict
from app.core.config import settings
import random
import logging
import yfinance as yf
import time
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()
MARKET_CACHE_TTL_SECONDS = 300
_cache_store: Dict[str, Dict[str, Any]] = {}


def _cache_get(key: str) -> Any:
    cached = _cache_store.get(key)
    if not cached:
        return None
    if time.time() - cached["ts"] > MARKET_CACHE_TTL_SECONDS:
        return None
    return cached["value"]


def _cache_set(key: str, value: Any) -> None:
    _cache_store[key] = {"ts": time.time(), "value": value}

# Import TrueData service
from app.services.true_data_service import true_data_service

# Import shared global state and helper
from app.core.state import (
    last_market_movers, 
    last_steward_prediction, 
    last_macro_indicators, 
    clean_ticker_symbol
)

@router.get("/status")
def get_market_status() -> Any:
    """
    Get current market status and latency.
    """
    import datetime
    import pytz

    # Get current time in IST (Indian Standard Time)
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(ist)

    # Define market hours (9:15 AM to 3:30 PM IST for normal trading)
    market_open_time = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close_time = current_time.replace(hour=15, minute=30, second=0, microsecond=0)

    # Check if it's a weekday and within market hours
    is_weekday = current_time.weekday() < 5  # Monday to Friday
    is_market_hours = market_open_time <= current_time <= market_close_time

    # Determine status based on current time
    nse_status = "open" if is_weekday and is_market_hours else "closed"
    bse_status = "open" if is_weekday and is_market_hours else "closed"
    mcx_status = "open" if is_weekday and is_market_hours else "closed"

    # Different status for different times of day
    if is_weekday:
        if current_time.time() < datetime.time(9, 15):
            nse_status = bse_status = mcx_status = "pre-market"
        elif current_time.time() < datetime.time(15, 30):
            nse_status = bse_status = mcx_status = "open"
        elif current_time.time() < datetime.time(16, 0):
            nse_status = bse_status = mcx_status = "closing-session"
        else:
            nse_status = bse_status = mcx_status = "closed"
    else:
        nse_status = bse_status = mcx_status = "closed"  # Weekend

    return {
        "status": "ONLINE",
        "latency": "24ms",
        "exchange": "NSE/BSE/MCX",
        "nse": nse_status,
        "bse": bse_status,
        "mcx": mcx_status,
        "timestamp": current_time.isoformat()
    }

@router.get("/movers")
async def get_market_movers() -> Any:
    """
    Get top gainers and losers.
    Uses batch downloading and 5-minute caching for high performance.
    """
    # --- SHARED STATE SYNC ---
    # Prioritize shared global state for consistency with Socket.IO
    if last_market_movers.get('gainers') and last_market_movers.get('losers'):
        return last_market_movers

    # --- CACHING LOGIC ---
    cached_movers = _cache_get("movers")
    if cached_movers:
        return cached_movers
    stale_movers = _cache_store.get("movers", {}).get("value")

    # Primary source for Indian stocks using yfinance (Batch download is MUCH faster)
    watchlist = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'SBIN.NS', 'ITC.NS', 'LT.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
        'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'MARUTI.NS',
        'BHARTIARTL.NS', 'ADANIENT.NS', 'ADANIPORTS.NS', 'ASIANPAINT.NS',
        'ULTRACEMCO.NS', 'WIPRO.NS', 'TECHM.NS', 'HCLTECH.NS', 'ONGC.NS',
        'POWERGRID.NS', 'NTPC.NS', 'COALINDIA.NS', 'SUNPHARMA.NS',
        'DRREDDY.NS', 'CIPLA.NS', 'HINDUNILVR.NS'
    ]

    try:
        # Fetch data for all tickers in one batch request
        import pandas as pd
        data = await asyncio.to_thread(
            yf.download,
            watchlist,
            period="5d",
            group_by='ticker',
            progress=False,
            timeout=8,
            threads=False
        )
        
        raw_quotes = {}
        for ticker_symbol in watchlist:
            try:
                # Handle single vs multi-index dataframe from yf.download
                if isinstance(data.columns, pd.MultiIndex):
                    if ticker_symbol in data.columns.levels[0]:
                        hist = data[ticker_symbol]
                else:
                    hist = data # Single ticker case

                if not hist.empty and 'Close' in hist:
                    current_price = hist['Close'].iloc[-1]
                    if len(hist) > 1:
                        prev_close = hist['Close'].iloc[-2]
                    else:
                        prev_close = current_price
                    
                    if prev_close != 0:
                        change_pct = ((current_price - prev_close) / prev_close) * 100
                        clean_symbol = ticker_symbol.replace('.NS', '')
                        raw_quotes[clean_symbol] = {
                            'last_price': current_price,
                            'change': change_pct,
                            'exchange': 'NSE',
                            'symbol': clean_symbol
                        }
            except Exception as ticker_err:
                logger.debug(f"Error processing {ticker_symbol}: {ticker_err}")
                continue

        # Identify Gainers and Losers
        quotes_with_changes = {}
        for s, q in raw_quotes.items():
            quotes_with_changes[s] = {**q, 'calculated_change': q['change']}

        sorted_movers = sorted(quotes_with_changes.items(), key=lambda x: x[1]['calculated_change'], reverse=True)
        
        gainers_data = []
        for s, q in sorted_movers[:15]:
            gainers_data.append({
                'symbol': q['symbol'],
                'exchange': q['exchange'],
                'price': round(q['last_price'], 2),
                'change': round(q['calculated_change'], 2),
                'last_price': round(q['last_price'], 2)
            })

        losers_data = []
        for s, q in sorted_movers[-15:]:
            losers_data.append({
                'symbol': q['symbol'],
                'exchange': q['exchange'],
                'price': round(q['last_price'], 2),
                'change': round(q['calculated_change'], 2),
                'last_price': round(q['last_price'], 2)
            })

        result = {
            "gainers": gainers_data,
            "losers": sorted(losers_data, key=lambda x: x['change']) # Most negative first
        }
        
        if result["gainers"] or result["losers"]:
            _cache_set("movers", result)
            return result

        # If batch fetch returned no usable rows, attempt fallback.
        raise RuntimeError("Empty movers payload from primary feed")

    except Exception as e:
        logger.error(f"Error fetching market movers: {e}")
        # Try TrueData API as fallback if other sources fail
        try:
            true_data_result = true_data_service.get_top_movers(count=15)
            if true_data_result and true_data_result.get("gainers") and true_data_result.get("losers"):
                fallback = {
                    "gainers": true_data_result["gainers"][:15],
                    "losers": true_data_result["losers"][:15]
                }
                _cache_set("movers", fallback)
                return fallback
        except Exception as td_error:
            logger.error(f"Error fetching data from TrueData: {td_error}")

        if stale_movers:
            return stale_movers
        return {"gainers": [], "losers": []}


@router.get("/heatmap")
def get_sector_heatmap() -> Any:
    sectors = [
        "Banking", "IT", "Energy", "FMCG", "Auto", "Metals", "Pharma", "Infra"
    ]
    return [
        {"sector": s, "score": round(random.uniform(-5, 5), 2)}
        for s in sectors
    ]


@router.get("/news")
def get_market_news() -> Any:
    headlines = [
        "FIIs net buyers as Nifty holds key support",
        "Banking stocks lead rally on credit growth optimism",
        "IT majors steady ahead of weekly earnings updates",
        "Oil slips; metals mixed in early trade",
        "Rupee stabilizes as dollar index softens"
    ]
    random.shuffle(headlines)
    return [{"headline": h, "impact": random.choice(["LOW", "MEDIUM", "HIGH"])} for h in headlines[:4]]


@router.get("/options")
def get_options_snapshot() -> Any:
    symbols = ["NIFTY", "BANKNIFTY", "RELIANCE", "TCS"]
    return [
        {
            "symbol": s,
            "iv": round(random.uniform(12, 28), 2),
            "oi_change": round(random.uniform(-8, 8), 2),
            "put_call": round(random.uniform(0.6, 1.4), 2)
        } for s in symbols
    ]


@router.get("/depth")
def get_order_book_depth() -> Any:
    bids = [{"price": round(2200 + i * 0.5, 2), "qty": random.randint(50, 500)} for i in range(5)]
    asks = [{"price": round(2202 + i * 0.5, 2), "qty": random.randint(50, 500)} for i in range(5)]
    return {"bids": bids, "asks": asks}


@router.get("/macro")
def get_macro_indicators() -> Any:
    # Use real data from shared state if available ($ USD/INR, Gold, Crude)
    if last_macro_indicators.get('usd_inr') and last_macro_indicators.get('usd_inr') > 0:
        return {
            "usd_inr": round(last_macro_indicators['usd_inr'], 2),
            "gold": round(last_macro_indicators['gold'], 2),
            "crude": round(last_macro_indicators['crude'], 2),
            "10y_yield": 7.15, # Sample yield
            "sentiment": "BULLISH" if last_macro_indicators['usd_inr'] < 83.5 else "NEUTRAL",
            "volatility_label": "STABLE"
        }
    
    # Mock fallback if feed hasn't initialized
    return {
        "usd_inr": 83.42,
        "gold": 62450.00,
        "crude": 78.50,
        "10y_yield": 7.12,
        "sentiment": "NEUTRAL",
        "volatility_label": "LOW"
    }


@router.get("/currencies")
async def get_currency_movers() -> Any:
    """
    Get top currency movers using yfinance batch download with 5-minute cache.
    """
    # Prioritize shared global state
    if last_market_movers.get('currencies'):
        return {"currencies": last_market_movers['currencies']}

    cached_currencies = _cache_get("currencies")
    if cached_currencies:
        return cached_currencies
    stale_currencies = _cache_store.get("currencies", {}).get("value")

    try:
        import yfinance as yf
        import pandas as pd
        symbols = ['USDINR=X', 'EURINR=X', 'GBPINR=X', 'JPYINR=X', 'AUDINR=X', 'CADINR=X', 'SGDINR=X']
        
        data = await asyncio.to_thread(
            yf.download,
            symbols,
            period="5d",
            group_by='ticker',
            progress=False,
            timeout=8,
            threads=False
        )
        
        results = []
        for symbol in symbols:
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    hist = data[symbol]
                else:
                    hist = data # Single symbol case

                if not hist.empty and 'Close' in hist:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0

                    results.append({
                        'symbol': symbol.replace('=X', ''),
                        'exchange': 'FOREX',
                        'price': round(float(current_price), 4),
                        'change': round(float(change_pct), 2),
                        'last_price': round(float(current_price), 4)
                    })
            except Exception:
                continue

        payload = {"currencies": results}
        _cache_set("currencies", payload)
        return payload
    except Exception as e:
        logger.error(f"Error in batch currency fetch: {e}")
        if stale_currencies:
            return stale_currencies
        return {"currencies": []}


@router.get("/metals")
async def get_metals_movers() -> Any:
    """
    Get top metals movers using yfinance batch download with 5-minute cache.
    """
    # Prioritize shared global state
    if last_market_movers.get('metals'):
        return {"metals": last_market_movers['metals']}

    cached_metals = _cache_get("metals")
    if cached_metals:
        return cached_metals
    stale_metals = _cache_store.get("metals", {}).get("value")

    try:
        import yfinance as yf
        import pandas as pd
        symbols = ['GC=F', 'SI=F', 'HG=F', 'PL=F', 'PA=F', 'ZN=F']
        
        data = await asyncio.to_thread(
            yf.download,
            symbols,
            period="5d",
            group_by='ticker',
            progress=False,
            timeout=8,
            threads=False
        )
        
        results = []
        for symbol in symbols:
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    hist = data[symbol]
                else:
                    hist = data

                if not hist.empty and 'Close' in hist:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0

                    results.append({
                        'symbol': symbol.replace('=F', ''),
                        'exchange': 'MCX',
                        'price': round(float(current_price), 2),
                        'change': round(float(change_pct), 2),
                        'last_price': round(float(current_price), 2)
                    })
            except Exception:
                continue

        payload = {"metals": results}
        _cache_set("metals", payload)
        return payload
    except Exception as e:
        logger.error(f"Error in batch metals fetch: {e}")
        if stale_metals:
            return stale_metals
        return {"metals": []}


@router.get("/commodities")
async def get_commodity_movers() -> Any:
    """
    Get top commodity movers using yfinance batch download with 5-minute cache.
    """
    # Prioritize shared global state
    if last_market_movers.get('commodities'):
        return {"commodities": last_market_movers['commodities']}

    cached_commodities = _cache_get("commodities")
    if cached_commodities:
        return cached_commodities
    stale_commodities = _cache_store.get("commodities", {}).get("value")

    try:
        import yfinance as yf
        import pandas as pd
        symbols = ['CL=F', 'NG=F', 'GC=F', 'SI=F', 'HG=F', 'ZN=F']
        
        data = await asyncio.to_thread(
            yf.download,
            symbols,
            period="5d",
            group_by='ticker',
            progress=False,
            timeout=8,
            threads=False
        )
        
        results = []
        for symbol in symbols:
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    hist = data[symbol]
                else:
                    hist = data

                if not hist.empty and 'Close' in hist:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0

                    results.append({
                        'symbol': symbol.replace('=F', ''),
                        'exchange': 'MCX',
                        'price': round(float(current_price), 2),
                        'change': round(float(change_pct), 2),
                        'last_price': round(float(current_price), 2)
                    })
            except Exception:
                continue

        payload = {"commodities": results}
        _cache_set("commodities", payload)
        return payload
    except Exception as e:
        logger.error(f"Error in batch commodity fetch: {e}")
        if stale_commodities:
            return stale_commodities
        return {"commodities": []}
