from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, index=True)
    risk_tolerance = Column(String, default="MODERATE") # LOW, MODERATE, HIGH, AGGRESSIVE
    trading_mode = Column(String, default="AUTO") # AUTO, MANUAL
    role = Column(String, default="TRADER") # SUPERADMIN, BUSINESS_OWNER, TRADER, AUDITOR
    allowed_sectors = Column(String, default="ALL") # Comma-separated list or "ALL"
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    trading_suspended = Column(Boolean, default=False)
    approval_threshold = Column(Float, nullable=True)
    confidence_threshold = Column(Float, nullable=True)

    # Relationships
    optimization_results = relationship("PortfolioOptimizationResult", back_populates="user")
    strategy_optimization_results = relationship("StrategyOptimizationResult", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")
    trades = relationship("Trade", back_populates="user")
    trade_approvals = relationship("TradeApproval", back_populates="user")
    activities = relationship("Activity", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    kyc = relationship("KYC", back_populates="user")
    watchlists = relationship("Watchlist", back_populates="user")
