from fastapi import APIRouter, Depends, HTTPException
from app.core.config import settings
from app.core.rbac import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/observability/embed-url")
def get_observability_embed_url(current_user: User = Depends(get_current_user)):
    if current_user.role != "SUPERADMIN" and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    url = settings.SUPERSET_EMBED_URL or "http://localhost:8088/superset/dashboard/stocksteward-executive-overview/"

    # In production, do not disclose embed URLs to non-superadmins (strict gate).
    if settings.APP_ENV == "PROD" and (current_user.role != "SUPERADMIN" and not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    return {"url": url}
