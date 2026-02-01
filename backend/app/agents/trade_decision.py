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
        
        if signal.get("signal") == "BUY":
            # Simple sizing logic
            quantity = 10 # Placeholder
            
            return {
                "trade_proposal": {
                    "action": "BUY",
                    "symbol": market_data.get("symbol"),
                    "quantity": quantity,
                    "price": current_price,
                    "estimated_total": quantity * current_price
                }
            }
            
        return {"trade_proposal": None}
