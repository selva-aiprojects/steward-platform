from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Any, List
from app import schemas, models
from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.rbac import get_current_user, require_roles

router = APIRouter()
ALLOWED_ROLES = {"SUPERADMIN", "BUSINESS_OWNER", "TRADER", "AUDITOR"}

@router.post("/", response_model=schemas.UserResponse)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
    current_user: models.user.User = Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"])),
) -> Any:
    """
    Create new user.
    """
    user = db.query(models.user.User).filter(models.user.User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    if user_in.role and user_in.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user = models.user.User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password if hasattr(user_in, "password") else "default_stock_steward_123"), 
        risk_tolerance=user_in.risk_tolerance,
        trading_mode=user_in.trading_mode,
        role=user_in.role or "TRADER",
        allowed_sectors=user_in.allowed_sectors,
        is_active=user_in.is_active,
        trading_suspended=user_in.trading_suspended,
        approval_threshold=user_in.approval_threshold,
        confidence_threshold=user_in.confidence_threshold,
        is_superuser=True if user_in.role == "SUPERADMIN" else False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/", response_model=List[schemas.UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.user.User = Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"])),
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(models.user.User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: models.user.User = Depends(get_current_user),
) -> Any:
    """
    Get a specific user by id.
    """
    if current_user.role not in ["SUPERADMIN", "BUSINESS_OWNER", "AUDITOR"] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    user = db.query(models.user.User).filter(models.user.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.user.User = Depends(get_current_user),
) -> Any:
    """
    Update a user.
    """
    user = db.query(models.user.User).filter(models.user.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role == "TRADER" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    if current_user.role == "AUDITOR":
        raise HTTPException(status_code=403, detail="Read-only role")

    # Check if trading mode is changing
    if user_in.trading_mode and user_in.trading_mode != user.trading_mode:
        activity = models.activity.Activity(
            user_id=user.id,
            activity_type="MODE_CHANGE",
            description=f"Trading mode updated to {user_in.trading_mode}"
        )
        db.add(activity)

    update_data = user_in.model_dump(exclude_unset=True)
    if current_user.role == "TRADER":
        allowed_fields = {"trading_mode"}
        disallowed = set(update_data.keys()) - allowed_fields
        if disallowed:
            raise HTTPException(status_code=403, detail="Cannot modify restricted fields")
    if "role" in update_data:
        if update_data["role"] not in ALLOWED_ROLES:
            raise HTTPException(status_code=400, detail="Invalid role")
        update_data["is_superuser"] = update_data["role"] == "SUPERADMIN"
    for field in update_data:
        setattr(user, field, update_data[field])

    db.add(user)
    if update_data:
        import json
        audit = models.AuditLog(
            action="UPDATE_USER",
            admin_id=current_user.id,
            target_user_id=user.id,
            details=json.dumps(update_data),
            reason="User profile update"
        )
        db.add(audit)
    db.commit()
    db.refresh(user)
    return user
