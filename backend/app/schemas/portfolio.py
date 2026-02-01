from pydantic import BaseModel
from typing import Optional

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int
    cash_balance: float
    
    class Config:
        from_attributes = True

class PortfolioHistoryPoint(BaseModel):
    date: str
    equity: float
    daily_pnl: float

