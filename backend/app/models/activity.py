from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String) # MODE_CHANGE, LOGIN, LOGOUT, SETTINGS_UPDATE
    description = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
