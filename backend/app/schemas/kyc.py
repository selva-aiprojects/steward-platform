from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class KYCApplicationBase(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    dob: Optional[str] = None
    pan: Optional[str] = None
    aadhaar_last4: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = "India"

    occupation: Optional[str] = None
    income_range: Optional[str] = None
    source_of_funds: Optional[str] = None

    pep: Optional[bool] = False
    sanctions: Optional[bool] = False
    tax_residency: Optional[str] = "India"

    bank_account_last4: Optional[str] = None
    ifsc: Optional[str] = None

    desired_role: Optional[str] = "TRADER"
    requested_trading_mode: Optional[str] = "AUTO"
    risk_tolerance: Optional[str] = "MODERATE"

    documents_json: Optional[str] = None


class KYCApplicationCreate(KYCApplicationBase):
    pass


class KYCApplicationUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    pan: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    occupation: Optional[str] = None
    income_range: Optional[str] = None
    source_of_funds: Optional[str] = None
    pep: Optional[bool] = None
    sanctions: Optional[bool] = None
    tax_residency: Optional[str] = None
    bank_account_last4: Optional[str] = None
    ifsc: Optional[str] = None
    desired_role: Optional[str] = None
    requested_trading_mode: Optional[str] = None
    risk_tolerance: Optional[str] = None
    documents_json: Optional[str] = None
    status: Optional[str] = None


class KYCReviewAction(BaseModel):
    status: str  # UNDER_REVIEW, APPROVED, REJECTED
    review_notes: Optional[str] = None


class KYCApplicationResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    dob: Optional[str] = None
    pan: Optional[str] = None
    aadhaar_last4: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = "India"

    occupation: Optional[str] = None
    income_range: Optional[str] = None
    source_of_funds: Optional[str] = None

    pep: Optional[bool] = False
    sanctions: Optional[bool] = False
    tax_residency: Optional[str] = "India"

    bank_account_last4: Optional[str] = None
    ifsc: Optional[str] = None

    desired_role: Optional[str] = "TRADER"
    requested_trading_mode: Optional[str] = "AUTO"
    risk_tolerance: Optional[str] = "MODERATE"

    documents_json: Optional[str] = None
    status: str
    reviewer_id: Optional[int] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KYCApprovalResponse(BaseModel):
    kyc_id: int
    user_id: int
    temp_password: Optional[str] = None

    class Config:
        from_attributes = True