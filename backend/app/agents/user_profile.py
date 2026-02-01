from typing import Any, Dict
from app.agents.base import BaseAgent

class UserProfileAgent(BaseAgent):
    """
    Responsible for fetching and analyzing User Identity and Preferences.
    
    Responsibilities:
    - Retrieve User Risk Tolerance (Aggressive, Moderate, Conservative).
    - Retrieve User Capital limits.
    - Retrieve User Goals.
    """
    
    def __init__(self):
        super().__init__(name="UserProfileAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get("user_id")
        
        # Placeholder logic: Fetch from DB later
        # For now, return a default profile
        return {
            "user_profile": {
                "id": user_id,
                "risk_tolerance": "MODERATE",
                "max_drawdown_limit": 0.10  # 10%
            }
        }
