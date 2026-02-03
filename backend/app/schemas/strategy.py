from pydantic import BaseModel
from typing import Optional

class StrategyBase(BaseModel):
    name: str
    symbol: str
    status: str
    pnl: str
    drawdown: float = 0.0
    execution_mode: str = "PAPER"

class StrategyCreate(StrategyBase):
    portfolio_id: int

class StrategyLaunchRequest(BaseModel):
    user_id: int
    name: str = "Unnamed Strategy"
    symbol: str = "TCS"
    status: str = "RUNNING"
    pnl: str = "+₹0.00"
    drawdown: float = 0.0
    execution_mode: str = "PAPER"

class StrategyResponse(StrategyBase):
    id: int
    portfolio_id: int

    class Config:
        from_attributes = True
