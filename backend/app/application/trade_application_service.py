from __future__ import annotations

from collections import defaultdict
import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)


class LegacyTradeExecutionGateway:
    """
    Compatibility adapter over the existing orchestrator-driven trade flow.
    This lets API endpoints move to a canonical application service without
    breaking runtime behavior during migration.
    """

    async def execute(self, trade_payload: Dict[str, Any]) -> Dict[str, Any]:
        from app.services.trade_service import TradeService

        service = TradeService()
        return await service.execute_trade(trade_payload)


class TradeApplicationService:
    ADMIN_READ_ROLES = {"SUPERADMIN", "BUSINESS_OWNER", "AUDITOR"}
    ADMIN_EXECUTE_ROLES = {"SUPERADMIN", "BUSINESS_OWNER"}
    APPROVAL_REQUIRED_STATES = {"PENDING", "REJECTED"}
    ORDER_STATES = {
        "PENDING",
        "APPROVAL_REQUIRED",
        "APPROVED",
        "REJECTED_RISK",
        "SUBMITTED",
        "FILLED",
        "FAILED",
        "CANCELLED",
    }

    def __init__(self, execution_gateway: Optional[LegacyTradeExecutionGateway] = None):
        self.execution_gateway = execution_gateway or LegacyTradeExecutionGateway()

    def list_trades(
        self,
        *,
        db: Session,
        actor_user: User,
        requested_user_id: Optional[int],
        skip: int = 0,
        limit: int = 100,
    ) -> List[models.trade.Trade]:
        resolved_user_id = self._resolve_read_user_id(
            actor_user=actor_user,
            requested_user_id=requested_user_id,
        )
        query = db.query(models.trade.Trade)
        if resolved_user_id:
            query = query.join(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == resolved_user_id)
        return query.offset(skip).limit(limit).all()

    async def execute_trade(
        self,
        *,
        actor_user: User,
        proposal: Dict[str, Any],
        force_execution_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._validate_proposal(proposal)

        requested_user_id = proposal.get("user_id")
        target_user_id = self._resolve_execute_user_id(
            actor_user=actor_user,
            requested_user_id=requested_user_id,
        )

        trade_payload = dict(proposal)
        trade_payload["user_id"] = target_user_id
        if force_execution_mode:
            trade_payload["execution_mode"] = force_execution_mode
        self._assert_live_trading_allowed(
            db=None,
            user_id=target_user_id,
            execution_mode=trade_payload.get("execution_mode"),
        )

        return await self.execution_gateway.execute(trade_payload)

    async def submit_order(
        self,
        *,
        db: Session,
        actor_user: User,
        proposal: Dict[str, Any],
        force_execution_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._validate_proposal(proposal)

        requested_user_id = proposal.get("user_id")
        target_user_id = self._resolve_execute_user_id(
            actor_user=actor_user,
            requested_user_id=requested_user_id,
        )
        trade_payload = dict(proposal)
        trade_payload["user_id"] = target_user_id
        if force_execution_mode:
            trade_payload["execution_mode"] = force_execution_mode
        self._assert_live_trading_allowed(
            db=db,
            user_id=target_user_id,
            execution_mode=trade_payload.get("execution_mode"),
        )

        estimated_total = float(trade_payload.get("estimated_total") or (trade_payload["price"] * trade_payload["quantity"]))
        approval_threshold = settings.HIGH_VALUE_TRADE_THRESHOLD

        if estimated_total >= approval_threshold:
            approval = models.trade_approval.TradeApproval(
                user_id=target_user_id,
                status="PENDING",
                trade_payload=json.dumps(trade_payload),
                reason=f"Manual approval required for value >= {approval_threshold}",
            )
            db.add(approval)
            db.commit()
            db.refresh(approval)
            self._record_trade_event(
                db=db,
                user_id=target_user_id,
                approval_id=approval.id,
                event_type="APPROVAL_REQUIRED",
                payload={
                    "threshold": approval_threshold,
                    "estimated_total": estimated_total,
                },
            )
            return {
                "status": "APPROVAL_REQUIRED",
                "reason": "Trade requires manual approval",
                "approval_id": approval.id,
                "trade_state": "APPROVAL_REQUIRED",
            }

        execution_result = await self.execution_gateway.execute(trade_payload)
        execution_status = str(execution_result.get("status", "")).upper()
        trade_state = "FILLED" if execution_status == "EXECUTED" else "FAILED"
        self._record_trade_event(
            db=db,
            user_id=target_user_id,
            approval_id=None,
            event_type="EXECUTION_ATTEMPT",
            payload={"result_status": execution_result.get("status"), "trade_state": trade_state},
        )
        if isinstance(execution_result, dict):
            execution_result.setdefault("trade_state", trade_state)
        return execution_result

    async def approve_order(
        self,
        *,
        db: Session,
        actor_user: User,
        approval_id: int,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        if actor_user.role not in self.ADMIN_EXECUTE_ROLES:
            raise PermissionError("Insufficient privileges to approve trades")

        approval = db.query(models.trade_approval.TradeApproval).filter(models.trade_approval.TradeApproval.id == approval_id).first()
        if not approval:
            raise ValueError("Approval request not found")
        if approval.status not in self.APPROVAL_REQUIRED_STATES:
            raise ValueError(f"Approval already {approval.status}")

        approval.status = "APPROVED"
        approval.approver_id = actor_user.id
        if reason:
            approval.reason = reason
        db.add(approval)
        self._add_audit_log(
            db=db,
            action="APPROVE_TRADE",
            admin_id=actor_user.id,
            target_user_id=approval.user_id,
            details=f"Approval {approval.id} approved",
            reason=reason or "High-value trade approval",
        )
        db.commit()
        db.refresh(approval)
        self._record_trade_event(
            db=db,
            user_id=approval.user_id,
            approval_id=approval.id,
            event_type="APPROVED",
            payload={"approved_by": actor_user.id},
        )

        trade_payload: Dict[str, Any] = json.loads(approval.trade_payload or "{}")
        trade_payload["approval_id"] = approval.id
        requested_user_id = trade_payload.get("user_id")
        target_user_id = self._resolve_execute_user_id(
            actor_user=actor_user,
            requested_user_id=requested_user_id,
        )
        trade_payload["user_id"] = target_user_id
        self._assert_live_trading_allowed(
            db=db,
            user_id=target_user_id,
            execution_mode=trade_payload.get("execution_mode"),
        )
        execution_result = await self.execution_gateway.execute(trade_payload)

        if execution_result.get("status") == "EXECUTED":
            approval.status = "EXECUTED"
            db.add(approval)
            db.commit()
            self._record_trade_event(
                db=db,
                user_id=approval.user_id,
                approval_id=approval.id,
                event_type="EXECUTED",
                payload={"trace_id": execution_result.get("trace_id")},
            )
        return execution_result

    def cancel_order(
        self,
        *,
        db: Session,
        actor_user: User,
        approval_id: int,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        approval = db.query(models.trade_approval.TradeApproval).filter(models.trade_approval.TradeApproval.id == approval_id).first()
        if not approval:
            raise ValueError("Approval request not found")
        is_admin = actor_user.role in self.ADMIN_EXECUTE_ROLES
        if not is_admin and actor_user.id != approval.user_id:
            raise PermissionError("Cannot cancel another user's trade approval")
        if approval.status == "EXECUTED":
            raise ValueError("Approval already executed")

        approval.status = "REJECTED"
        approval.reason = reason
        approval.approver_id = actor_user.id if is_admin else approval.approver_id
        db.add(approval)
        self._add_audit_log(
            db=db,
            action="REJECT_TRADE",
            admin_id=actor_user.id if is_admin else None,
            target_user_id=approval.user_id,
            details=f"Approval {approval.id} rejected",
            reason=reason or "Trade cancelled",
        )
        db.commit()
        self._record_trade_event(
            db=db,
            user_id=approval.user_id,
            approval_id=approval.id,
            event_type="REJECTED",
            payload={"rejected_by": actor_user.id, "reason": reason},
        )
        return {"status": "rejected", "approval_id": approval.id}

    def get_daily_pnl(
        self,
        *,
        db: Session,
        actor_user: User,
        requested_user_id: Optional[int],
    ) -> List[Dict[str, Any]]:
        resolved_user_id = self._resolve_read_user_id(
            actor_user=actor_user,
            requested_user_id=requested_user_id,
        )
        query = db.query(models.trade.Trade)
        if resolved_user_id:
            query = query.join(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == resolved_user_id)
        trades = query.all()

        daily_stats = defaultdict(lambda: {"user": 0.0, "agent": 0.0})
        for trade in trades:
            date_str = trade.timestamp.strftime("%a")
            pnl_str = (trade.pnl or "0%").replace("%", "")
            try:
                pnl_val = float(pnl_str)
            except Exception:
                pnl_val = 0.0
            if trade.execution_mode == "MANUAL":
                daily_stats[date_str]["user"] += pnl_val
            else:
                daily_stats[date_str]["agent"] += pnl_val

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        result: List[Dict[str, Any]] = []
        for day in days:
            if day in daily_stats:
                result.append(
                    {
                        "name": day,
                        "user": round(daily_stats[day]["user"], 2),
                        "agent": round(daily_stats[day]["agent"], 2),
                    }
                )
            else:
                result.append({"name": day, "user": 0, "agent": 0})
        return result

    def _resolve_read_user_id(self, *, actor_user: User, requested_user_id: Optional[int]) -> int:
        target_user_id = requested_user_id or actor_user.id
        if actor_user.role not in self.ADMIN_READ_ROLES and target_user_id != actor_user.id:
            raise PermissionError("Cannot access other user data")
        return target_user_id

    def _resolve_execute_user_id(self, *, actor_user: User, requested_user_id: Optional[int]) -> int:
        target_user_id = requested_user_id or actor_user.id
        if actor_user.role not in self.ADMIN_EXECUTE_ROLES and target_user_id != actor_user.id:
            raise PermissionError("Cannot execute trades for another user")
        return target_user_id

    def _validate_proposal(self, proposal: Dict[str, Any]) -> None:
        if proposal.get("price") is None:
            raise ValueError("Price is required for execution")
        if proposal.get("quantity") is None or int(proposal.get("quantity", 0)) <= 0:
            raise ValueError("Quantity must be greater than 0")
        if not proposal.get("symbol"):
            raise ValueError("Symbol is required for execution")
        action = str(proposal.get("action", "")).upper()
        if action not in {"BUY", "SELL"}:
            raise ValueError("Action must be BUY or SELL")

    def _add_audit_log(
        self,
        *,
        db: Session,
        action: str,
        admin_id: Optional[int],
        target_user_id: Optional[int],
        details: str,
        reason: Optional[str],
    ) -> None:
        db_log = models.AuditLog(
            action=action,
            admin_id=admin_id,
            target_user_id=target_user_id,
            details=details,
            reason=reason,
        )
        db.add(db_log)

    def _record_trade_event(
        self,
        *,
        db: Session,
        user_id: Optional[int],
        approval_id: Optional[int],
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            event = models.TradeEvent(
                user_id=user_id,
                approval_id=approval_id,
                event_type=event_type,
                payload=json.dumps(payload or {}),
            )
            db.add(event)
            db.commit()
        except Exception as error:
            db.rollback()
            logger.warning("Trade event persistence skipped: %s", error)

    def _assert_live_trading_allowed(
        self,
        *,
        db: Optional[Session],
        user_id: int,
        execution_mode: Optional[str],
    ) -> None:
        mode = str(execution_mode or settings.EXECUTION_MODE).upper()
        if mode != "LIVE_TRADING":
            return
        if db is None:
            # Legacy execute path does not pass db session. Treat as restricted in live mode.
            raise PermissionError("Live trading requires verified KYC context")
        latest_kyc = (
            db.query(models.KYCApplication)
            .filter(models.KYCApplication.user_id == user_id)
            .order_by(models.KYCApplication.updated_at.desc())
            .first()
        )
        if not latest_kyc or latest_kyc.status != "APPROVED":
            raise PermissionError("Live trading requires approved KYC")
