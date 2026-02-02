from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db as _get_db
from app.models.user import User

def get_db() -> Generator:
    try:
        db = next(_get_db())
        yield db
    except StopIteration:
        # Fallback if the generator is empty or misconfigured
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

async def get_current_active_user(
    db: Session = Depends(get_db)
) -> User:
    """
    Mock authentication dependency. 
    In a real system, this would verify a JWT token.
    For now, it returns the first user in the database to allow development.
    """
    user = db.query(User).first()
    if not user:
        # Create a default user if none exists (safety for fresh DBs)
        user = User(
            email="admin@stocksteward.ai",
            full_name="Default Admin",
            hashed_password="mock",
            is_active=True,
            is_superuser=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
