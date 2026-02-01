from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Projection(Base):
    __tablename__ = "projections"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    move_prediction = Column(String) # e.g. "+3.8%"
    action = Column(String) # ACCUMULATE, BUY, TRIM, SELL, HOLD
    logic = Column(String)
