from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, List
from app import schemas, models
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.PortfolioResponse])
def get_portfolios(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all portfolios.
    """
    portfolios = db.query(models.portfolio.Portfolio).offset(skip).limit(limit).all()
    return portfolios

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
