"""
Portfolio Allocation Model — stores AI-driven portfolio investment allocations
with 25% buffer tracking for rotation/risk management.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class PortfolioAllocation(Base):
    """
    A single portfolio investment event.
    Tracks the full lifecycle: creation → active → rebalanced → closed.
    """
    __tablename__ = "portfolio_allocations"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, default="AI Portfolio")

    # Investment details
    investment_amount = Column(Float, nullable=False)
    buffer_percentage = Column(Float, default=25.0)
    buffer_amount = Column(Float, default=0.0)
    active_allocation = Column(Float, default=0.0)
    strategy_type = Column(String, default="AI_HYBRID")  # AI_HYBRID, MARKOWITZ, AI_ONLY, MPT_ONLY

    # AI ensemble scores at time of creation (snapshot)
    ai_scores_snapshot = Column(JSON, default=dict)     # {"RELIANCE": 0.82, "TCS": 0.76, ...}
    allocation_map = Column(JSON, default=dict)          # {"RELIANCE": {"weight": 0.185, "amount": 1387.5, "quantity": 3, "ai_score": 0.82}, ...}
    buffer_composition = Column(JSON, default=dict)      # {"rotation_reserve": 0.15, "risk_hedge": 0.10}

    # Status & lifecycle
    status = Column(String, default="ACTIVE")            # ACTIVE, REBALANCED, CLOSED, SUSPENDED
    rebalance_count = Column(Integer, default=0)
    last_rebalance_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime, nullable=True)

    # Performance tracking
    total_pnl = Column(Float, default=0.0)
    total_pnl_pct = Column(Float, default=0.0)

    # Notes / reasoning
    notes = Column(Text, nullable=True)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="allocations")
    user = relationship("User", back_populates="portfolio_allocations")
    rebalance_events = relationship("PortfolioRebalanceEvent", back_populates="allocation", cascade="all, delete-orphan")


class PortfolioRebalanceEvent(Base):
    """
    Tracks every rebalance action taken on a portfolio allocation.
    """
    __tablename__ = "portfolio_rebalance_events"

    id = Column(Integer, primary_key=True, index=True)
    allocation_id = Column(Integer, ForeignKey("portfolio_allocations.id"), nullable=False)
    trigger = Column(String, nullable=False)  # MANUAL, AI_SIGNAL_CHANGE, SCHEDULED, THRESHOLD_BREACH

    # Pre-rebalance state
    previous_allocation_map = Column(JSON, default=dict)
    previous_buffer_amount = Column(Float, default=0.0)

    # Post-rebalance state
    new_allocation_map = Column(JSON, default=dict)
    new_buffer_amount = Column(Float, default=0.0)

    # Orders generated
    rebalance_orders = Column(JSON, default=list)  # [{"symbol": "TCS", "action": "BUY", "quantity": 2, "reason": "AI score increased"}, ...]

    # AI scores at rebalance time
    ai_scores_at_rebalance = Column(JSON, default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    allocation = relationship("PortfolioAllocation", back_populates="rebalance_events")
