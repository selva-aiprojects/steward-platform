from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
import json
from app.core.database import get_db
from app.core.rbac import get_current_user, require_roles
from app import models, schemas
from app.services.trade_service import TradeService

router = APIRouter()


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
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"])),
) -> Any:
    approval = db.query(models.trade_approval.TradeApproval).filter(models.trade_approval.TradeApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    if approval.status not in ["PENDING", "REJECTED"]:
        raise HTTPException(status_code=400, detail=f"Approval already {approval.status}")

    approval.status = "APPROVED"
    approval.approver_id = approver_id
    db.add(approval)

    if approver_id is not None:
        db_log = models.AuditLog(
            action="APPROVE_TRADE",
            admin_id=approver_id,
            target_user_id=approval.user_id,
            details=f"Approval {approval.id} executed",
            reason="High-value trade approval"
        )
        db.add(db_log)
    db.commit()
    db.refresh(approval)

    trade_payload: Dict[str, Any] = json.loads(approval.trade_payload)
    trade_payload["approval_id"] = approval.id
    service = TradeService()
    return await service.execute_trade(trade_payload)


@router.post("/{approval_id}/reject")
def reject_trade(
    approval_id: int,
    reason: Optional[str] = None,
    approver_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(require_roles(["SUPERADMIN", "BUSINESS_OWNER"])),
) -> Any:
    approval = db.query(models.trade_approval.TradeApproval).filter(models.trade_approval.TradeApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    if approval.status == "EXECUTED":
        raise HTTPException(status_code=400, detail="Approval already executed")

    approval.status = "REJECTED"
    approval.reason = reason
    approval.approver_id = approver_id
    db.add(approval)

    if approver_id is not None:
        db_log = models.AuditLog(
            action="REJECT_TRADE",
            admin_id=approver_id,
            target_user_id=approval.user_id,
            details=f"Approval {approval.id} rejected",
            reason=reason or "High-value trade rejected"
        )
        db.add(db_log)
    db.commit()
    return {"status": "rejected", "approval_id": approval.id}
