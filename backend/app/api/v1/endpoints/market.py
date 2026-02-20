from fastapi import APIRouter
from typing import Any, Dict, Optional
from app.core.config import settings
import random
import logging
import yfinance as yf
import time
import asyncio
from datetime import datetime, timezone
import httpx
from app.observability.metrics import record_external_call

logger = logging.getLogger(__name__)

router = APIRouter()
MARKET_CACHE_TTL_SECONDS = 300
_cache_store: Dict[str, Dict[str, Any]] = {}
_provider_stats: Dict[str, Dict[str, Any]] = {}
_yf_failure_streak = 0
_yf_cooldown_until = 0.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record_provider_result(provider: str, success: bool, latency_ms: Optional[float] = None, error: str = "") -> None:
    stats = _provider_stats.get(provider, {
        "calls": 0,
        "failures": 0,
        "last_success_at": None,
        "last_error_at": None,
        "last_error": "",
        "last_latency_ms": None,
        "avg_latency_ms": None,
    })
    stats["calls"] += 1
    if not success:
        stats["failures"] += 1
        stats["last_error_at"] = _now_iso()
        stats["last_error"] = error
    else:
        stats["last_success_at"] = _now_iso()

    if latency_ms is not None:
        latency_ms = round(float(latency_ms), 2)
        stats["last_latency_ms"] = latency_ms
        if stats["avg_latency_ms"] is None:
            stats["avg_latency_ms"] = latency_ms
        else:
            stats["avg_latency_ms"] = round((stats["avg_latency_ms"] * 0.7) + (latency_ms * 0.3), 2)

    calls = max(stats["calls"], 1)
    stats["error_rate"] = round(stats["failures"] / calls, 4)
    _provider_stats[provider] = stats
    record_external_call(
        provider=provider,
        operation="market_data_fetch",
        latency_seconds=(latency_ms / 1000.0) if latency_ms is not None else None,
        success=success,
    )


def _with_market_meta(payload: Dict[str, Any], source: str, status: str, as_of: Optional[str] = None) -> Dict[str, Any]:
    data = dict(payload)
    data["source"] = source
    data["status"] = status
    data["as_of"] = as_of or _now_iso()
    return data


def _last_two_valid(values: list[Any]) -> tuple[Optional[float], Optional[float]]:
    valid: list[float] = []
    for v in values or []:
        if v is None:
            continue
        try:
            valid.append(float(v))
        except Exception:
            continue
    if not valid:
        return None, None
    if len(valid) == 1:
        return valid[0], valid[0]
    return valid[-1], valid[-2]


async def _fetch_chart_quote(client: httpx.AsyncClient, symbol: str) -> Optional[Dict[str, Any]]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "5d", "interval": "1d"}
    r = await client.get(url, params=params)
    r.raise_for_status()
    payload = r.json() or {}
    result = ((payload.get("chart") or {}).get("result") or [None])[0]
    if not result:
        return None
    closes = ((((result.get("indicators") or {}).get("quote") or [{}])[0]).get("close") or [])
    current, previous = _last_two_valid(closes)
    if current is None:
        return None
    previous = previous or current
    change = 0.0 if previous == 0 else ((current - previous) / previous) * 100
    return {"last_price": current, "change": change}


async def _chart_quotes(symbols: list[str], timeout_s: int = 4) -> Dict[str, Dict[str, Any]]:
    quotes: Dict[str, Dict[str, Any]] = {}
    timeout = httpx.Timeout(timeout_s)
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        tasks = [_fetch_chart_quote(client, s) for s in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    for symbol, result in zip(symbols, results):
        if isinstance(result, Exception) or not result:
            continue
        quotes[symbol] = result
    return quotes


async def _quote_batch(symbols: list[str], timeout_s: int = 2) -> Dict[str, Dict[str, Any]]:
    timeout = httpx.Timeout(timeout_s)
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"symbols": ",".join(symbols)}
    out: Dict[str, Dict[str, Any]] = {}
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        r = await client.get("https://query1.finance.yahoo.com/v7/finance/quote", params=params)
        r.raise_for_status()
        payload = r.json() or {}
    rows = (((payload.get("quoteResponse") or {}).get("result")) or [])
    for row in rows:
        symbol = row.get("symbol")
        if not symbol:
            continue
        current = row.get("regularMarketPrice")
        prev = row.get("regularMarketPreviousClose")
        try:
            current_f = float(current)
            prev_f = float(prev) if prev is not None else current_f
        except Exception:
            continue
        change = 0.0 if prev_f == 0 else ((current_f - prev_f) / prev_f) * 100
        out[symbol] = {"last_price": current_f, "change": change}
    return out


def _chart_quotes_sync(symbols: list[str], timeout_s: int = 3) -> Dict[str, Dict[str, Any]]:
    quotes: Dict[str, Dict[str, Any]] = {}
    timeout = httpx.Timeout(timeout_s)
    headers = {"User-Agent": "Mozilla/5.0"}
    with httpx.Client(timeout=timeout, headers=headers) as client:
        for symbol in symbols:
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                params = {"range": "5d", "interval": "1d"}
                r = client.get(url, params=params)
                r.raise_for_status()
                payload = r.json() or {}
                result = ((payload.get("chart") or {}).get("result") or [None])[0]
                if not result:
                    continue
                closes = ((((result.get("indicators") or {}).get("quote") or [{}])[0]).get("close") or [])
                current, previous = _last_two_valid(closes)
                if current is None:
                    continue
                previous = previous or current
                change = 0.0 if previous == 0 else ((current - previous) / previous) * 100
                quotes[symbol] = {"last_price": current, "change": change}
            except Exception:
                continue
    return quotes


async def _yf_download(symbols: list[str], period: str = "5d", timeout_s: int = 2):
    global _yf_failure_streak, _yf_cooldown_until
    now = time.time()
    if now < _yf_cooldown_until:
        raise RuntimeError("Yahoo Finance fetch on cooldown after repeated failures")
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)
    # yfinance can occasionally block far beyond its own timeout argument.
    try:
        data = await asyncio.wait_for(
            asyncio.to_thread(
                yf.download,
                symbols,
                period=period,
                group_by='ticker',
                progress=False,
                auto_adjust=False,
                timeout=timeout_s,
                threads=False
            ),
            timeout=timeout_s + 1
        )
        _yf_failure_streak = 0
        _yf_cooldown_until = 0.0
        return data
    except Exception:
        _yf_failure_streak += 1
        cooldown_seconds = min(30, 2 ** min(_yf_failure_streak, 5))
        _yf_cooldown_until = time.time() + cooldown_seconds
        raise


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
        return _with_market_meta(
            last_market_movers,
            last_market_movers.get("source", "socket_feed"),
            last_market_movers.get("status", "LIVE"),
            last_market_movers.get("as_of")
        )

    # --- CACHING LOGIC ---
    cached_movers = _cache_get("movers")
    if cached_movers:
        return cached_movers
    stale_movers = _cache_store.get("movers", {}).get("value")

    # Primary source for Indian stocks using Yahoo chart API (more reliable on Render).
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
        started = time.time()
        chart_quotes = await _quote_batch(watchlist, timeout_s=2)
        raw_quotes: Dict[str, Dict[str, Any]] = {}
        for ticker_symbol, quote in chart_quotes.items():
            clean_symbol = ticker_symbol.replace('.NS', '')
            raw_quotes[clean_symbol] = {
                'last_price': quote['last_price'],
                'change': quote['change'],
                'exchange': 'NSE',
                'symbol': clean_symbol
            }

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

        result = _with_market_meta({
            "gainers": gainers_data,
            "losers": sorted(losers_data, key=lambda x: x['change']) # Most negative first
        }, source="yahoo_finance", status="LIVE")
        
        if result["gainers"] or result["losers"]:
            _record_provider_result("yahoo_chart_api", True, (time.time() - started) * 1000)
            _cache_set("movers", result)
            return result

        # If primary fetch returned no usable rows, attempt yfinance fallback.
        _record_provider_result("yahoo_chart_api", False, (time.time() - started) * 1000, "Empty movers payload")
        raise RuntimeError("Empty movers payload from chart API")

    except Exception as e:
        logger.error(f"Error fetching market movers from chart API: {e}")
        _record_provider_result("yahoo_chart_api", False, error=str(e))
        # Fail fast with stale cache if available instead of waiting through slower providers.
        if stale_movers:
            return _with_market_meta(stale_movers, stale_movers.get("source", "cache"), "STALE", stale_movers.get("as_of"))
        # yfinance fallback
        try:
            yf_started = time.time()
            import pandas as pd
            data = await _yf_download(watchlist, period="5d", timeout_s=2)
            raw_quotes = {}
            for ticker_symbol in watchlist:
                if isinstance(data.columns, pd.MultiIndex):
                    if ticker_symbol not in data.columns.levels[0]:
                        continue
                    hist = data[ticker_symbol]
                else:
                    hist = data
                if hist.empty or 'Close' not in hist:
                    continue
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                if prev_close == 0:
                    continue
                change_pct = ((current_price - prev_close) / prev_close) * 100
                clean_symbol = ticker_symbol.replace('.NS', '')
                raw_quotes[clean_symbol] = {
                    'last_price': current_price,
                    'change': change_pct,
                    'exchange': 'NSE',
                    'symbol': clean_symbol
                }
            sorted_movers = sorted(raw_quotes.items(), key=lambda x: x[1]['change'], reverse=True)
            gainers = [{'symbol': q['symbol'], 'exchange': q['exchange'], 'price': round(q['last_price'], 2), 'change': round(q['change'], 2), 'last_price': round(q['last_price'], 2)} for _, q in sorted_movers[:15]]
            losers = [{'symbol': q['symbol'], 'exchange': q['exchange'], 'price': round(q['last_price'], 2), 'change': round(q['change'], 2), 'last_price': round(q['last_price'], 2)} for _, q in sorted_movers[-15:]]
            fallback = _with_market_meta({"gainers": gainers, "losers": sorted(losers, key=lambda x: x['change'])}, source="yahoo_finance", status="LIVE")
            if fallback["gainers"] or fallback["losers"]:
                _record_provider_result("yahoo_finance", True, (time.time() - yf_started) * 1000)
                _cache_set("movers", fallback)
                return fallback
            _record_provider_result("yahoo_finance", False, (time.time() - yf_started) * 1000, "Empty movers payload")
        except Exception as yf_error:
            _record_provider_result("yahoo_finance", False, error=str(yf_error))

        # Try TrueData API as fallback if other sources fail
        if settings.TRUEDATA_API_KEY:
            try:
                td_started = time.time()
                true_data_result = await asyncio.wait_for(
                    asyncio.to_thread(true_data_service.get_top_movers, 15),
                    timeout=3
                )
                if true_data_result and true_data_result.get("gainers") and true_data_result.get("losers"):
                    fallback = _with_market_meta({
                        "gainers": true_data_result["gainers"][:15],
                        "losers": true_data_result["losers"][:15]
                    }, source="truedata", status="LIVE")
                    _record_provider_result("truedata", True, (time.time() - td_started) * 1000)
                    _cache_set("movers", fallback)
                    return fallback
            except Exception as td_error:
                logger.error(f"Error fetching data from TrueData: {td_error}")
                _record_provider_result("truedata", False, error=str(td_error))

        if stale_movers:
            return _with_market_meta(stale_movers, stale_movers.get("source", "cache"), "STALE", stale_movers.get("as_of"))
        return _with_market_meta({"gainers": [], "losers": []}, source="none", status="UNAVAILABLE")


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
    # Build depth from live movers so numbers are anchored to current market prices.
    gainers = last_market_movers.get("gainers") or []
    losers = last_market_movers.get("losers") or []
    universe = gainers + losers

    if universe:
        anchor = universe[0]
        symbol = anchor.get("symbol", "NIFTY")
        ltp = float(anchor.get("price") or anchor.get("last_price") or 0)
    else:
        symbol = "NIFTY"
        ltp = 0

    if ltp <= 0:
        return {
            "symbol": symbol,
            "source": "none",
            "status": "UNAVAILABLE",
            "bids": [],
            "asks": [],
        }

    spread = max(0.05, round(ltp * 0.0006, 2))
    tick = max(0.05, round(ltp * 0.0003, 2))
    bids = []
    asks = []

    for level in range(5):
        bid_price = round(ltp - spread - (level * tick), 2)
        ask_price = round(ltp + spread + (level * tick), 2)
        base_qty = max(20, int((1000 / max(1.0, ltp)) * 100))
        qty_bias = (5 - level) * 7
        bids.append({"price": bid_price, "qty": base_qty + qty_bias})
        asks.append({"price": ask_price, "qty": base_qty + max(3, level * 5)})

    return {
        "symbol": symbol,
        "ltp": round(ltp, 2),
        "source": last_market_movers.get("source", "socket_feed"),
        "status": last_market_movers.get("status", "LIVE"),
        "as_of": last_market_movers.get("as_of"),
        "bids": bids,
        "asks": asks,
    }


@router.get("/macro")
def get_macro_indicators() -> Any:
    # Use real data from shared state if available ($ USD/INR, Gold, Crude)
    if last_macro_indicators.get('usd_inr') and last_macro_indicators.get('usd_inr') > 0:
        return _with_market_meta({
            "usd_inr": round(last_macro_indicators['usd_inr'], 2),
            "gold": round(last_macro_indicators['gold'], 2),
            "crude": round(last_macro_indicators['crude'], 2),
            "10y_yield": 7.15, # Sample yield
            "sentiment": "BULLISH" if last_macro_indicators['usd_inr'] < 83.5 else "NEUTRAL",
            "volatility_label": "STABLE"
        }, source="socket_feed", status="LIVE")

    # API fallback for macro cards so pilot users don't see blank tiles.
    try:
        macro_symbols = ['USDINR=X', 'GC=F', 'CL=F']
        started = time.time()
        quotes = _chart_quotes_sync(macro_symbols, timeout_s=3)
        if quotes:
            payload = _with_market_meta({
                "usd_inr": round((quotes.get('USDINR=X') or {}).get('last_price', 0), 2) or None,
                "gold": round((quotes.get('GC=F') or {}).get('last_price', 0), 2) or None,
                "crude": round((quotes.get('CL=F') or {}).get('last_price', 0), 2) or None,
                "10y_yield": None,
                "sentiment": "NEUTRAL",
                "volatility_label": "LIVE"
            }, source="yahoo_chart_api", status="LIVE")
            _record_provider_result("yahoo_chart_api_macro", True, (time.time() - started) * 1000)
            return payload
        _record_provider_result("yahoo_chart_api_macro", False, (time.time() - started) * 1000, "Empty macro payload")
    except Exception as e:
        _record_provider_result("yahoo_chart_api_macro", False, error=str(e))

    # No mock fallback: return explicit unavailable state until real data arrives.
    return _with_market_meta({
        "usd_inr": None,
        "gold": None,
        "crude": None,
        "10y_yield": None,
        "sentiment": "UNAVAILABLE",
        "volatility_label": "UNAVAILABLE"
    }, source="none", status="UNAVAILABLE")


@router.get("/currencies")
async def get_currency_movers() -> Any:
    """
    Get top currency movers using yfinance batch download with 5-minute cache.
    """
    # Prioritize shared global state
    if last_market_movers.get('currencies'):
        return _with_market_meta({
            "currencies": last_market_movers['currencies']
        }, source=last_market_movers.get("source", "socket_feed"), status=last_market_movers.get("status", "LIVE"), as_of=last_market_movers.get("as_of"))

    cached_currencies = _cache_get("currencies")
    if cached_currencies:
        return cached_currencies
    stale_currencies = _cache_store.get("currencies", {}).get("value")

    try:
        started = time.time()
        import yfinance as yf
        import pandas as pd
        symbols = ['USDINR=X', 'EURINR=X', 'GBPINR=X', 'JPYINR=X', 'AUDINR=X', 'CADINR=X', 'SGDINR=X']
        
        data = await _yf_download(symbols, period="5d", timeout_s=4)
        
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

        payload = _with_market_meta({"currencies": results}, source="yahoo_finance", status="LIVE")
        _record_provider_result("yahoo_finance_fx", True, (time.time() - started) * 1000)
        _cache_set("currencies", payload)
        return payload
    except Exception as e:
        logger.error(f"Error in batch currency fetch: {e}")
        _record_provider_result("yahoo_finance_fx", False, error=str(e))
        if stale_currencies:
            return _with_market_meta(stale_currencies, stale_currencies.get("source", "cache"), "STALE", stale_currencies.get("as_of"))
        return _with_market_meta({"currencies": []}, source="none", status="UNAVAILABLE")


@router.get("/metals")
async def get_metals_movers() -> Any:
    """
    Get top metals movers using yfinance batch download with 5-minute cache.
    """
    # Prioritize shared global state
    if last_market_movers.get('metals'):
        return _with_market_meta({
            "metals": last_market_movers['metals']
        }, source=last_market_movers.get("source", "socket_feed"), status=last_market_movers.get("status", "LIVE"), as_of=last_market_movers.get("as_of"))

    cached_metals = _cache_get("metals")
    if cached_metals:
        return cached_metals
    stale_metals = _cache_store.get("metals", {}).get("value")

    try:
        started = time.time()
        import yfinance as yf
        import pandas as pd
        symbols = ['GC=F', 'SI=F', 'HG=F', 'PL=F', 'PA=F', 'ZN=F']
        
        data = await _yf_download(symbols, period="5d", timeout_s=4)
        
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

        payload = _with_market_meta({"metals": results}, source="yahoo_finance", status="LIVE")
        _record_provider_result("yahoo_finance_metals", True, (time.time() - started) * 1000)
        _cache_set("metals", payload)
        return payload
    except Exception as e:
        logger.error(f"Error in batch metals fetch: {e}")
        _record_provider_result("yahoo_finance_metals", False, error=str(e))
        if stale_metals:
            return _with_market_meta(stale_metals, stale_metals.get("source", "cache"), "STALE", stale_metals.get("as_of"))
        return _with_market_meta({"metals": []}, source="none", status="UNAVAILABLE")


@router.get("/commodities")
async def get_commodity_movers() -> Any:
    """
    Get top commodity movers using yfinance batch download with 5-minute cache.
    """
    # Prioritize shared global state
    if last_market_movers.get('commodities'):
        return _with_market_meta({
            "commodities": last_market_movers['commodities']
        }, source=last_market_movers.get("source", "socket_feed"), status=last_market_movers.get("status", "LIVE"), as_of=last_market_movers.get("as_of"))

    cached_commodities = _cache_get("commodities")
    if cached_commodities:
        return cached_commodities
    stale_commodities = _cache_store.get("commodities", {}).get("value")

    try:
        started = time.time()
        import yfinance as yf
        import pandas as pd
        symbols = ['CL=F', 'NG=F', 'GC=F', 'SI=F', 'HG=F', 'ZN=F']
        
        data = await _yf_download(symbols, period="5d", timeout_s=4)
        
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

        payload = _with_market_meta({"commodities": results}, source="yahoo_finance", status="LIVE")
        _record_provider_result("yahoo_finance_commodities", True, (time.time() - started) * 1000)
        _cache_set("commodities", payload)
        return payload
    except Exception as e:
        logger.error(f"Error in batch commodity fetch: {e}")
        _record_provider_result("yahoo_finance_commodities", False, error=str(e))
        if stale_commodities:
            return _with_market_meta(stale_commodities, stale_commodities.get("source", "cache"), "STALE", stale_commodities.get("as_of"))
        return _with_market_meta({"commodities": []}, source="none", status="UNAVAILABLE")


@router.get("/health")
def get_market_data_health() -> Any:
    now = _now_iso()
    cache_age_seconds = {}
    for key, entry in _cache_store.items():
        cache_age_seconds[key] = round(max(0.0, time.time() - entry.get("ts", time.time())), 2)

    return {
        "status": "ok",
        "as_of": now,
        "cache_ttl_seconds": MARKET_CACHE_TTL_SECONDS,
        "cache_age_seconds": cache_age_seconds,
        "providers": _provider_stats,
    }
