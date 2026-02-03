from pydantic import BaseModel
from typing import Optional, List

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int
    cash_balance: float
    invested_amount: float
    win_rate: float
    
    class Config:
        from_attributes = True

class PortfolioHistoryPoint(BaseModel):
    name: str
    value: float
    daily_pnl: float

class HoldingResponse(BaseModel):
    id: int
    portfolio_id: int
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    pnl: float
    pnl_pct: float

    class Config:
        from_attributes = True

class DepositRequest(BaseModel):
    user_id: int
    amount: float

