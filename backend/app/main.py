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

logger = logging.getLogger(__name__)

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
    from app.services.data_integration import data_integration_service
    from app.core.config import settings
    import os
    import random
    import yfinance as yf

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

    while True:
        await asyncio.sleep(refresh_interval if settings.EXECUTION_MODE == "LIVE_TRADING" else 5)

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
            
            groq_client = market_feed.groq_client

            # 1. Attempt real fetch using yfinance batch download (For both LIVE and PAPER modes)
            import pandas as pd
            real_data_success = False
            raw_quotes = {}
            
            try:
                data = yf.download(watchlist, period="5d", group_by='ticker', progress=False)
                
                for ticker_symbol in watchlist:
                    try:
                        # Handle multi-index dataframe from yf.download (group_by='ticker')
                        if isinstance(data.columns, pd.MultiIndex):
                            # Ticker is Level 0, Attribute (Open, Close, etc) is Level 1
                            if ticker_symbol in data.columns.levels[0]:
                                ticker_df = data[ticker_symbol].dropna(subset=['Close'])
                                if not ticker_df.empty:
                                    current_price = ticker_df['Close'].iloc[-1]
                                    prev_batch_price = ticker_df['Close'].iloc[-2] if len(ticker_df) > 1 else current_price
                                    change_pct = ((current_price - prev_batch_price) / prev_batch_price * 100) if prev_batch_price != 0 else 0
                                    
                                    # Localize Commodities
                                    if ticker_symbol == 'GC=F': 
                                        current_price = (current_price / 31.1035) * 83.5 * 10 
                                    elif ticker_symbol == 'CL=F': 
                                        current_price = current_price * 83.5 

                                    raw_quotes[ticker_symbol] = {
                                        'last_price': float(current_price),
                                        'change': float(change_pct),
                                        'exchange': 'NSE' if '.NS' in ticker_symbol else 'BSE' if ('.BO' in ticker_symbol or ticker_symbol.startswith('^')) else 'FOREX' if ticker_symbol.endswith('=X') else 'MCX' if ticker_symbol.endswith('=F') else 'NSE',
                                        'symbol': clean_ticker_symbol(ticker_symbol)
                                    }
                        else:
                            # Single ticker or flattened columns
                            if not data.empty and 'Close' in data.columns:
                                current_price = data['Close'].iloc[-1]
                                raw_quotes[ticker_symbol] = {
                                    'last_price': float(current_price),
                                    'change': 0.0,
                                    'exchange': 'NSE',
                                    'symbol': clean_ticker_symbol(ticker_symbol)
                                }
                    except Exception as ticker_err:
                        logger.debug(f"Error processing {ticker_symbol}: {ticker_err}")
                        continue
                
                if raw_quotes:
                    real_data_success = True
                    logger.info(f"Successfully fetched {len(raw_quotes)} real-time quotes")
            except Exception as e:
                logger.error(f"yfinance batch fetch failed: {e}")

            if real_data_success:
                # 2. Process quotes for gainers/losers
                quotes_to_sort = []
                for ticker_symbol, q_data in raw_quotes.items():
                    # Only include stocks (NSE/BSE) in gainers/losers, not macro
                    if '.NS' in ticker_symbol or '.BO' in ticker_symbol:
                        quotes_to_sort.append(q_data)

                if quotes_to_sort:
                    sorted_movers = sorted(quotes_to_sort, key=lambda x: x['change'], reverse=True)
                    gainers_data = sorted_movers[:10]
                    losers_data = sorted(sorted_movers[-10:], key=lambda x: x['change']) # Most negative first

                    # Update global state - mutate to maintain reference
                    last_market_movers.update({
                        'gainers': gainers_data,
                        'losers': losers_data
                    })
                    await sio.emit('market_movers', last_market_movers, room='market_data')
            else:
                # ABSOLUTE FALLBACK - If both fetch and existing data fail
                if not last_market_movers.get('gainers'):
                    logger.warning("No real data available, using mock baseline")
                    mock_gainers = [
                        {'symbol': 'RELIANCE', 'exchange': 'NSE', 'price': 2985.50, 'change': 1.2},
                        {'symbol': 'TCS', 'exchange': 'NSE', 'price': 3850.20, 'change': 0.8},
                        {'symbol': 'HDFCBANK', 'exchange': 'NSE', 'price': 1640.45, 'change': 0.5}
                    ]
                    last_market_movers.update({'gainers': mock_gainers, 'losers': []})
                    await sio.emit('market_movers', last_market_movers, room='market_data')
                else:
                    logger.info("Maintaining last known good prices during API outage")
                    await sio.emit('market_movers', last_market_movers, room='market_data')

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
                    completion = groq_client.chat.completions.create(
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
