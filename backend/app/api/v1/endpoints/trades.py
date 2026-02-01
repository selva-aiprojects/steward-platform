from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from app.api.v1 import deps
from app import schemas

router = APIRouter()

from sqlalchemy.orm import Session
from app.core.database import get_db
from app import models

@router.get("/", response_model=List[schemas.TradeResponse])
def list_trades(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve trades.
    """
    trades = db.query(models.trade.Trade).offset(skip).limit(limit).all()
    return trades

@router.post("/paper/order", response_model=schemas.TradeResult)
async def create_paper_order(proposal: schemas.TradeProposal) -> Any:
    """
    Submit a Paper Trading Order.
    Triggers the full Agentic Logic: User -> Market -> Strategy -> Trade -> Risk -> Execution.
    """
    from app.services.trade_service import TradeService
    
    # Convert Pydantic model to dict for internal flow
    trade_dict = proposal.model_dump()
    
    # Default to Market Order if price is missing
    if not trade_dict.get("price"):
        trade_dict["price"] = 100.0 # Mock current price if not provided
        
    service = TradeService()
    return await service.execute_trade(trade_dict)
