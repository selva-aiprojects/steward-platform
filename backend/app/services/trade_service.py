from typing import Dict, Any
from app.core.config import settings

class TradeService:
    """
    Business logic for trading.
    Delegates to SupervisorAgent for decision making.
    """
    
    async def execute_trade(self, trade_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a trade workflow via the Orchestrator.
        """
        from app.agents.orchestrator import OrchestratorAgent
        from app.core.database import SessionLocal
        from app.models.trade_approval import TradeApproval
        import json
        
        # Initialize the Agentic Workflow
        orchestrator = OrchestratorAgent()
        
        approval_id = trade_proposal.get("approval_id")
        if approval_id and not trade_proposal.get("symbol"):
            db = SessionLocal()
            try:
                approval = db.query(TradeApproval).filter(TradeApproval.id == approval_id).first()
                if approval:
                    trade_proposal = json.loads(approval.trade_payload)
                    trade_proposal["approval_id"] = approval_id
            finally:
                db.close()

        # Prepare initial context
        # In a real app, we'd fetch the user_id from the authenticated session
        context = {
            "request_id": trade_proposal.get("request_id"),
            "user_id": trade_proposal.get("user_id", 1), # Use provided user_id
            "symbol": trade_proposal.get("symbol"),
            "manual_override": trade_proposal,
            "execution_mode": trade_proposal.get("execution_mode"),
            "approval_id": trade_proposal.get("approval_id"),
            "confidence_threshold": trade_proposal.get("confidence_threshold"),
            "approval_threshold": trade_proposal.get("approval_threshold"),
        }
        
        # Run the workflow
        result = await orchestrator.run(context)
        
        return result
