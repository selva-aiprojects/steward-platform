from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
from app import schemas, models
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.watchlist.WatchlistItemResponse])
def get_watchlist(
    db: Session = Depends(get_db),
    user_id: int = 1, # Default for demo
) -> Any:
    return db.query(models.watchlist.WatchlistItem).filter(models.watchlist.WatchlistItem.user_id == user_id).all()

@router.post("/", response_model=schemas.watchlist.WatchlistItemResponse)
def add_to_watchlist(
    item: schemas.watchlist.WatchlistItemCreate,
    db: Session = Depends(get_db),
) -> Any:
    # Check if exists
    existing = db.query(models.watchlist.WatchlistItem).filter(
        models.watchlist.WatchlistItem.user_id == item.user_id,
        models.watchlist.WatchlistItem.symbol == item.symbol
    ).first()
    if existing:
        return existing
    
    db_item = models.watchlist.WatchlistItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{symbol}")
def delete_from_watchlist(
    symbol: str,
    user_id: int = 1,
    db: Session = Depends(get_db),
) -> Any:
    item = db.query(models.watchlist.WatchlistItem).filter(
        models.watchlist.WatchlistItem.user_id == user_id,
        models.watchlist.WatchlistItem.symbol == symbol
    ).first()
    if item:
        db.delete(item)
        db.commit()
    return {"status": "success"}
