from fastapi import APIRouter, HTTPException
from typing import Any
from app import schemas

router = APIRouter()

@router.post("/", response_model=schemas.UserResponse)
def create_user(
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    # Mock Database interaction
    # user = crud.user.create(db, obj_in=user_in)
    return {
        "id": 1,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "is_active": True
    }
