from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


class ApprovalCreate(BaseModel):
    user_id: int
    trade_payload: Dict[str, Any]
    reason: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: int
    user_id: int
    status: str
    trade_payload: str
    reason: Optional[str] = None
    approver_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

