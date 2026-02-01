from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.core.database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    name = Column(String, index=True)
    symbol = Column(String)
    status = Column(String) # RUNNING, PAUSED, IDLE
    pnl = Column(String) # e.g. "+4.2%"
    drawdown = Column(Float, default=0.0)
    execution_mode = Column(String, default="PAPER")
