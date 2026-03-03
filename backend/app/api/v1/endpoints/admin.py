from fastapi import APIRouter, Depends, HTTPException
from app.core.config import settings
from app.core.rbac import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/observability/embed-url")
def get_observability_embed_url(current_user: User = Depends(get_current_user)):
    if current_user.role != "SUPERADMIN" and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    superset_url = settings.SUPERSET_EMBED_URL or "http://localhost:8088/superset/dashboard/stocksteward-executive-overview/"
    grafana_url = os.getenv("GRAFANA_URL") or "http://localhost:3001"

    return {
        "superset_url": superset_url,
        "grafana_url": grafana_url
    }
