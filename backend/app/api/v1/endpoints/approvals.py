from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from app.core.database import get_db
from app.core.rbac import require_roles
from app import models, schemas
from app.application.trade_application_service import TradeApplicationService

router = APIRouter()
trade_app_service = TradeApplicationService()


@router.get("/", response_model=List[schemas.ApprovalResponse])
def list_approvals(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.user.User = Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER", "AUDITOR"])),
) -> Any:
    query = db.query(models.trade_approval.TradeApproval)
    if status:
        query = query.filter(models.trade_approval.TradeApproval.status == status)
    if user_id:
        query = query.filter(models.trade_approval.TradeApproval.user_id == user_id)
    return query.order_by(models.trade_approval.TradeApproval.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/{approval_id}/approve", response_model=schemas.TradeResult)
async def approve_trade(
    approval_id: int,
    approver_id: Optional[int] = None,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"])),
) -> Any:
    if approver_id is not None and approver_id != current_user.id:
        raise HTTPException(status_code=400, detail="approver_id must match authenticated user")
    try:
        return await trade_app_service.approve_order(
            db=db,
            actor_user=current_user,
            approval_id=approval_id,
            reason=reason,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@router.post("/{approval_id}/reject")
def reject_trade(
    approval_id: int,
    reason: Optional[str] = None,
    approver_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"])),
) -> Any:
    if approver_id is not None and approver_id != current_user.id:
        raise HTTPException(status_code=400, detail="approver_id must match authenticated user")
    try:
        return trade_app_service.cancel_order(
            db=db,
            actor_user=current_user,
            approval_id=approval_id,
            reason=reason,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        status_code = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
