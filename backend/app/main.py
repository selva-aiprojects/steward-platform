from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Response
import socketio
import asyncio
import random
import os
import logging
import httpx
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Import shared global state
from app.core.state import (
    last_market_movers, 
    last_steward_prediction, 
    last_exchange_status,
    last_macro_indicators,
    clean_ticker_symbol
)

# Import startup services
from app.startup import startup_sequence

# Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Agentic AI-driven stock stewardship platform.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Global CORS headers (handles preflight even if middleware/config fails)
@app.middleware("http")
async def add_cors_headers(request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=204)
    else:
        response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "600"
    return response

# CORS
raw_origins = (settings.CORS_ORIGINS or "").strip()
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO Setup
socket_cors = "*" if "*" in allowed_origins else allowed_origins
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=socket_cors)
socket_app = socketio.ASGIApp(sio, app)

# Global state is now imported from app.core.state to ensure consistency
# last_market_movers and last_steward_prediction are already imported above

# Note: Using TrueData API for live market data - no hardcoded fallback values
# The system will fetch live data from TrueData API and only show actual market prices

@sio.event
async def connect(sid, environ):
    print(f"Socket connected: {sid}")
    await sio.emit('connect_response', {'msg': 'Connected to StockSteward AI Market Feed', 'socket_id': sid}, room=sid)

@sio.event
async def join_stream(sid, data):
    """
    Clients request to join specific role-based streams.
    Data expected: {'role': 'SUPERADMIN' | 'BUSINESS_OWNER' | 'TRADER' | 'AUDITOR', 'userId': ...}
    """
    role = data.get('role', 'TRADER')
    print(f"Socket {sid} requesting stream access for role: {role}")
    
    # 1. End User Stream (Standard Market Data)
    if role in ['TRADER', 'SUPERADMIN', 'BUSINESS_OWNER']:
        await sio.enter_room(sid, 'market_data')
        await sio.emit('stream_status', {'msg': 'Connected to Live Market Feed'}, to=sid)
        
        # Immediate state send
        if last_market_movers['gainers']:
            await sio.emit('market_movers', last_market_movers, to=sid)
        if last_steward_prediction['prediction'] != "Initializing...":
            await sio.emit('steward_prediction', last_steward_prediction, to=sid)

    # 2. Superadmin & Business Owner Stream (System Telemetry)
    if role in ['SUPERADMIN', 'BUSINESS_OWNER']:
        await sio.enter_room(sid, 'admin_telemetry')
        await sio.emit('stream_status', {'msg': 'Connected to Command Center Telemetry'}, to=sid)
        
    # 3. Auditor Stream
    if role == 'AUDITOR':
        await sio.enter_room(sid, 'compliance_log')

@sio.event
async def disconnect(sid):
    print(f"Socket disconnected: {sid}")

# Background Market Publisher (Live & Public)
async def market_feed():
    """
    Background worker that broadcasts market updates.
    Switches between Live yfinance Data and Mock Data based on EXECUTION_MODE.
    """
    # uses shared globals from app.core.state
    from app.core.config import settings
    import os
    import random
    import yfinance as yf
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)

    # Multi-exchange Watchlist (Major indices and top stocks only - excluding commodities/currencies for ticker)
    watchlist = [
        # Top NSE stocks
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'SBIN.NS', 'ITC.NS', 'LT.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
        'BAJFINANCE.NS', 'MARUTI.NS',
        # Major indices
        '^NSEI',  # NIFTY 50 index
        '^BSESN',  # SENSEX index
        # Macro Indicators (added for consistency across cards and tickers)
        'USDINR=X', # USD/INR
        'GC=F',     # Gold Futures
        'CL=F'      # Crude Oil Futures
    ]

    # Store history in memory (simple deque-like structure)
    prediction_history = []
    last_ai_analysis_time = 0
    refresh_interval = 30
    failure_streak = 0
    last_heartbeat_log = 0.0

    async def fetch_quote_batch(symbols: list[str], timeout_s: int = 6) -> dict[str, dict[str, float]]:
        timeout = httpx.Timeout(timeout_s)
        headers = {"User-Agent": "Mozilla/5.0"}
        params = {"symbols": ",".join(symbols)}
        url = "https://query1.finance.yahoo.com/v7/finance/quote"
        quotes: dict[str, dict[str, float]] = {}
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            rows = ((response.json().get("quoteResponse") or {}).get("result")) or []

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
            quotes[symbol] = {"last_price": current_f, "change": change}
        return quotes

    while True:
        try:
            # Cache Groq client
            if not hasattr(market_feed, 'groq_client'):
                groq_key = os.getenv("GROQ_API_KEY")
                if groq_key:
                    try:
                        from groq import Groq
                        market_feed.groq_client = Groq(api_key=groq_key)
                    except Exception:
                        market_feed.groq_client = None
                else:
                    market_feed.groq_client = None
            
            # 0. Sync Heartbeat (throttled)
            import time
            if time.time() - last_heartbeat_log > 60:
                logger.info("Market feed heartbeat: syncing live data")
                last_heartbeat_log = time.time()
            groq_client = market_feed.groq_client

            # 1. Attempt real fetch using Yahoo quote batch API (fast and stable on Render)
            real_data_success = False
            raw_quotes = {}
            
            # Robust type conversion for JSON serialization
            def safe_float(v):
                try:
                    if v is None:
                        return 0.0
                    return float(v)
                except:
                    return 0.0

            try:
                quotes = await fetch_quote_batch(watchlist, timeout_s=6)
                if not quotes:
                    raise RuntimeError("Empty payload from quote batch API")
            except Exception as quote_error:
                logger.debug(f"Quote batch API fallback to yfinance: {quote_error}")
                quotes = {}
                try:
                    import pandas as pd
                    data = await asyncio.wait_for(
                        asyncio.to_thread(
                            yf.download,
                            watchlist,
                            period="5d",
                            group_by='ticker',
                            progress=False,
                            auto_adjust=False,
                            timeout=8,
                            threads=False
                        ),
                        timeout=10
                    )
                    for ticker_symbol in watchlist:
                        try:
                            if isinstance(data.columns, pd.MultiIndex):
                                if ticker_symbol not in data.columns.levels[0]:
                                    continue
                                ticker_df = data[ticker_symbol].dropna(subset=['Close'])
                            else:
                                ticker_df = data.dropna(subset=['Close'])
                            if ticker_df.empty:
                                continue
                            current_price = float(ticker_df['Close'].iloc[-1])
                            prev_price = float(ticker_df['Close'].iloc[-2]) if len(ticker_df) > 1 else current_price
                            change_pct = 0.0 if prev_price == 0 else ((current_price - prev_price) / prev_price * 100)
                            quotes[ticker_symbol] = {"last_price": current_price, "change": change_pct}
                        except Exception:
                            continue
                except Exception as yf_error:
                    raise RuntimeError(f"Both quote-batch and yfinance failed: {yf_error}") from yf_error

            try:
                usd_inr_rate = 83.5
                if "USDINR=X" in quotes:
                    usd_inr_rate = safe_float(quotes["USDINR=X"].get("last_price", usd_inr_rate))

                for ticker_symbol in watchlist:
                    try:
                        quote = quotes.get(ticker_symbol)
                        if not quote:
                            continue

                        current_price = safe_float(quote.get("last_price"))
                        change_pct = safe_float(quote.get("change"))

                        # Localize commodities to INR units for UI consistency.
                        if ticker_symbol == 'GC=F':
                            current_price = (current_price / 31.1035) * usd_inr_rate * 10 * 1.15
                        elif ticker_symbol == 'CL=F':
                            current_price = current_price * usd_inr_rate

                        if '^NSEI' in ticker_symbol or '.NS' in ticker_symbol:
                            exchange = 'NSE'
                        elif '^BSESN' in ticker_symbol or '.BO' in ticker_symbol:
                            exchange = 'BSE'
                        elif ticker_symbol.endswith('=X'):
                            exchange = 'FOREX'
                        elif ticker_symbol.endswith('=F'):
                            exchange = 'MCX'
                        else:
                            exchange = 'NSE'

                        raw_quotes[ticker_symbol] = {
                            'last_price': safe_float(current_price),
                            'change': safe_float(change_pct),
                            'exchange': exchange,
                            'symbol': clean_ticker_symbol(ticker_symbol)
                        }
                    except Exception as ticker_err:
                        logger.debug(f"Error processing {ticker_symbol}: {ticker_err}")
                        continue
                
                if raw_quotes:
                    real_data_success = True
                    failure_streak = 0
                    logger.info(f"Broadcast: Real-time data sync completed for {len(raw_quotes)} instruments")
            except Exception as e:
                failure_streak += 1
                logger.warning(f"Market quote batch fetch failed: {e}")

            if real_data_success:
                # 2. Update Global State (Categories)
                quotes_list = list(raw_quotes.values())
                # Gainers/Losers are filtered to show only Stocks (NSE/BSE)
                gainers_data = sorted([q for q in quotes_list if q['exchange'] in ['NSE', 'BSE']], key=lambda x: x['change'], reverse=True)[:10]
                losers_data = sorted([q for q in quotes_list if q['exchange'] in ['NSE', 'BSE']], key=lambda x: x['change'])[:10]
                
                currencies = [q for q in quotes_list if q['exchange'] == 'FOREX']
                metals = [q for ts, q in raw_quotes.items() if q['exchange'] == 'MCX' and ts in ['GC=F', 'SI=F', 'HG=F']]
                commodities = [q for ts, q in raw_quotes.items() if q['exchange'] == 'MCX' and ts not in ['GC=F', 'SI=F', 'HG=F']]

                # 3. Update Macro Indicators State
                last_macro_indicators.update({
                    "usd_inr": safe_float(usd_inr_rate),
                    "gold": safe_float(raw_quotes.get('GC=F', {}).get('last_price', 0)),
                    "crude": safe_float(raw_quotes.get('CL=F', {}).get('last_price', 0)),
                    "sentiment": "BULLISH" if len(gainers_data) > len(losers_data) else "BEARISH",
                    "volatility_level": "MODERATE"
                })

                # Update global movers - mutate to maintain reference
                last_market_movers.update({
                    'gainers': gainers_data,
                    'losers': losers_data,
                    'currencies': currencies,
                    'metals': metals,
                    'commodities': commodities,
                    'source': 'yahoo_quote_api',
                    'status': 'LIVE',
                    'as_of': _now_iso()
                })
                
                # Emit updates
                await sio.emit('market_movers', last_market_movers, room='market_data')
                await sio.emit('macro_indicators', last_macro_indicators, room='market_data')
            else:
                # Emit only last known real state; do not inject synthetic market values.
                if any(last_market_movers.get(bucket) for bucket in ["gainers", "losers", "currencies", "metals", "commodities"]):
                    last_market_movers["status"] = "STALE"
                    last_market_movers["as_of"] = last_market_movers.get("as_of") or _now_iso()
                    await sio.emit('market_movers', last_market_movers, room='market_data')
                    await sio.emit('macro_indicators', last_macro_indicators, room='market_data')
                    for bucket in ["gainers", "losers", "currencies", "metals", "commodities"]:
                        for item in last_market_movers.get(bucket, []):
                            symbol = item.get("symbol")
                            price = item.get("price", item.get("last_price"))
                            change = item.get("change", 0)
                            exchange = item.get("exchange", "NSE")
                            if not symbol or price is None:
                                continue
                            raw_quotes[symbol] = {
                                "last_price": safe_float(price),
                                "change": safe_float(change),
                                "exchange": exchange,
                                "symbol": symbol
                            }

            # 3. Always update Ticker Batch (from raw_quotes if success, else legacy state)
            ticker_batch = []
            if raw_quotes:
                for ts, q in raw_quotes.items():
                    ticker_batch.append({
                        'symbol': q['symbol'],
                        'exchange': q['exchange'],
                        'price': round(q['last_price'], 2),
                        'change': round(q['change'], 2),
                        'type': 'up' if q['change'] >= 0 else 'down'
                    })
            
            if ticker_batch:
                await sio.emit('ticker_batch', ticker_batch, room='market_data')
                
                # 4. Sample Market Updates (lively UI)
                sample_size = min(5, len(ticker_batch))
                for update in random.sample(ticker_batch, k=sample_size):
                    await sio.emit('market_update', update, room='market_data')

            # 5. Update Macro Indicators from real data if available
            if raw_quotes:
                for ticker in watchlist:
                    if ticker in raw_quotes:
                        val = round(raw_quotes[ticker]['last_price'], 2)
                        if 'USDINR' in ticker: last_macro_indicators['usd_inr'] = val
                        elif 'GC=F' in ticker: last_macro_indicators['gold'] = val
                        elif 'CL=F' in ticker: last_macro_indicators['crude'] = val

            # 6. AI Market Narrative (Throttled)
            import time
            if groq_client and (time.time() - last_ai_analysis_time > 300):
                try:
                    last_ai_analysis_time = time.time()
                    market_summary = ", ".join([f"{q['symbol']}: {q['change']:.2f}%" for q in ticker_batch[:5]])
                    prompt = f"Analyze market in JSON: {market_summary}"
                    completion = await asyncio.to_thread(
                        groq_client.chat.completions.create,
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"},
                        timeout=15
                    )
                    import json
                    analysis = json.loads(completion.choices[0].message.content.strip())
                    last_steward_prediction.update({
                        'prediction': analysis.get('prediction', "Market steady."),
                        'decision': analysis.get('decision', "HOLD"),
                        'confidence': analysis.get('confidence', 80),
                        'signal_mix': analysis.get('signal_mix', {"technical": 70, "fundamental": 90, "news": 50}),
                        'risk_radar': analysis.get('risk_radar', 30),
                        'history': prediction_history
                    })
                    await sio.emit('steward_prediction', last_steward_prediction, room='market_data')
                except:
                    pass

        except Exception as e:
            print(f"Market feed error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if settings.EXECUTION_MODE == "LIVE_TRADING":
                sleep_seconds = refresh_interval
            else:
                sleep_seconds = min(30, 5 + (failure_streak * 5))
            await asyncio.sleep(sleep_seconds)

# Background System Telemetry (Admin Only)
async def admin_feed():
    while True:
        await asyncio.sleep(5) # Slower tick for system stats
        try:
            telemetry = {
                'active_users': random.randint(120, 500),
                'system_load': f"{random.randint(10, 45)}%",
                'latency': f"{random.randint(20, 60)}ms",
                'audit_events': random.randint(0, 5)
            }
            await sio.emit('admin_metrics', telemetry, room='admin_telemetry')
        except Exception as e:
             print(f"Admin feed error: {e}")

@app.on_event("startup")
async def startup_event():
    """
    Application startup event - initialize all services
    """
    try:
        await startup_sequence()
        logging.info("Application startup sequence completed successfully")
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        raise

    # Start background tasks
    if os.getenv("DISABLE_BACKGROUND_TASKS") != "1":
        # Start market feed background task
        asyncio.create_task(market_feed())
        # Start admin telemetry background task
        asyncio.create_task(admin_feed())

@app.get("/")
async def root():
    return {
        "message": "StockSteward AI Backend is fully operational",
        "mode": settings.EXECUTION_MODE,
        "risk_policy": "STRICT"
    }

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "ok", "build": "cors-fix-2699d6f"}
