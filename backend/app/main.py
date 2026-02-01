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

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('market_update', {'symbol': 'SPY', 'price': 450.20, 'change': '+0.5%'}, to=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# Background Market Publisher (Mock)
import asyncio
import random

async def market_feed():
    try:
        while True:
            await asyncio.sleep(2)
            update = {
                'symbol': random.choice(['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN']),
                'price': round(random.uniform(100, 1000), 2),
                'change': f"{random.choice(['+', '-'])}{round(random.uniform(0, 5), 2)}%"
            }
            await sio.emit('market_update', update)
    except Exception as e:
        print(f"Market feed error: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(market_feed())

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
