from typing import Any, Dict
from app.agents.base import BaseAgent
from app.core.config import settings

class RiskManagementAgent(BaseAgent):
    """
    Responsible for Final Gatekeeping.
    
    Responsibilities:
    - VETO POWER: Can reject any proposal.
    - Check structural validity.
    - Check capital limits (Max loss, Max position).
    - Check compliance rules.
    """
    
    def __init__(self):
        super().__init__(name="RiskManagementAgent")
        self.max_trade_value = 2000.0 # Example Limit

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates trade risk. 
        VETO POWER: Rejects if ANY rule is violated.
        """
        proposal = context.get("trade_proposal")
        user_profile = context.get("user_profile", {})
        # Assuming portfolio state is injected or mocked for now.
        # In full prod, Orchestrator would fetch this from PortfolioService.
        portfolio = context.get("portfolio", {"cash_balance": 100000.0, "daily_loss": 0.0})
        
        if not proposal:
            return {
                "risk_assessment": {
                    "approved": False,
                    "reason": "No proposal presented"
                }
            }

        # --- 1. CONFIGURATION extraction ---
        # Default to Conservative if missing
        risk_tolerance = user_profile.get("risk_tolerance", "CONSERVATIVE")
        
        # Risk Parameters based on profile
        if risk_tolerance == "AGGRESSIVE":
            max_risk_per_trade_pct = 0.02 # 2%
            max_daily_loss_pct = 0.05     # 5%
            stop_loss_pct = 0.05
            take_profit_pct = 0.15
        elif risk_tolerance == "MODERATE":
            max_risk_per_trade_pct = 0.01 # 1%
            max_daily_loss_pct = 0.03     # 3%
            stop_loss_pct = 0.03
            take_profit_pct = 0.09
        else: # CONSERVATIVE
            max_risk_per_trade_pct = 0.005 # 0.5%
            max_daily_loss_pct = 0.01      # 1%
            stop_loss_pct = 0.02
            take_profit_pct = 0.04

        # --- 2. CALCULATIONS ---
        current_cash = portfolio.get("cash_balance", 0.0)
        current_daily_loss = portfolio.get("daily_loss", 0.0)
        
        # Trade details
        price = proposal.get("price", 0.0)
        quantity = proposal.get("quantity", 0)
        estimated_total = proposal.get("estimated_total", price * quantity)
        
        # --- 3. RULE CHECKS ---
        
        rejection_reason = None
        
        # Rule A: Max Trade Value / Position Sizing check (Capital at Risk)
        # Simplified: Risking the entire trade value? Or calculating risk based on stop loss?
        # Standard approach: Risk amount = Entry - StopLoss.
        # Here we check if the nominal value exceeds a sanity limit or if potential loss exceeds % capital
        
        potential_loss_amount = estimated_total * stop_loss_pct
        max_allowed_risk_amount = current_cash * max_risk_per_trade_pct
        
        if potential_loss_amount > max_allowed_risk_amount:
            rejection_reason = (f"Position size too large. Potential loss ${potential_loss_amount:.2f} "
                                f"exceeds limit ${max_allowed_risk_amount:.2f} ({max_risk_per_trade_pct*100}%)")

        # Rule B: Daily Drawdown Limit
        # If we take this loss, do we breach daily limit? (Conservative check)
        elif (current_daily_loss + potential_loss_amount) > (current_cash * max_daily_loss_pct):
             rejection_reason = "Trade would risk breaching daily drawdown limit."
             
        # Rule C: Sanity Use of Cash
        elif estimated_total > current_cash:
            rejection_reason = "Insufficient cash balance."

        # --- 4. DECISION ---
        if rejection_reason:
            return {
                "risk_assessment": {
                    "approved": False,
                    "risk_score": 100,
                    "reason": rejection_reason,
                    "generated_at": str(context.get("trace_id"))
                }
            }

        # Calculate Mandatory Levels
        stop_loss_price = price * (1 - stop_loss_pct) if proposal.get("action") == "BUY" else price * (1 + stop_loss_pct)
        take_profit_price = price * (1 + take_profit_pct) if proposal.get("action") == "BUY" else price * (1 - take_profit_price)

        return {
            "risk_assessment": {
                "approved": True,
                "risk_score": 10, # Low risk
                "reason": "Within defined limits",
                "rules_checked": ["max_loss_per_trade", "daily_drawdown", "cash_balance"],
                "limits": {
                    "stop_loss_price": round(stop_loss_price, 2),
                    "take_profit_price": round(take_profit_price, 2),
                    "max_risk_amount": round(max_allowed_risk_amount, 2)
                }
            }
        }
