from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password
from app import models, schemas

router = APIRouter()


@router.post("/login", response_model=schemas.LoginResponse)
@router.post("/login/", response_model=schemas.LoginResponse)
def login(
    payload: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.user.User).filter(models.user.User.email == payload.email).first()
    default_passwords = {
        "admin@stocksteward.ai": "admin123",
        "admin@stocksteward-ai": "admin123",
        "owner@stocksteward.ai": "owner123",
        "trader@stocksteward.ai": "trader123",
        "auditor@stocksteward.ai": "audit123",
    }
    # Auto-provision default superadmin if missing (fresh DB on hosted env)
    # Support both email formats for compatibility
    if not user and payload.email in ["admin@stocksteward.ai", "admin@stocksteward-ai"] and payload.password == "admin123":
        from app.core.security import get_password_hash
        # Use the email format that the user is trying to log in with for consistency
        user = models.user.User(
            id=999,
            full_name="Super Admin",
            email=payload.email,  # Use the email the user provided
            hashed_password=get_password_hash("admin123"),
            risk_tolerance="LOW",
            is_active=True,
            role="SUPERADMIN",
            is_superuser=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # If a seeded account exists with a different password, reset to default for demo access
    if user and payload.email in default_passwords and payload.password == default_passwords[payload.email]:
        if not verify_password(payload.password, user.hashed_password):
            from app.core.security import get_password_hash
            user.hashed_password = get_password_hash(payload.password)
            db.add(user)
            db.commit()
            db.refresh(user)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role or ("SUPERADMIN" if user.is_superuser else "TRADER"),
        "trading_mode": user.trading_mode,
        "risk_tolerance": user.risk_tolerance,
    }


@router.options("/login")
@router.options("/login/")
def login_options():
    return Response(status_code=204)
