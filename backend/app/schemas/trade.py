from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TradeProposal(BaseModel):
    symbol: str
    action: str  # BUY, SELL
    quantity: int
    price: Optional[float] = None # Optional for Market orders
    request_id: Optional[str] = None
    user_id: Optional[int] = None

class TradeResponse(BaseModel):
    id: int
    symbol: str
    action: str
    quantity: int
    price: float
    status: str
    timestamp: datetime
    execution_mode: str
    risk_score: Optional[float] = None
    pnl: Optional[str] = None
    decision_logic: Optional[str] = None
    market_behavior: Optional[str] = None

    class Config:
        from_attributes = True

class TradeResult(BaseModel):
    """
    Response for the Orchestrator Execution.
    """
    status: str
    reason: Optional[str] = None
    trace_id: str
    risk_score: Optional[int] = None
    execution_result: Optional[Dict[str, Any]] = None
    trace: List[Dict[str, Any]]
