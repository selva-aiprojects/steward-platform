from typing import Any, Dict
from app.agents.base import BaseAgent

class TradeDecisionAgent(BaseAgent):
    """
    Responsible for proposing a concrete trade action.
    
    Responsibilities:
    - Synthesize User Profile (Risk Tolerance) + Strategy Signal.
    - Determine sizing (quantity).
    - Formulate a specific Trade Proposal.
    """
    
    def __init__(self):
        super().__init__(name="TradeDecisionAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        user_profile = context.get("user_profile", {})
        signal = context.get("strategy_signal", {})
        market_data = context.get("market_data", {})
        
        current_price = market_data.get("current_price", 0)
        risk_tolerance = user_profile.get("risk_tolerance", "MODERATE")
        
        # Smart Sizing Logic
        risk_multipliers = {
            "LOW": 10,
            "MODERATE": 50,
            "HIGH": 100,
            "AGGRESSIVE": 250
        }
        
        base_quantity = risk_multipliers.get(risk_tolerance, 50)
        
        # 1. Manual Override Priority
        manual_override = context.get("manual_override")
        if manual_override:
            action = manual_override.get("action")
            symbol = manual_override.get("symbol")
            quantity = manual_override.get("quantity")
            price = manual_override.get("price") or current_price
            
            return {
                "trade_proposal": {
                    "action": action,
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": price,
                    "estimated_total": quantity * price,
                    "logic": "MANUAL_OVERRIDE: User-directed execution."
                }
            }

        # 2. Automated Strategy Logic
        if signal.get("signal") in ["BUY", "SELL"]:
            action = signal.get("signal")
            quantity = base_quantity
            
            return {
                "trade_proposal": {
                    "action": action,
                    "symbol": market_data.get("symbol"),
                    "quantity": quantity,
                    "price": current_price,
                    "estimated_total": quantity * current_price,
                    "logic": f"Execution for {risk_tolerance} profile based on {signal.get('strategy_used')} signal."
                }
            }
            
        return {"trade_proposal": None}
