from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware
import socketio

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

# Background Market Publisher (Public)
async def market_feed():
    while True:
        await asyncio.sleep(2)
        try:
            update = {
                'symbol': random.choice(['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN']),
                'price': round(random.uniform(100, 1000), 2),
                'change': f"{random.choice(['+', '-'])}{round(random.uniform(0, 5), 2)}%"
            }
            # Emit to specific room
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
