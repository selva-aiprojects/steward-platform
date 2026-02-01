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

class StrategyResponse(StrategyBase):
    id: int
    portfolio_id: int

    class Config:
        from_attributes = True
