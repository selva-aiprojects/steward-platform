import sys
import os

# Add backend directory to path so FastAPI imports work cleanly inside Vercel serverless environment
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import traceback

app = FastAPI()

try:
    from app.main import app as _real_app
    app.mount("", _real_app)
except Exception as e:
    err_trace = traceback.format_exc()
    import logging
    logging.error(f"Failed to import app.main: {err_trace}")
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    async def catch_all(path: str):
        return JSONResponse(
            status_code=500,
            content={"error": "Serverless Module Import Crash", "traceback": err_trace}
        )
