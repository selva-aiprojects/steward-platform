from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class TradeApproval(Base):
    __tablename__ = "trade_approvals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(String, default="PENDING")  # PENDING, APPROVED, REJECTED, EXECUTED
    trade_payload = Column(Text)  # JSON payload for the proposed trade
    reason = Column(String, nullable=True)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
