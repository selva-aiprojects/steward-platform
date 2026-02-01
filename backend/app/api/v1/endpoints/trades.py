from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from app.api.v1 import deps
from app import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.TradeResponse])
def list_trades() -> Any:
    """
    Retrieve trades.
    """
    # Mock data
    return [
        {
            "id": 1, 
            "symbol": "AAPL", 
            "action": "BUY", 
            "quantity": 10, 
            "price": 150.0, 
            "status": "EXECUTED", 
            "timestamp": "2024-01-01T12:00:00Z",
            "execution_mode": "PAPER_TRADING",
            "risk_score": 10
        }
    ]

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
