from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

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
