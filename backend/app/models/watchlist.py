from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.core.database import Base

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String, index=True)
    # Optional fields for simulation
    current_price = Column(Float, default=0.0)
    change = Column(String, default="0.0%")
