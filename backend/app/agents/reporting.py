from typing import Any, Dict
from app.agents.base import BaseAgent

class ReportingAgent(BaseAgent):
    """
    Responsible for auditing and notification.
    
    Responsibilities:
    - Log the entire transaction flow.
    - Save to Database (Services layer usually helps here, but agent triggers it).
    - Notify User (Email/SMS/UI Alert).
    """
    
    def __init__(self):
        super().__init__(name="ReportingAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a comprehensive audit record and human-readable narrative.
        """
        from datetime import datetime
        
        # 1. Extract artifacts from context
        trace_id = context.get("trace_id")
        user = context.get("user_profile", {})
        market = context.get("market_data", {})
        strategy = context.get("strategy_signal", {})
        proposal = context.get("trade_proposal")
        risk = context.get("risk_assessment", {})
        execution = context.get("execution_result", {})
        
        # 2. Determine Final Status
        if execution.get("status") == "EXECUTED":
            status = "COMPLETED"
        elif risk.get("approved") is False:
            status = "REJECTED_RISK"
        elif not proposal:
            status = "SKIPPED_NO_SIGNAL"
        elif execution.get("status") == "FAILED":
            status = "FAILED_EXECUTION"
        else:
            status = "UNKNOWN"

        # 3. Deterministic Narrative Generation (No LLM here, pure logic for audit)
        narrative_parts = []
        
        # User & Market Context
        narrative_parts.append(f"Trace {trace_id}: Processing for User (Risk: {user.get('risk_tolerance', 'N/A')}).")
        narrative_parts.append(f"Market Condition: {market.get('trend', 'Unknown')} trend detected for {market.get('symbol', 'Unknown')}.")
        
        # Strategy
        if strategy:
            narrative_parts.append(f"Strategy '{strategy.get('strategy_used')}' signal: {strategy.get('signal')} ({strategy.get('confidence', 0)*100:.0f}% confidence).")
            narrative_parts.append(f"Rationale: {strategy.get('rationale')}")
        
        # Proposal
        if proposal:
            narrative_parts.append(f"Proposed Action: {proposal.get('action')} {proposal.get('quantity')} units @ ${proposal.get('price')}.")
        else:
            narrative_parts.append("No actionable trade proposed.")
            
        # Risk (The filter)
        if risk:
            if risk.get("approved"):
                narrative_parts.append("Risk Management: APPROVED.")
            else:
                narrative_parts.append(f"Risk Management: REJECTED. Reason: {risk.get('reason')}.")
                
        # Execution
        if execution and status == "COMPLETED":
            narrative_parts.append(f"Execution: SUCCESS via {execution.get('mode')} using {execution.get('details', {}).get('engine', 'Unknown')}.")
            narrative_parts.append(f"Filled @ ${execution.get('filled_price')} (Order ID: {execution.get('order_id')}).")
        elif execution.get("status") == "FAILED":
             narrative_parts.append(f"Execution: FAILED. Reason: {execution.get('reason')}.")

        final_narrative = " ".join(narrative_parts)

        # 4. Structured Audit Object
        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "status": status,
            "symbol": market.get("symbol"),
            "components": {
                "strategy": strategy.get("strategy_used"),
                "signal": strategy.get("signal"),
                "risk_score": risk.get("risk_score"),
                "execution_mode": context.get("execution_mode")
            },
            "narrative": final_narrative
        }

        # Persist to audit log for regression coverage.
        try:
            from app.core.database import SessionLocal
            from app.models.audit_log import AuditLog
            import json

            user_id = context.get("user_id") or user.get("id") or 1
            symbol = proposal.get("symbol") if proposal else market.get("symbol")
            action = f"TRADE_{status}"
            if symbol:
                action = f"{action}_{symbol}"

            db = SessionLocal()
            try:
                db_log = AuditLog(
                    action=action,
                    admin_id=user_id,
                    target_user_id=user_id,
                    details=json.dumps(audit_record),
                    reason="Automated trade audit"
                )
                db.add(db_log)
                db.commit()
            finally:
                db.close()
        except Exception:
            pass

        # Return record to update context.
        return {
            "report": audit_record
        }
