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
        from app.core.database import SessionLocal
        from app.models.user import User
        from app.models.portfolio import Portfolio
        
        user_id = context.get("user_id", 1) # Default to 1 for demo
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                # Fallback to default if not found
                return {
                    "user_profile": {
                        "id": user_id,
                        "risk_tolerance": "MODERATE",
                        "trading_mode": "AUTO",
                        "max_drawdown_limit": 0.10,
                        "allowed_sectors": "ALL",
                        "trading_suspended": False,
                        "approval_threshold": None,
                        "confidence_threshold": None
                    }
                }
            
            portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
            portfolio_id = portfolio.id if portfolio else None

            return {
                "user_profile": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "risk_tolerance": user.risk_tolerance,
                    "trading_mode": user.trading_mode,
                    "portfolio_id": portfolio_id,
                    "max_drawdown_limit": 0.05 if user.risk_tolerance == "LOW" else 0.15,
                    "allowed_sectors": user.allowed_sectors,
                    "trading_suspended": user.trading_suspended,
                    "approval_threshold": user.approval_threshold,
                    "confidence_threshold": user.confidence_threshold
                }
            }
        finally:
            db.close()
