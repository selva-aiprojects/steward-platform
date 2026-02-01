from fastapi import APIRouter
from typing import Any, List
from app import schemas

router = APIRouter()

@router.get("/", response_model=schemas.PortfolioResponse)
def get_portfolio() -> Any:
    """
    Get current portfolio.
    """
    # Mock Return
    return {
        "id": 1,
        "user_id": 1,
        "name": "Main Portfolio",
        "description": "Primary trading account",
        "cash_balance": 100000.0
    }

@router.get("/history", response_model=List[schemas.PortfolioHistoryPoint])
def get_portfolio_history() -> Any:
    """
    Get historical portfolio performance (Equity & PnL).
    """
    # Mock Data Generation
    history = []
    equity = 100000.0
    import random
    from datetime import datetime, timedelta
    
    base_date = datetime.utcnow() - timedelta(days=30)
    
    for i in range(30):
        daily_pnl = random.uniform(-1000, 1500)
        equity += daily_pnl
        history.append({
            "date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "equity": round(equity, 2),
            "daily_pnl": round(daily_pnl, 2)
        })
        
    return history
