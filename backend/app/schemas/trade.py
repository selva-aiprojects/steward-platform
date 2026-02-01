from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TradeProposal(BaseModel):
    symbol: str
    action: str  # BUY, SELL
    quantity: int
    price: Optional[float] = None # Optional for Market orders

class TradeResponse(BaseModel):
    id: int
    symbol: str
    action: str
    quantity: int
    price: float
    status: str
    timestamp: datetime
    execution_mode: str
    risk_score: Optional[int] = None

    class Config:
        from_attributes = True

class TradeResult(BaseModel):
    """
    Response for the Orchestrator Execution.
    """
    status: str
    reason: Optional[str] = None
    trace_id: str
    trace: List[Dict[str, Any]]
