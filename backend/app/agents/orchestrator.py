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
        context["execution_mode"] = settings.EXECUTION_MODE
        
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
            risk_out = await self.risk_management.run(context)
            context.update(risk_out)
            log_step("RiskManagementAgent", risk_out)

            # CRITICAL: STOP IF RISK REJECTS
            risk_assessment = context.get("risk_assessment", {})
            if not risk_assessment.get("approved"):
                return {
                    "status": "REJECTED",
                    "reason": f"Risk Veto: {risk_assessment.get('reason')}",
                    "trace_id": trace_id,
                    "risk_score": risk_assessment.get("risk_score"),
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
