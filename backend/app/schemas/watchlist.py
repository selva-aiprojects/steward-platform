from pydantic import BaseModel
from typing import Optional

class WatchlistItemBase(BaseModel):
    symbol: str
    current_price: float = 0.0
    change: str = "0.0%"

class WatchlistItemCreate(WatchlistItemBase):
    user_id: int

class WatchlistItemResponse(WatchlistItemBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
