from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware
import socketio
import asyncio
import random
import os

# Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Agentic AI-driven stock stewardship platform.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO Setup
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# Global state for immediate feed on join
last_market_movers = {'gainers': [], 'losers': []}
last_steward_prediction = {"prediction": "Initializing...", "history": []}

# Mock data for fallback mode
mock_gainers = [
    {'symbol': 'RELIANCE', 'price': 2450.00, 'change': '+1.20%'},
    {'symbol': 'TCS', 'price': 3820.00, 'change': '+0.85%'},
    {'symbol': 'INFY', 'price': 1540.00, 'change': '+2.10%'},
    {'symbol': 'HDFCBANK', 'price': 1680.00, 'change': '+1.45%'},
    {'symbol': 'ICICIBANK', 'price': 940.00, 'change': '+1.15%'}
]
mock_losers = [
    {'symbol': 'WIPRO', 'price': 420.00, 'change': '-1.10%'},
    {'symbol': 'TATASTEEL', 'price': 115.00, 'change': '-2.30%'},
    {'symbol': 'ONGC', 'price': 185.00, 'change': '-0.95%'},
    {'symbol': 'SBIN', 'price': 580.00, 'change': '-1.50%'},
    {'symbol': 'ITC', 'price': 440.00, 'change': '-0.75%'}
]

@sio.event
async def join_stream(sid, data):
    """
    Clients request to join specific role-based streams.
    Data expected: {'role': 'ADMIN' | 'USER', 'userId': ...}
    """
    role = data.get('role', 'USER')
    print(f"Socket {sid} requesting stream access for role: {role}")
    
    # 1. End User Stream (Standard Market Data)
    if role in ['USER', 'ADMIN', 'BUSINESS_OWNER']:
        await sio.enter_room(sid, 'market_data')
        await sio.emit('stream_status', {'msg': 'Connected to Live Market Feed'}, to=sid)
        
        # Immediate state send
        if last_market_movers['gainers']:
            await sio.emit('market_movers', last_market_movers, to=sid)
        if last_steward_prediction['prediction'] != "Initializing...":
            await sio.emit('steward_prediction', last_steward_prediction, to=sid)

    # 2. Superadmin & Business Owner Stream (System Telemetry)
    if role in ['ADMIN', 'BUSINESS_OWNER']:
        await sio.enter_room(sid, 'admin_data')
        await sio.emit('stream_status', {'msg': 'Connected to Command Center Telemetry'}, to=sid)
        
    # 3. Auditor Stream
    if role == 'AUDITOR':
        await sio.enter_room(sid, 'compliance_log')

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

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
        # BSE 
        'BSE:SENSEX', 'BSE:BOM500002', 'BSE:BOM500010',
        # Commodities (MCX)
        'MCX:GOLD', 'MCX:SILVER', 'MCX:CRUDEOIL', 'MCX:NATURALGAS'
    ]
    
    # Store history in memory (simple deque-like structure)
    prediction_history = []
    
    while True:
        # 30-60 second cycle for comprehensive analysis to avoid rate limits
        # Using 10s for demo responsiveness
        await asyncio.sleep(10 if settings.EXECUTION_MODE == "LIVE_TRADING" else 5)
        
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

            if settings.EXECUTION_MODE == "LIVE_TRADING":
                # 1. Attempt real fetch
                raw_quotes = kite_service.get_quotes(watchlist)
                
                # 2. Smart Simulator fallback
                if not raw_quotes:
                    raw_quotes = {s: {
                        'last_price': round((72000 if 'SENSEX' in s else 50000 if 'MCX' in s else 1500) + random.uniform(-100, 100), 2),
                        'change': round(random.uniform(-3, 3), 2),
                        'exchange': s.split(":")[0]
                    } for s in watchlist}

                quotes = {s.split(":")[-1]: q for s, q in raw_quotes.items()}

                # 2. Identify Gainers and Losers
                # Filter out any that might have missing change data
                valid_quotes = {s: q for s, q in quotes.items() if 'change' in q}
                sorted_movers = sorted(valid_quotes.items(), key=lambda x: x[1].get('change', 0), reverse=True)
                
                top_gainers = sorted_movers[:5] # Top 5
                top_losers = sorted_movers[-5:] # Bottom 5
                
                # Format movers for frontend
                gainers_data = [{'symbol': s.split(":")[-1], 'exchange': s.split(":")[0], 'price': q['last_price'], 'change': round(q.get('change', 0), 2)} for s, q in top_gainers]
                losers_data = [{'symbol': s.split(":")[-1], 'exchange': s.split(":")[0], 'price': q['last_price'], 'change': round(q.get('change', 0), 2)} for s, q in top_losers]
                
                # Update global state
                last_market_movers = {'gainers': gainers_data, 'losers': losers_data}
                
                # Emit consolidated movers event
                await sio.emit('market_movers', last_market_movers, room='market_data')


                # 4. Ticker Broadcast (Multi-exchange)
                for s in watchlist:
                    symbol = s.split(":")[-1]
                    quote = raw_quotes.get(s)
                    if not quote: continue
                    
                    update = {
                        'symbol': symbol,
                        'exchange': s.split(":")[0],
                        'price': quote['last_price'],
                        'change': quote['change'],
                        'type': 'up' if quote['change'] >= 0 else 'down'
                    }
                    await sio.emit('market_update', update, room='market_data')

                # 4. Global "Steward Prediction" (Dynamic real-time trend)
                if groq_client:
                    try:
                        market_summary = ", ".join([f"{s}: {q.get('change', 0):.2f}%" for s, q in quotes.items()])
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
                            response_format={"type": "json_object"}
                        )
                        import json
                        analysis = json.loads(completion.choices[0].message.content.strip())
                        
                        # Update global state
                        last_steward_prediction = {
                            'prediction': analysis.get('prediction', "Market stability maintained."),
                            'decision': analysis.get('decision', "HOLD"),
                            'confidence': analysis.get('confidence', 85),
                            'signal_mix': analysis.get('signal_mix', {"technical": 70, "fundamental": 80, "news": 60}),
                            'risk_radar': analysis.get('risk_radar', 40),
                            'history': prediction_history
                        }
                            
                        await sio.emit('steward_prediction', last_steward_prediction, room='market_data')
                    except Exception:
                        pass
            else:
                # Mock Mode Fallback
                symbol = random.choice(['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK'])
                # Update global state for REST compatibility
                last_market_movers = {'gainers': mock_gainers, 'losers': mock_losers}
                
                await sio.emit('market_movers', last_market_movers, room='market_data')

                update = {
                    'symbol': symbol,
                    'price': round(random.uniform(100, 1000), 2),
                    'change': round(random.uniform(-5, 5), 2)
                }
                projection = "AI Projection pending: System in MOCK mode."
                
                # Enable Groq Analysis even for Mock Data if available
                if groq_client:
                    try:
                        prompt = f"Provide a concise 1-sentence market projection for Indian stock {symbol} (NSE) trading at {update['price']}."
                        completion = groq_client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.1-8b-instant",
                            max_tokens=60
                        )
                        projection = completion.choices[0].message.content.strip()
                    except Exception:
                        pass

                update['projection'] = projection
                update['type'] = 'up' # Mock change logic
                await sio.emit('market_update', update, room='market_data')
                
                # Mock high-fidelity prediction for UI testing
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
    if os.getenv("DISABLE_BACKGROUND_TASKS") == "1":
        return
    asyncio.create_task(market_feed())
    asyncio.create_task(admin_feed())

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "StockSteward AI Backend is fully operational",
        "mode": settings.EXECUTION_MODE,
        "risk_policy": "STRICT"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
