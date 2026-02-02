from typing import Any, Dict
from app.agents.base import BaseAgent
from app.core.config import settings

class ExecutionAgent(BaseAgent):
    """
    Responsible for routing the approved trade to the exchange/broker.
    
    Responsibilities:
    - Check Execution Mode (Paper vs Live).
    - Call Broker API.
    - Handle Order Types (Market, Limit).
    """
    
    def __init__(self):
        super().__init__(name="ExecutionAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        from app.services.broker.paper import PaperTradingEngine
        from app.services.broker.live import LiveBrokerAdapter
        
        proposal = context.get("trade_proposal")
        risk_assessment = context.get("risk_assessment", {})
        
        # 1. Validation: Intent Integrity
        if not proposal:
            return {"execution_result": {"status": "SKIPPED", "reason": "No proposal"}}

        # 2. Risk Check (Redundant safety, Orchestrator also checks)
        if not risk_assessment.get("approved"):
             return {
                "execution_result": {
                    "status": "ABORTED",
                    "details": "Risk validation failed"
                }
            }
            
        # 3. Mode Injection
        # CRITICAL: Use mode injected by Orchestrator, do not read settings directly
        mode = context.get("execution_mode", "PAPER_TRADING")
        
        # 4. Adapter Selection
        if mode == "LIVE_TRADING":
            broker = LiveBrokerAdapter()
        else:
            # Fetch default portfolio_id from context or DB
            user_profile = context.get("user_profile", {})
            portfolio_id = user_profile.get("portfolio_id")
            
            if not portfolio_id:
                # Last resort: Try to find any portfolio for user_id
                user_id = context.get("user_id")
                from app.core.database import SessionLocal
                from app.models.portfolio import Portfolio
                db = SessionLocal()
                try:
                    p = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
                    portfolio_id = p.id if p else 1
                finally:
                    db.close()

            broker = PaperTradingEngine(portfolio_id=portfolio_id)
            
        try:
            # 5. Execution
            # Broker executes EXACTLY what is proposed. No modification of intent.
            result = await broker.place_order(
                symbol=proposal.get("symbol"),
                quantity=proposal.get("quantity"),
                action=proposal.get("action"),
                price=proposal.get("price"),
                order_type="MARKET" # Defaulting to Market for now
            )
            
            return {
                "execution_result": {
                    "status": "EXECUTED",
                    "mode": mode,
                    "order_id": result.get("order_id"),
                    "filled_price": result.get("filled_price"),
                    "timestamp": result.get("timestamp"), # Ensure broker returns this
                    "details": result
                }
            }
        except Exception as e:
             return {
                "execution_result": {
                    "status": "FAILED",
                    "mode": mode,
                    "reason": str(e)
                }
            }
