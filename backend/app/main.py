from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware
import socketio
import asyncio
import random

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

# Role-Based Room Management
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    # Default: All users get public market data
    await sio.save_session(sid, {'role': 'GUEST'})

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

    # 2. Superadmin & Business Owner Stream (System Telemetry)
    if role in ['ADMIN', 'BUSINESS_OWNER']:
        await sio.enter_room(sid, 'admin_telemetry')
        await sio.emit('stream_status', {'msg': 'Connected to Command Center Telemetry'}, to=sid)
        
    # 3. Auditor Stream (Future Scope Placeholder)
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
    from app.services.kite_service import kite_service
    from app.core.config import settings
    import os
    import random
    
    # Nifty 50 watchlist for dashboard movers
    watchlist = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK']
    
    while True:
        # 30-60 second cycle for comprehensive analysis to avoid rate limits
        await asyncio.sleep(60 if settings.EXECUTION_MODE == "LIVE_TRADING" else 5)
        
        try:
            if settings.EXECUTION_MODE == "LIVE_TRADING":
                # 1. Fetch real quotes for the watchlist
                quotes = {}
                for symbol in watchlist:
                    q = kite_service.get_quote(symbol)
                    if q:
                        # Kite quote 'change' is usually pre-calculated
                        quotes[symbol] = q
                
                if not quotes:
                    continue

                # 2. Identify Gainers and Losers
                sorted_movers = sorted(quotes.items(), key=lambda x: x[1].get('change', 0), reverse=True)
                top_gainers = sorted_movers[:2]
                top_losers = sorted_movers[-2:]
                
                movers = top_gainers + top_losers
                
                # 3. Setup Groq for projections (if key exists)
                groq_key = os.getenv("GROQ_API_KEY")
                groq_client = None
                if groq_key:
                    try:
                        from groq import Groq
                        groq_client = Groq(api_key=groq_key)
                    except ImportError:
                        print("Groq library not installed")

                for symbol, quote in movers:
                    projection = "Strategic analysis pending..."
                    if groq_client:
                        try:
                            # Contextual prompt for Groq
                            prompt = f"Provide a concise 1-sentence market projection/advice for {symbol} trading at {quote['last_price']} ({quote['change']}% change today)."
                            completion = groq_client.chat.completions.create(
                                messages=[{"role": "user", "content": prompt}],
                                model="llama-3.1-8b-instant",
                                max_tokens=60
                            )
                            projection = completion.choices[0].message.content.strip()
                        except Exception as ge:
                            projection = f"AI Analysis deferred: {str(ge)[:30]}..."

                    update = {
                        'symbol': symbol,
                        'price': quote.get('last_price'),
                        'change': f"{'+' if quote.get('change', 0) >= 0 else ''}{quote.get('change', 0):.2f}%",
                        'projection': projection,
                        'type': 'up' if quote.get('change', 0) >= 0 else 'down'
                    }
                    await sio.emit('market_update', update, room='market_data')

                # 4. Global "Steward Prediction" (Dynamic real-time trend)
                if groq_client:
                    try:
                        market_summary = ", ".join([f"{s}: {q.get('change', 0):.2f}%" for s, q in quotes.items()])
                        prompt = f"Summarize the current Nifty trend in one punchy, expert sentence based on these Nifty 50 changes: {market_summary}. Act as a senior wealth steward."
                        completion = groq_client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile",
                            max_tokens=100
                        )
                        prediction = completion.choices[0].message.content.strip()
                        await sio.emit('steward_prediction', {'prediction': prediction}, room='market_data')
                    except Exception:
                        pass
            else:
                # Mock Mode Fallback
                symbol = random.choice(['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN'])
                update = {
                    'symbol': symbol,
                    'price': round(random.uniform(100, 1000), 2),
                    'change': f"{random.choice(['+', '-'])}{round(random.uniform(0, 5), 2)}%",
                    'projection': "AI Projection pending: System in MOCK mode.",
                    'type': 'up' # Mock change logic
                }
                await sio.emit('market_update', update, room='market_data')
                
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
