from fastapi import APIRouter, Depends
from typing import Any, List, Dict
from app.core.config import settings
import random

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


@router.get("/heatmap")
def get_sector_heatmap() -> Any:
    sectors = [
        "Banking", "IT", "Energy", "FMCG", "Auto", "Metals", "Pharma", "Infra"
    ]
    return [
        {"sector": s, "score": round(random.uniform(-5, 5), 2)}
        for s in sectors
    ]


@router.get("/news")
def get_market_news() -> Any:
    headlines = [
        "FIIs net buyers as Nifty holds key support",
        "Banking stocks lead rally on credit growth optimism",
        "IT majors steady ahead of weekly earnings updates",
        "Oil slips; metals mixed in early trade",
        "Rupee stabilizes as dollar index softens"
    ]
    random.shuffle(headlines)
    return [{"headline": h, "impact": random.choice(["LOW", "MEDIUM", "HIGH"])} for h in headlines[:4]]


@router.get("/options")
def get_options_snapshot() -> Any:
    symbols = ["NIFTY", "BANKNIFTY", "RELIANCE", "TCS"]
    return [
        {
            "symbol": s,
            "iv": round(random.uniform(12, 28), 2),
            "oi_change": round(random.uniform(-8, 8), 2),
            "put_call": round(random.uniform(0.6, 1.4), 2)
        } for s in symbols
    ]


@router.get("/depth")
def get_order_book_depth() -> Any:
    bids = [{"price": round(2200 + i * 0.5, 2), "qty": random.randint(50, 500)} for i in range(5)]
    asks = [{"price": round(2202 + i * 0.5, 2), "qty": random.randint(50, 500)} for i in range(5)]
    return {"bids": bids, "asks": asks}


@router.get("/macro")
def get_macro_indicators() -> Any:
    return {
        "usd_inr": round(random.uniform(82.5, 84.5), 2),
        "gold": round(random.uniform(60000, 65000), 2),
        "crude": round(random.uniform(70, 86), 2),
        "10y_yield": round(random.uniform(6.8, 7.4), 2)
    }
