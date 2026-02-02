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

# Global state for immediate feed on join
last_market_movers = {'gainers': [], 'losers': []}
last_steward_prediction = {"prediction": "Initializing...", "history": []}

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
    from app.services.kite_service import kite_service
    from app.core.config import settings
    import os
    import random
    
    # Nifty 50 & Bank Nifty Extended Watchlist
    watchlist = [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
        'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'TITAN', 'BAJFINANCE', 'WIPRO', 'ULTRACEMCO', 'SUNPHARMA', 'NESTLEIND',
        'M&M', 'ADANIENT', 'POWERGRID', 'TATASTEEL', 'NTPC', 'JSWSTEEL', 'GRASIM', 'COALINDIA', 'HCLTECH', 'ADANIPORTS',
        'INDUSINDBK', 'BAJAJFINSV', 'ONGC', 'TATAMOTORS', 'HDFCLIFE', 'SBILIFE', 'DRREDDY', 'CIPLA', 'APOLLOHOSP', 'DIVISLAB'
    ]
    
    # Store history in memory (simple deque-like structure)
    prediction_history = []
    
    while True:
        # 30-60 second cycle for comprehensive analysis to avoid rate limits
        # Using 10s for demo responsiveness
        await asyncio.sleep(10 if settings.EXECUTION_MODE == "LIVE_TRADING" else 5)
        
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
                top_gainers = sorted_movers[:5] # Top 5
                top_losers = sorted_movers[-5:] # Bottom 5
                
                # Format movers for frontend
                gainers_data = [{'symbol': s, 'price': q['last_price'], 'change': q['change']} for s, q in top_gainers]
                losers_data = [{'symbol': s, 'price': q['last_price'], 'change': q['change']} for s, q in top_losers]
                
                # Update global state
                global last_market_movers
                last_market_movers = {'gainers': gainers_data, 'losers': losers_data}
                
                # Emit consolidated movers event
                await sio.emit('market_movers', last_market_movers, room='market_data')

                # 3. Setup Groq for projections (if key exists)
                groq_key = os.getenv("GROQ_API_KEY")
                groq_client = None
                if groq_key:
                    try:
                        from groq import Groq
                        groq_client = Groq(api_key=groq_key)
                    except ImportError:
                        print("Groq library not installed")

                # Emit individual updates for ticker tape effects
                movers = top_gainers[:2] + top_losers[-2:]
                for symbol, quote in movers:
                    projection = "Strategic analysis pending..."
                    if groq_client:
                        try:
                            # Contextual prompt for Groq
                            prompt = f"Provide a concise 1-sentence market projection/advice for Indian stock {symbol} (NSE) trading at {quote['last_price']} ({quote['change']}% change today)."
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
                        
                        # Update global state
                        global last_steward_prediction
                        last_steward_prediction = {'prediction': prediction, 'history': prediction_history}
                            
                        await sio.emit('steward_prediction', last_steward_prediction, room='market_data')
                    except Exception:
                        pass
            else:
                # Mock Mode Fallback
                symbol = random.choice(['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK'])
                mock_gainers = [{'symbol': 'MOCK_UP', 'price': 120.5, 'change': 2.5}, {'symbol': 'MOCK_UP2', 'price': 300, 'change': 1.2}]
                mock_losers = [{'symbol': 'MOCK_DN', 'price': 90.5, 'change': -1.5}, {'symbol': 'MOCK_DN2', 'price': 50, 'change': -0.8}]
                
                await sio.emit('market_movers', {'gainers': mock_gainers, 'losers': mock_losers}, room='market_data')

                update = {
                    'symbol': symbol,
                    'price': round(random.uniform(100, 1000), 2),
                    'change': f"{random.choice(['+', '-'])}{round(random.uniform(0, 5), 2)}%",
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
