from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Dict
from app import schemas, models
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.strategy.StrategyResponse])
def read_strategies(
    db: Session = Depends(get_db),
    user_id: int = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    query = db.query(models.strategy.Strategy)
    if user_id:
        query = query.join(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.strategy.StrategyResponse)
def create_strategy(
    strategy: Dict[Any, Any],
    db: Session = Depends(get_db),
) -> Any:
    """
    Launch a new strategy.
    Maps user_id to portfolio_id for frontend compatibility.
    """
    user_id = strategy.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
        
    portfolio = db.query(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == user_id).first()
    if not portfolio:
        # Auto-create if not exists for demo/dev robustness
        portfolio = models.portfolio.Portfolio(user_id=user_id, name="Auto-Created Portfolio")
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    strat_data = {
        "portfolio_id": portfolio.id,
        "name": strategy.get("name", "Unnamed Strategy"),
        "symbol": strategy.get("symbol", "TCS"),
        "status": strategy.get("status", "RUNNING"),
        "pnl": strategy.get("pnl", "+$0.00"),
        "drawdown": strategy.get("drawdown", 0.0),
        "execution_mode": strategy.get("execution_mode", "PAPER")
    }
    
    db_strategy = models.strategy.Strategy(**strat_data)
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy
