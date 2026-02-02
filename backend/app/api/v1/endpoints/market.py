from fastapi import APIRouter, Depends
from typing import Any, List, Dict
from app.core.config import settings

router = APIRouter()

@router.get("/status")
def get_market_status() -> Any:
    """
    Get current market status and latency.
    """
    return {
        "status": "ONLINE",
        "latency": "24ms",
        "exchange": "NSE" # Default to NSE as requested earlier
    }

@router.get("/movers")
def get_market_movers() -> Any:
    """
    Get top gainers and losers.
    Returns cached state from the global market_feed.
    """
    from app.main import last_market_movers
    return last_market_movers
