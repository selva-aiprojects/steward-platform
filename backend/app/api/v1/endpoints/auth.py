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
    try:
        user = db.query(models.user.User).filter(models.user.User.email == payload.email).first()

        # Define default passwords
        default_passwords = {
            "admin@stocksteward.ai": "admin123",
            "owner@stocksteward.ai": "owner123",
            "trader@stocksteward.ai": "trader123",
            "auditor@stocksteward.ai": "auditor123",
        }

        # Auto-provision default users if missing (fresh DB on hosted env)
        if not user and payload.email in default_passwords and payload.password == default_passwords[payload.email]:
            from app.core.security import get_password_hash
            # Determine role based on email
            role_map = {
                "admin@stocksteward.ai": "SUPERADMIN",
                "owner@stocksteward.ai": "BUSINESS_OWNER",
                "trader@stocksteward.ai": "TRADER",
                "auditor@stocksteward.ai": "AUDITOR"
            }

            role = role_map.get(payload.email, "TRADER")
            full_name_map = {
                "admin@stocksteward.ai": "Super Admin",
                "owner@stocksteward.ai": "Business Owner",
                "trader@stocksteward.ai": "Trader User",
                "auditor@stocksteward.ai": "Auditor User"
            }

            user = models.user.User(
                id=999 if payload.email == "admin@stocksteward.ai" else None,
                full_name=full_name_map.get(payload.email, "Default User"),
                email=payload.email,  # Use the email the user provided
                hashed_password=get_password_hash(default_passwords[payload.email]),
                risk_tolerance="MODERATE",
                is_active=True,
                role=role,
                is_superuser=(role == "SUPERADMIN"),
                trading_mode="AUTO"  # Add default trading mode
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        # If a seeded account exists with a different password, reset to default for demo access
        elif user and payload.email in default_passwords and payload.password == default_passwords[payload.email]:
            if not verify_password(payload.password, user.hashed_password):
                from app.core.security import get_password_hash
                user.hashed_password = get_password_hash(payload.password)
                db.add(user)
                db.commit()
                db.refresh(user)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role or ("SUPERADMIN" if user.is_superuser else "TRADER"),
            "trading_mode": user.trading_mode or "AUTO",  # Provide default if not set
            "risk_tolerance": user.risk_tolerance,
        }
    finally:
        db.close()


@router.options("/login")
@router.options("/login/")
def login_options(response: Response):
    response.status_code = 204
    return response
