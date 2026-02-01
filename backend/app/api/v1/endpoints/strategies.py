from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, List
from app import schemas, models
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.strategy.StrategyResponse])
def read_strategies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return db.query(models.strategy.Strategy).offset(skip).limit(limit).all()
