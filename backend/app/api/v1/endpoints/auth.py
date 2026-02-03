from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password
from app import models, schemas

router = APIRouter()


@router.post("/login", response_model=schemas.LoginResponse)
def login(
    payload: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.user.User).filter(models.user.User.email == payload.email).first()
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
