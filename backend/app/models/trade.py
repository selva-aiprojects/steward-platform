from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String, index=True)
    action = Column(String) # BUY, SELL
    quantity = Column(Integer)
    price = Column(Float)
    status = Column(String) # PENDING, EXECUTED, REJECTED, FAILED
    execution_mode = Column(String) # PAPER, LIVE
    
    # Auditing
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    risk_score = Column(Float)
    rejection_reason = Column(String, nullable=True)
    
    # Intelligence Journal Fields
    pnl = Column(String, nullable=True) # e.g. "+2.41%"
    decision_logic = Column(String, nullable=True)
    market_behavior = Column(String, nullable=True)

