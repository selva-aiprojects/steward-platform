from typing import Any, Dict
from app.agents.base import BaseAgent
from app.agents.user_profile import UserProfileAgent
from app.agents.market_data import MarketDataAgent
from app.agents.strategy import StrategyAgent
from app.agents.trade_decision import TradeDecisionAgent
from app.agents.risk_management import RiskManagementAgent
from app.agents.execution import ExecutionAgent
from app.agents.reporting import ReportingAgent

class OrchestratorAgent(BaseAgent):
    """
    The Conductor.
    
    Responsibilities:
    - Manages the lifecycle of a request.
    - Instantiates (or calls) specific agents in the correct order.
    - Passes context between agents.
    - Handles failures.
    - ENSURES NO AGENT CALLS ANOTHER DIRECTLY.
    """
    
    def __init__(self):
        super().__init__(name="OrchestratorAgent")
        # Initialize sub-agents
        self.user_profile = UserProfileAgent()
        self.market_data = MarketDataAgent()
        self.strategy = StrategyAgent()
        self.trade_decision = TradeDecisionAgent()
        self.risk_management = RiskManagementAgent()
        self.execution = ExecutionAgent()
        self.reporting = ReportingAgent()

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the full investment workflow.
        Flow: User -> Market -> Strategy -> Trade Decision -> Risk -> Execution -> Reporting
        """
        import uuid
        from datetime import datetime
        from app.core.config import settings

        trace_id = str(uuid.uuid4())
        context["trace_id"] = trace_id
        context["execution_mode"] = context.get("execution_mode") or settings.EXECUTION_MODE
        context["confidence_threshold"] = context.get("confidence_threshold") or settings.DEFAULT_CONFIDENCE_THRESHOLD
        context["approval_threshold"] = context.get("approval_threshold") or settings.HIGH_VALUE_TRADE_THRESHOLD
        
        # Ensure user_id is valid
        if not context.get("user_id"):
            # Try to get from trade_proposal if present
            proposal = context.get("manual_override") # TradeService puts it here
            if proposal and proposal.get("user_id"):
                context["user_id"] = proposal.get("user_id")
            else:
                context["user_id"] = 1 # Absolute fallback
        
        # decision trace log
        trace = []
        
        def log_step(agent_name: str, output: Dict[str, Any]):
            trace.append({
                "step": agent_name,
                "timestamp": datetime.utcnow().isoformat(),
                "output": output
            })

        try:
            # 1. User Profile (User)
            user_out = await self.user_profile.run(context)
            context.update(user_out)
            log_step("UserProfileAgent", user_out)

            user_profile = context.get("user_profile", {})
            if user_profile.get("approval_threshold"):
                context["approval_threshold"] = user_profile.get("approval_threshold")
            if user_profile.get("confidence_threshold"):
                context["confidence_threshold"] = user_profile.get("confidence_threshold")

            # Global/User Kill Switch Gate
            if settings.GLOBAL_KILL_SWITCH or user_profile.get("trading_suspended"):
                return {
                    "status": "SUSPENDED",
                    "reason": "Trading suspended by policy",
                    "trace_id": trace_id,
                    "trace": trace
                }

            # Environment guardrail for live trading
            if context.get("execution_mode") == "LIVE_TRADING":
                if settings.APP_ENV != "PROD" or not settings.ENABLE_LIVE_TRADING:
                    context["execution_mode"] = "PAPER_TRADING"
                    context["live_guardrail"] = "blocked"

            # 2. Market Data (Market)
            market_out = await self.market_data.run(context)
            context.update(market_out)
            log_step("MarketDataAgent", market_out)

            # 3. Strategy (Strategy)
            strategy_out = await self.strategy.run(context)
            context.update(strategy_out)
            log_step("StrategyAgent", strategy_out)

            # 4. Trade Decision (Trade Decision)
            decision_out = await self.trade_decision.run(context)
            context.update(decision_out)
            log_step("TradeDecisionAgent", decision_out)

            # Check if a trade was even proposed
            if not context.get("trade_proposal"):
                return {
                    "status": "HOLD",
                    "reason": "No trade proposed by TradeDecisionAgent",
                    "trace_id": trace_id,
                    "trace": trace
                }

            # 5. Risk Management (Risk)
            # Inject real portfolio state for Risk Check
            from app.core.database import SessionLocal
            from app.models.portfolio import Portfolio
            db = SessionLocal()
            try:
                portfolio = db.query(Portfolio).filter(Portfolio.user_id == context.get("user_id")).first()
                if portfolio:
                    context["portfolio"] = {
                        "cash_balance": portfolio.cash_balance,
                        "daily_loss": 0.0 # Placeholder for now
                    }
            finally:
                db.close()

            risk_out = await self.risk_management.run(context)
            context.update(risk_out)
            log_step("RiskManagementAgent", risk_out)

            # CRITICAL: STOP IF RISK REJECTS
            risk_assessment = context.get("risk_assessment", {})
            if not risk_assessment.get("approved"):
                if risk_assessment.get("reason") == "Insufficient cash balance.":
                    return {
                        "status": "INSUFFICIENT_FUNDS",
                        "reason": "Insufficient cash balance.",
                        "trace_id": trace_id,
                        "risk_score": risk_assessment.get("risk_score"),
                        "required_cash": risk_assessment.get("required_cash"),
                        "trace": trace
                    }
                return {
                    "status": "REJECTED",
                    "reason": f"Risk Veto: {risk_assessment.get('reason')}",
                    "trace_id": trace_id,
                    "risk_score": risk_assessment.get("risk_score"),
                    "trace": trace
                }

            # 5.1 Manual Approval Gate for High-Value Trades
            proposal = context.get("trade_proposal", {})
            approval_id = context.get("approval_id") or proposal.get("approval_id")
            if approval_id:
                from app.core.database import SessionLocal
                from app.models.trade_approval import TradeApproval
                db = SessionLocal()
                try:
                    approval = db.query(TradeApproval).filter(TradeApproval.id == approval_id).first()
                    if not approval or approval.status != "APPROVED":
                        return {
                            "status": "PENDING_APPROVAL",
                            "reason": "Awaiting manual approval",
                            "trace_id": trace_id,
                            "trace": trace
                        }
                finally:
                    db.close()
            else:
                approval_threshold = context.get("approval_threshold", settings.HIGH_VALUE_TRADE_THRESHOLD)
                estimated_total = proposal.get("estimated_total", 0)
                if estimated_total >= approval_threshold:
                    from app.core.database import SessionLocal
                    from app.models.trade_approval import TradeApproval
                    import json
                    db = SessionLocal()
                    try:
                        approval = TradeApproval(
                            user_id=context.get("user_id"),
                            status="PENDING",
                            trade_payload=json.dumps(proposal),
                            reason="High-value trade requires manual approval"
                        )
                        db.add(approval)
                        db.commit()
                        db.refresh(approval)
                    finally:
                        db.close()
                    return {
                        "status": "PENDING_APPROVAL",
                        "reason": "Manual approval required for high-value trade",
                        "trace_id": trace_id,
                        "approval_id": approval.id,
                        "trace": trace
                    }

            # 6. Execution (Execution)
            # Enforce mode inside ExecutionAgent, but we pass it effectively via context
            execution_out = await self.execution.run(context)
            context.update(execution_out)
            log_step("ExecutionAgent", execution_out)

            # 7. Reporting (Reporting/Audit)
            report_out = await self.reporting.run(context)
            context.update(report_out)
            log_step("ReportingAgent", report_out)

            return {
                "status": "EXECUTED",
                "reason": "Trade executed successfully",
                "trace_id": trace_id,
                "execution_result": context.get("execution_result"),
                "trace": trace
            }

        except Exception as e:
            # Fallback for unexpected failures
            return {
                "status": "ERROR",
                "reason": str(e),
                "trace_id": trace_id,
                "trace": trace
            }
