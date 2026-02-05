from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class KYCApplication(Base):
    __tablename__ = "kyc_applications"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    dob = Column(String, nullable=True)
    pan = Column(String, nullable=True)
    aadhaar_last4 = Column(String, nullable=True)

    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    country = Column(String, default="India")

    occupation = Column(String, nullable=True)
    income_range = Column(String, nullable=True)
    source_of_funds = Column(String, nullable=True)

    pep = Column(Boolean, default=False)
    sanctions = Column(Boolean, default=False)
    tax_residency = Column(String, default="India")

    bank_account_last4 = Column(String, nullable=True)
    ifsc = Column(String, nullable=True)

    desired_role = Column(String, default="TRADER")
    requested_trading_mode = Column(String, default="AUTO")
    risk_tolerance = Column(String, default="MODERATE")

    documents_json = Column(Text, nullable=True)

    status = Column(String, default="DRAFT", index=True)  # DRAFT, SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
