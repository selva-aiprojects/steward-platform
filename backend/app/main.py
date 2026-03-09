import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.api import api_router
from app.core.config import settings
from app.observability.middleware import RequestContextMiddleware
from app.realtime.streaming import setup_socket, start_background_tasks
from app.startup import startup_sequence

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Agentic AI-driven stock stewardship platform.",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(RequestContextMiddleware)

allowed_origins = settings.cors_origins_list or ["http://localhost:3000"]
logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio, socket_app = setup_socket(app, allowed_origins)


@app.on_event("startup")
async def startup_event():
    try:
        await startup_sequence()
        logging.info("Application startup sequence completed successfully")
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        raise
    start_background_tasks(sio)


@app.get("/")
async def root():
    return {
        "message": "StockSteward AI Backend is fully operational",
        "mode": settings.EXECUTION_MODE,
        "risk_policy": "STRICT",
    }


app.include_router(api_router, prefix=settings.API_V1_STR)
Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
).instrument(app)


@app.get("/health")
async def health_check():
    return {"status": "ok", "build": "realtime-module-refactor"}

