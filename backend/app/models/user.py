from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, index=True)
    risk_tolerance = Column(String, default="MODERATE") # LOW, MODERATE, HIGH, AGGRESSIVE
    trading_mode = Column(String, default="AUTO") # AUTO, MANUAL
    allowed_sectors = Column(String, default="ALL") # Comma-separated list or "ALL"
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
