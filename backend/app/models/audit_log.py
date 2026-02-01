from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, index=True)  # e.g., "UPDATE_TRADING_MODE", "CHANGE_SECTORS"
    admin_id = Column(Integer, ForeignKey("users.id"))
    target_user_id = Column(Integer, ForeignKey("users.id"))
    details = Column(Text) # JSON string or text description of change
    reason = Column(String) # Admin comment/reason
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
