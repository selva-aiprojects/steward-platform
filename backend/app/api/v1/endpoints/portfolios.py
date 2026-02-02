from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from app import schemas, models
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.PortfolioResponse])
def get_portfolios(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all portfolios or a specific user's portfolio.
    """
    query = db.query(models.portfolio.Portfolio)
    if user_id:
        query = query.filter(models.portfolio.Portfolio.user_id == user_id)
    
    portfolios = query.offset(skip).limit(limit).all()
    return portfolios

@router.get("/history", response_model=List[schemas.PortfolioHistoryPoint])
def get_portfolio_history(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Any:
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

@router.post("/deposit", response_model=schemas.PortfolioResponse)
def deposit_funds(
    *,
    db: Session = Depends(get_db),
    deposit_in: schemas.DepositRequest,
) -> Any:
    """
    Deposit funds into a user's portfolio.
    """
    portfolio = db.query(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == deposit_in.user_id).first()
    if not portfolio:
        # Create portfolio if not exists
        portfolio = models.portfolio.Portfolio(
            user_id=deposit_in.user_id,
            name="Primary Wealth Vault",
            cash_balance=deposit_in.amount,
            invested_amount=0.0
        )
        db.add(portfolio)
    else:
        portfolio.cash_balance += deposit_in.amount
        db.add(portfolio)
    
    db.commit()
    db.refresh(portfolio)
    return portfolio

@router.get("/holdings", response_model=List[schemas.HoldingResponse])
def get_holdings(
    *,
    db: Session = Depends(get_db),
    user_id: int,
) -> Any:
    """
    Get all holdings for a user's portfolio.
    """
    portfolio = db.query(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == user_id).first()
    if not portfolio:
        return []
    
    return portfolio.holdings
