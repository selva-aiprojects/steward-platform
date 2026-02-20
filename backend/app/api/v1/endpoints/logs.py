from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.core.rbac import get_current_user
from app.models.user import User

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("frontend_errors")

class ErrorLog(BaseModel):
    level: str
    message: str
    context: Optional[Dict[str, Any]] = None
    source: str

@router.post("/error")
def log_frontend_error(error: ErrorLog):
    """
    Log critical frontend errors to the backend system.
    """
    if error.level == "CRITICAL":
        logger.critical(f"FRONTEND CRASH: {error.message} | Context: {error.context}")
    else:
        logger.error(f"Frontend Error: {error.message}")
    
    # In a real system, we would insert this into an 'error_logs' table in DB
    
    return {"status": "logged", "level": error.level}


@router.get("/metrics")
def get_metrics(current_user: User = Depends(get_current_user)):
    """
    Superadmin-only Prometheus metrics endpoint.
    """
    if current_user.role != "SUPERADMIN" and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    payload = generate_latest()
    return Response(content=payload, media_type=CONTENT_TYPE_LATEST)
