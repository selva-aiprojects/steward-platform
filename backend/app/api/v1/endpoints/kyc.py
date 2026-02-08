from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import secrets

from app.core.database import get_db
from app.core.rbac import require_roles
from app.core.security import get_password_hash
from app import models, schemas

router = APIRouter()


@router.post("/applications", response_model=schemas.KYCApplicationResponse)
def create_kyc_application(
    payload: schemas.KYCApplicationCreate,
    db: Session = Depends(get_db)
):
    # Check if user already has a KYC application
    existing_kyc = db.query(models.kyc.KYCApplication).filter(
        models.kyc.KYCApplication.email == payload.email
    ).first()

    if existing_kyc:
        raise HTTPException(status_code=400, detail="KYC application already exists for this email")

    # Create new KYC application
    kyc_app = models.kyc.KYCApplication(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        dob=payload.dob,
        pan=payload.pan,
        aadhaar_last4=payload.aadhaar_last4,
        address_line1=payload.address_line1,
        address_line2=payload.address_line2,
        city=payload.city,
        state=payload.state,
        pincode=payload.pincode,
        country=payload.country or "India",
        occupation=payload.occupation,
        income_range=payload.income_range,
        source_of_funds=payload.source_of_funds,
        pep=payload.pep or False,
        sanctions=payload.sanctions or False,
        tax_residency=payload.tax_residency or "India",
        bank_account_last4=payload.bank_account_last4,
        ifsc=payload.ifsc,
        desired_role=payload.desired_role or "TRADER",
        requested_trading_mode=payload.requested_trading_mode or "AUTO",
        risk_tolerance=payload.risk_tolerance or "MODERATE",
        documents_json=payload.documents_json,
        status="SUBMITTED",
    )

    db.add(kyc_app)
    db.commit()
    db.refresh(kyc_app)

    return kyc_app


@router.get("/applications", response_model=List[schemas.KYCApplicationResponse])
def list_kyc_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"]))
):
    kyc_applications = db.query(models.kyc.KYCApplication).offset(skip).limit(limit).all()
    return kyc_applications


@router.get("/applications/{kyc_id}", response_model=schemas.KYCApplicationResponse)
def get_kyc_application(
    kyc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER", "AUDITOR"]))
):
    kyc_app = db.query(models.kyc.KYCApplication).filter(
        models.kyc.KYCApplication.id == kyc_id
    ).first()

    if not kyc_app:
        raise HTTPException(status_code=404, detail="KYC application not found")

    return kyc_app


@router.put("/applications/{kyc_id}", response_model=schemas.KYCApplicationResponse)
def update_kyc_application(
    kyc_id: int,
    payload: schemas.KYCApplicationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["TRADER", "SUPERADMIN", "BUSINESS_OWNER"]))
):
    kyc_app = db.query(models.kyc.KYCApplication).filter(
        models.kyc.KYCApplication.id == kyc_id
    ).first()

    if not kyc_app:
        raise HTTPException(status_code=404, detail="KYC application not found")

    # Check permissions - users can only update their own application
    if current_user.role not in ["SUPERADMIN", "BUSINESS_OWNER"] and kyc_app.email != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to update this KYC application")

    # Update fields
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(kyc_app, field) and value is not None:
            setattr(kyc_app, field, value)

    db.add(kyc_app)
    db.commit()
    db.refresh(kyc_app)

    return kyc_app


@router.post("/applications/{kyc_id}/review", response_model=schemas.KYCApplicationResponse)
def review_kyc_application(
    kyc_id: int,
    payload: schemas.KYCReviewAction,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"]))
):
    kyc_app = db.query(models.kyc.KYCApplication).filter(
        models.kyc.KYCApplication.id == kyc_id
    ).first()

    if not kyc_app:
        raise HTTPException(status_code=404, detail="KYC application not found")

    if payload.status not in ["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    kyc_app.status = payload.status
    kyc_app.review_notes = payload.review_notes
    kyc_app.reviewer_id = current_user.id
    kyc_app.reviewed_at = datetime.utcnow()

    db.add(kyc_app)
    db.commit()
    db.refresh(kyc_app)

    return kyc_app


@router.post("/applications/{kyc_id}/approve", response_model=schemas.KYCApprovalResponse)
def approve_kyc_application(
    kyc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"]))
):
    kyc_app = db.query(models.kyc.KYCApplication).filter(
        models.kyc.KYCApplication.id == kyc_id
    ).first()

    if not kyc_app:
        raise HTTPException(status_code=404, detail="KYC application not found")

    # Check if user already exists
    existing_user = db.query(models.user.User).filter(
        models.user.User.email == kyc_app.email
    ).first()

    temp_password = None
    user_id = None
    if not existing_user:
        # Create user account
        temp_password = secrets.token_urlsafe(12)
        user = models.user.User(
            email=kyc_app.email,
            full_name=kyc_app.full_name,
            hashed_password=get_password_hash(temp_password),
            risk_tolerance=kyc_app.risk_tolerance or "MODERATE",
            trading_mode=kyc_app.requested_trading_mode or "AUTO",
            role=kyc_app.desired_role or "TRADER",
            is_active=True,
            is_superuser=(kyc_app.desired_role == "SUPERADMIN")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
    else:
        user_id = existing_user.id

    # Update KYC status
    kyc_app.status = "APPROVED"
    kyc_app.reviewer_id = current_user.id
    kyc_app.reviewed_at = datetime.utcnow()

    db.add(kyc_app)
    db.commit()

    return schemas.KYCApprovalResponse(
        kyc_id=kyc_app.id,
        user_id=user_id,
        temp_password=temp_password
    )


@router.post("/applications/{kyc_id}/reject", response_model=schemas.KYCApplicationResponse)
def reject_kyc_application(
    kyc_id: int,
    payload: schemas.KYCReviewAction,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"]))
):
    kyc_app = db.query(models.kyc.KYCApplication).filter(
        models.kyc.KYCApplication.id == kyc_id
    ).first()

    if not kyc_app:
        raise HTTPException(status_code=404, detail="KYC application not found")

    kyc_app.status = "REJECTED"
    kyc_app.review_notes = payload.review_notes
    kyc_app.reviewer_id = current_user.id
    kyc_app.reviewed_at = datetime.utcnow()

    db.add(kyc_app)
    db.commit()
    db.refresh(kyc_app)

    return kyc_app


# Include the router in the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8000)