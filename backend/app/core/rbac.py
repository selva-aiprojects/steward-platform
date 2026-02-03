from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Iterable

from app.core.database import get_db
from app.models.user import User


def get_current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
    db: Session = Depends(get_db),
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing user identity")
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    if x_user_role and user.role and user.role != x_user_role:
        raise HTTPException(status_code=403, detail="Role mismatch")
    return user


def require_roles(roles: Iterable[str]):
    allowed = set(roles)

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return current_user

    return dependency

