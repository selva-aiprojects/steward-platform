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
        
        # Initialize the Agentic Workflow
        orchestrator = OrchestratorAgent()
        
        # Prepare initial context
        # In a real app, we'd fetch the user_id from the authenticated session
        context = {
            "request_id": trade_proposal.get("request_id"),
            "user_id": 1,  # Hardcoded for single-user dev
            "symbol": trade_proposal.get("symbol"), # passed to MarketDataAgent
            # Initial proposal data if provided manually, though Strategy usually generates it
            "manual_override": trade_proposal 
        }
        
        # Run the workflow
        result = await orchestrator.run(context)
        
        return result
