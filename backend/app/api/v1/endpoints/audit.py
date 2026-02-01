from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.AuditLogResponse)
def create_audit_log(
    log: schemas.AuditLogCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new audit log entry (Admin Action).
    """
    db_log = models.AuditLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/", response_model=List[schemas.AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    target_user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Get audit logs. Optionally filter by target user.
    """
    query = db.query(models.AuditLog)
    if target_user_id:
        query = query.filter(models.AuditLog.target_user_id == target_user_id)
    
    return query.order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
