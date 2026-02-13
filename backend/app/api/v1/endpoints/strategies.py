from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Dict
from app import schemas, models
from app.core.database import get_db
from app.core.rbac import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.strategy.StrategyResponse])
def read_strategies(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_id: int = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    query = db.query(models.strategy.Strategy)

    # Allow users to only see their own strategies unless they're an admin
    if user_id:
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to view strategies for this user")
        query = query.join(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == user_id)
    else:
        # Default to current user's strategies
        query = query.join(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == current_user.id)

    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.strategy.StrategyResponse)
def create_strategy(
    strategy: schemas.strategy.StrategyLaunchRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Launch a new strategy using user_id.
    Maps user_id to portfolio_id for frontend compatibility.
    """
    # Ensure the user can only create strategies for themselves
    if strategy.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to create strategy for this user")

    portfolio = db.query(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == strategy.user_id).first()
    if not portfolio:
        # Auto-create portfolio if not exists for demo robustness
        portfolio = models.portfolio.Portfolio(user_id=strategy.user_id, name="Auto-Created Portfolio")
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    strat_data = {
        "portfolio_id": portfolio.id,
        "name": strategy.name,
        "symbol": strategy.symbol,
        "status": strategy.status,
        "pnl": strategy.pnl,
        "drawdown": strategy.drawdown,
        "execution_mode": strategy.execution_mode
    }

    db_strategy = models.strategy.Strategy(**strat_data)
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy
