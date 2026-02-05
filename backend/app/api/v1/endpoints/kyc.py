import secrets
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rbac import require_roles
from app.core.security import get_password_hash
from app import models, schemas

router = APIRouter()


@router.post("/applications", response_model=schemas.KYCApplicationResponse)
def create_kyc_application(payload: schemas.KYCApplicationCreate, db: Session = Depends(get_db)):
    kyc = models.KYCApplication(
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
    db.add(kyc)
    db.commit()
    db.refresh(kyc)
    return kyc


@router.get("/applications", response_model=list[schemas.KYCApplicationResponse])
def list_kyc_applications(db: Session = Depends(get_db), _=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"]))):
    return db.query(models.KYCApplication).order_by(models.KYCApplication.created_at.desc()).all()


@router.get("/applications/{kyc_id}", response_model=schemas.KYCApplicationResponse)
def get_kyc_application(kyc_id: int, db: Session = Depends(get_db), _=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER", "AUDITOR"]))):
    kyc = db.query(models.KYCApplication).filter(models.KYCApplication.id == kyc_id).first()
    if not kyc:
        raise HTTPException(status_code=404, detail="KYC application not found")
    return kyc


@router.post("/applications/{kyc_id}/review", response_model=schemas.KYCApplicationResponse)
def review_kyc_application(
    kyc_id: int,
    payload: schemas.KYCReviewAction,
    db: Session = Depends(get_db),
    reviewer=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"]))
):
    kyc = db.query(models.KYCApplication).filter(models.KYCApplication.id == kyc_id).first()
    if not kyc:
        raise HTTPException(status_code=404, detail="KYC application not found")
    if payload.status not in ["UNDER_REVIEW", "REJECTED", "APPROVED"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    kyc.status = payload.status
    kyc.review_notes = payload.review_notes
    kyc.reviewer_id = reviewer.id
    kyc.reviewed_at = datetime.utcnow()
    db.add(kyc)
    db.commit()
    db.refresh(kyc)
    return kyc


@router.post("/applications/{kyc_id}/approve", response_model=schemas.KYCApprovalResponse)
def approve_kyc_application(
    kyc_id: int,
    db: Session = Depends(get_db),
    reviewer=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"]))
):
    kyc = db.query(models.KYCApplication).filter(models.KYCApplication.id == kyc_id).first()
    if not kyc:
        raise HTTPException(status_code=404, detail="KYC application not found")

    temp_password = None
    user = db.query(models.user.User).filter(models.user.User.email == kyc.email).first()
    if not user:
        temp_password = secrets.token_urlsafe(10)
        user = models.user.User(
            email=kyc.email,
            full_name=kyc.full_name,
            hashed_password=get_password_hash(temp_password),
            risk_tolerance=kyc.risk_tolerance or "MODERATE",
            trading_mode=kyc.requested_trading_mode or "AUTO",
            role=kyc.desired_role or "TRADER",
            is_active=True,
            is_superuser=True if (kyc.desired_role or "TRADER") == "SUPERADMIN" else False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    kyc.status = "APPROVED"
    kyc.reviewer_id = reviewer.id
    kyc.reviewed_at = datetime.utcnow()
    db.add(kyc)
    db.commit()

    return schemas.KYCApprovalResponse(kyc_id=kyc.id, user_id=user.id, temp_password=temp_password)


@router.post("/applications/{kyc_id}/reject", response_model=schemas.KYCApplicationResponse)
def reject_kyc_application(
    kyc_id: int,
    payload: schemas.KYCReviewAction,
    db: Session = Depends(get_db),
    reviewer=Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"]))
):
    kyc = db.query(models.KYCApplication).filter(models.KYCApplication.id == kyc_id).first()
    if not kyc:
        raise HTTPException(status_code=404, detail="KYC application not found")
    kyc.status = "REJECTED"
    kyc.review_notes = payload.review_notes
    kyc.reviewer_id = reviewer.id
    kyc.reviewed_at = datetime.utcnow()
    db.add(kyc)
    db.commit()
    db.refresh(kyc)
    return kyc
