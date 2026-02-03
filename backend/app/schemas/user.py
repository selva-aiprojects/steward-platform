from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    risk_tolerance: Optional[str] = "MODERATE"
    trading_mode: Optional[str] = "AUTO"
    allowed_sectors: Optional[str] = "ALL"
    is_active: bool = True
    trading_suspended: Optional[bool] = False
    approval_threshold: Optional[float] = None
    confidence_threshold: Optional[float] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    trading_mode: Optional[str] = None
    allowed_sectors: Optional[str] = None
    is_active: Optional[bool] = None
    trading_suspended: Optional[bool] = None
    approval_threshold: Optional[float] = None
    confidence_threshold: Optional[float] = None

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True
