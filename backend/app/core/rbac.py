from fastapi import Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Iterable

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from jose import JWTError, jwt


def get_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    user_id_query: int | None = Query(default=None, alias="user_id"), # Fallback for dev ease
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
    db: Session = Depends(get_db),
) -> User:
    token_user_id = None
    token_role = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            token_user_id = payload.get("user_id")
            token_role = payload.get("role")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    if token_user_id is not None:
        x_user_id = int(token_user_id)
        if not x_user_role and token_role:
            x_user_role = str(token_role)

    # Use query param fallback in dev if header is missing
    app_env = (settings.APP_ENV or "DEV").upper()
    if app_env == "PROD" and token_user_id is None:
        raise HTTPException(status_code=401, detail="Bearer token required")

    if token_user_id is None and not settings.ALLOW_HEADER_IDENTITY:
        x_user_id = None
        x_user_role = None

    if x_user_id is None and user_id_query is not None and app_env in {"DEV", "TEST"}:
        x_user_id = user_id_query

    if x_user_id is None:
        if settings.ALLOW_DEV_USER_FALLBACK and app_env in {"DEV", "QA", "UAT", "TEST"}:
            user = db.query(User).first()
            if user:
                return user
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
