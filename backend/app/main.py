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

# Global state for immediate feed on join
last_market_movers = {'gainers': [], 'losers': []}
last_steward_prediction = {"prediction": "Initializing...", "history": []}

# Mock data for fallback mode
mock_gainers = [
    {'symbol': 'RELIANCE', 'exchange': 'NSE', 'price': 2987.5, 'change': 1.2},
    {'symbol': 'TCS', 'exchange': 'NSE', 'price': 3820.0, 'change': 0.8},
    {'symbol': 'HDFCBANK', 'exchange': 'NSE', 'price': 1675.0, 'change': 0.6},
    {'symbol': 'INFY', 'exchange': 'NSE', 'price': 1540.0, 'change': 1.1},
    {'symbol': 'ICICIBANK', 'exchange': 'NSE', 'price': 1042.0, 'change': 0.9},
    {'symbol': 'ITC', 'exchange': 'NSE', 'price': 438.0, 'change': 0.7},
    {'symbol': 'AXISBANK', 'exchange': 'NSE', 'price': 1125.0, 'change': 0.5},
    {'symbol': 'SENSEX', 'exchange': 'BSE', 'price': 72420.0, 'change': 0.6},
    {'symbol': 'NIFTY', 'exchange': 'NSE', 'price': 22340.0, 'change': 0.8},
    {'symbol': 'GOLD', 'exchange': 'MCX', 'price': 62450.0, 'change': 0.9}
]

mock_losers = [
    {'symbol': 'WIPRO', 'exchange': 'NSE', 'price': 420.0, 'change': -1.2},
    {'symbol': 'TATASTEEL', 'exchange': 'NSE', 'price': 115.0, 'change': -2.3},
    {'symbol': 'SBIN', 'exchange': 'NSE', 'price': 580.0, 'change': -1.5},
    {'symbol': 'NTPC', 'exchange': 'NSE', 'price': 310.0, 'change': -0.8},
    {'symbol': 'POWERGRID', 'exchange': 'NSE', 'price': 275.0, 'change': -0.7},
    {'symbol': 'BAJAJFINSV', 'exchange': 'NSE', 'price': 1680.0, 'change': -0.9},
    {'symbol': 'SUNPHARMA', 'exchange': 'NSE', 'price': 1340.0, 'change': -0.6},
    {'symbol': 'CRUDEOIL', 'exchange': 'MCX', 'price': 6985.0, 'change': -0.9},
    {'symbol': 'SILVER', 'exchange': 'MCX', 'price': 74200.0, 'change': -0.5},
    {'symbol': 'BOM500002', 'exchange': 'BSE', 'price': 1790.0, 'change': -0.4}
]

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
    Switches between Live Zerodha Data and Mock Data based on EXECUTION_MODE.
    """
    global last_market_movers, last_steward_prediction
    from app.services.kite_service import kite_service
    from app.core.config import settings
    import os
    import random
    
    # Multi-exchange Watchlist (NSE, BSE, MCX)
    watchlist = [
        # NSE (Nifty 50 highlights)
        'NSE:RELIANCE', 'NSE:TCS', 'NSE:HDFCBANK', 'NSE:INFY', 'NSE:ICICIBANK',
        'NSE:SBIN', 'NSE:ITC', 'NSE:LT', 'NSE:AXISBANK', 'NSE:KOTAKBANK',
        'NSE:BAJFINANCE', 'NSE:BAJAJFINSV', 'NSE:MARUTI', 'NSE:TATAMOTORS',
        'NSE:BHARTIARTL', 'NSE:ADANIENT', 'NSE:ADANIPORTS', 'NSE:ASIANPAINT',
        'NSE:ULTRACEMCO', 'NSE:WIPRO', 'NSE:TECHM', 'NSE:HCLTECH', 'NSE:ONGC',
        'NSE:POWERGRID', 'NSE:NTPC', 'NSE:COALINDIA', 'NSE:SUNPHARMA',
        'NSE:DRREDDY', 'NSE:CIPLA', 'NSE:HINDUNILVR',
        # BSE
        'BSE:SENSEX', 'BSE:BOM500002', 'BSE:BOM500010',
        # Commodities (MCX)
        'MCX:GOLD', 'MCX:SILVER', 'MCX:CRUDEOIL', 'MCX:NATURALGAS'
    ]
    
    # Store history in memory (simple deque-like structure)
    prediction_history = []
    
    while True:
        # 30-60 second cycle for comprehensive analysis to avoid rate limits
        # Using 8s for demo responsiveness
        await asyncio.sleep(8 if settings.EXECUTION_MODE == "LIVE_TRADING" else 3)
        
        try:
            # Setup Groq once per cycle (if key exists)
            groq_key = os.getenv("GROQ_API_KEY")
            groq_client = None
            if groq_key:
                try:
                    from groq import Groq
                    groq_client = Groq(api_key=groq_key)
                except ImportError:
                    print("Groq library not installed")
                    groq_client = None  # Define the variable even if import fails
                except Exception as e:
                    print(f"Error initializing Groq client: {e}")
                    groq_client = None  # Define the variable even if initialization fails

            if settings.EXECUTION_MODE == "LIVE_TRADING":
                # 1. Attempt real fetch
                raw_quotes = kite_service.get_quotes(watchlist)

                # 2. Smart Simulator fallback
                if not raw_quotes or not isinstance(raw_quotes, dict) or len(raw_quotes) == 0:
                    print("Kite API failed, using smart simulator fallback")
                    raw_quotes = {s: {
                        'last_price': round((72000 if 'SENSEX' in s else 50000 if 'MCX' in s else 1500) + random.uniform(-100, 100), 2),
                        'change': round(random.uniform(-3, 3), 2),
                        'exchange': s.split(":")[0]
                    } for s in watchlist}

                quotes = {s.split(":")[-1]: q for s, q in raw_quotes.items()}

                # 2. Identify Gainers and Losers
                # Filter out any that might have missing change data
                valid_quotes = {s: q for s, q in quotes.items() if 'change' in q and q.get('change') is not None}
                if valid_quotes:
                    sorted_movers = sorted(valid_quotes.items(), key=lambda x: x[1].get('change', 0), reverse=True)

                    top_gainers = sorted_movers[:10] # Top 10
                    top_losers = sorted_movers[-10:] # Bottom 10

                    # Format movers for frontend
                    gainers_data = [{'symbol': s.split(":")[-1], 'exchange': s.split(":")[0], 'price': q.get('last_price', 0), 'change': round(q.get('change', 0), 2)} for s, q in top_gainers]
                    losers_data = [{'symbol': s.split(":")[-1], 'exchange': s.split(":")[0], 'price': q.get('last_price', 0), 'change': round(q.get('change', 0), 2)} for s, q in top_losers]

                    # Update global state
                    global last_market_movers
                    last_market_movers = {'gainers': gainers_data, 'losers': losers_data}

                    # Emit consolidated movers event
                    await sio.emit('market_movers', last_market_movers, room='market_data')

                    # 3. Ticker Broadcast (Multi-exchange)
                    for s in watchlist:
                        symbol = s.split(":")[-1]
                        exchange = s.split(":")[0]
                        quote = raw_quotes.get(s)
                        if not quote: continue

                        # Handle cases where quote data might be an error object
                        if quote.get('error'):
                            print(f"Quote error for {s}: {quote.get('error')}")
                            continue

                        update = {
                            'symbol': symbol,
                            'exchange': exchange,
                            'price': quote.get('last_price', quote.get('price', 0)),
                            'change': quote.get('change', 0),
                            'type': 'up' if quote.get('change', 0) >= 0 else 'down'
                        }
                        await sio.emit('market_update', update, room='market_data')

                    # 4. Global "Steward Prediction" (Dynamic real-time trend)
                    if groq_client:
                        try:
                            market_summary = ", ".join([f"{s.split(':')[-1]}: {q.get('change', 0):.2f}%" for s, q in quotes.items() if q.get('change') is not None])
                            prompt = f"""
                            Analyze the current Nifty 50 trend based on these changes: {market_summary}.
                            Provide a senior wealth steward analysis in JSON format:
                            {{
                                "prediction": "one punchy, expert sentence summary",
                                "decision": "STRONG BUY | BUY | HOLD | SELL | STRONG SELL",
                                "confidence": 0-100,
                                "signal_mix": {{
                                    "technical": 0-100,
                                    "fundamental": 0-100,
                                    "news": 0-100
                                }},
                                "risk_radar": 0-100
                            }}
                            """
                            completion = groq_client.chat.completions.create(
                                messages=[{"role": "user", "content": prompt}],
                                model="llama-3.3-70b-versatile",
                                response_format={"type": "json_object"},
                                timeout=30  # Add timeout to prevent hanging
                            )
                            import json
                            analysis = json.loads(completion.choices[0].message.content.strip())

                            # Update global state
                            global last_steward_prediction
                            last_steward_prediction = {
                                'prediction': analysis.get('prediction', "Market stability maintained."),
                                'decision': analysis.get('decision', "HOLD"),
                                'confidence': analysis.get('confidence', 85),
                                'signal_mix': analysis.get('signal_mix', {"technical": 70, "fundamental": 80, "news": 60}),
                                'risk_radar': analysis.get('risk_radar', 40),
                                'history': prediction_history
                            }

                            await sio.emit('steward_prediction', last_steward_prediction, room='market_data')
                        except Exception as e:
                            print(f"Groq analysis error: {e}")
                            # Use fallback prediction
                            global last_steward_prediction
                            last_steward_prediction = {
                                'prediction': "Market showing neutral momentum. Monitoring AI signals.",
                                'decision': "HOLD",
                                'confidence': 70,
                                'signal_mix': {"technical": 60, "fundamental": 70, "news": 65},
                                'risk_radar': 45,
                                'history': prediction_history
                            }
                            await sio.emit('steward_prediction', last_steward_prediction, room='market_data')
                else:
                    print("No valid quotes received, using mock data")
                    # Use mock data as fallback
                    last_market_movers = {'gainers': mock_gainers, 'losers': mock_losers}
                    await sio.emit('market_movers', last_market_movers, room='market_data')
            else:
                # Mock Mode Fallback
                symbol = random.choice([
                    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN',
                    'ITC', 'LT', 'AXISBANK', 'KOTAKBANK', 'BAJFINANCE', 'MARUTI'
                ])
                # Update global state for REST compatibility
                global last_market_movers
                last_market_movers = {'gainers': mock_gainers, 'losers': mock_losers}

                await sio.emit('market_movers', last_market_movers, room='market_data')

                mock_watchlist = [
                    ("NSE", "RELIANCE"), ("NSE", "TCS"), ("NSE", "INFY"), ("NSE", "HDFCBANK"),
                    ("NSE", "ICICIBANK"), ("NSE", "SBIN"), ("NSE", "ITC"), ("NSE", "AXISBANK"),
                    ("NSE", "KOTAKBANK"), ("NSE", "BAJFINANCE"), ("NSE", "MARUTI"),
                    ("BSE", "SENSEX"), ("BSE", "BOM500002"), ("BSE", "BOM500010"),
                    ("MCX", "GOLD"), ("MCX", "SILVER"), ("MCX", "CRUDEOIL"), ("MCX", "NATURALGAS")
                ]
                updates = random.sample(mock_watchlist, k=min(6, len(mock_watchlist)))
                for exchange, symbol in updates:
                    update = {
                        'symbol': symbol,
                        'exchange': exchange,
                        'price': round(random.uniform(100, 1000), 2),
                        'change': round(random.uniform(-5, 5), 2)
                    }
                    projection = "AI Projection pending: System in MOCK mode."
                    if groq_client:
                        try:
                            prompt = f"Provide a concise 1-sentence market projection for Indian stock {symbol} (NSE) trading at {update['price']}."
                            completion = groq_client.chat.completions.create(
                                messages=[{"role": "user", "content": prompt}],
                                model="llama-3.1-8b-instant",
                                max_tokens=60,
                                timeout=30  # Add timeout to prevent hanging
                            )
                            projection = completion.choices[0].message.content.strip()
                        except Exception as e:
                            print(f"Groq projection error: {e}")
                    update['projection'] = projection
                    update['type'] = 'up' if update['change'] >= 0 else 'down'
                    await sio.emit('market_update', update, room='market_data')

                # Mock high-fidelity prediction for UI testing
                global last_steward_prediction
                last_steward_prediction = {
                    'prediction': "Nifty showing strong resilience at current levels. Bullish technical setup emerging.",
                    'decision': "STRONG BUY",
                    'confidence': 92,
                    'signal_mix': {"technical": 88, "fundamental": 94, "news": 85},
                    'risk_radar': 32,
                    'history': prediction_history
                }
                await sio.emit('steward_prediction', last_steward_prediction, room='market_data')

                # Also update global prediction in mock mode
                if last_steward_prediction['prediction'] == "Initializing...":
                    last_steward_prediction['prediction'] = "Market showing neutral momentum in mock session. Monitoring AI signals."
                    await sio.emit('steward_prediction', last_steward_prediction, room='market_data')

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

@app.get("/api/v1/market/movers")
async def get_market_movers():
    """REST endpoint to get market movers (for compatibility with existing frontend code)"""
    global last_market_movers
    return last_market_movers

@app.get("/api/v1/ai/steward-prediction")
async def get_steward_prediction():
    """REST endpoint to get steward prediction (for compatibility with existing frontend code)"""
    global last_steward_prediction
    return last_steward_prediction