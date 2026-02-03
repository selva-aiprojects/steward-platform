import asyncio
import os
from app.agents.orchestrator import OrchestratorAgent
from app.core.database import SessionLocal
from app.models.user import User

async def run_end_to_end_test():
    print("🚀 Starting End-to-End Platform Verification...")
    
    orchestrator = OrchestratorAgent()
    db = SessionLocal()
    
    try:
        # 1. Verify User Profile & Restrictions
        user = db.query(User).filter(User.id == 1).first()
        print(f"👤 Testing User: {user.full_name} (Role: {user.risk_tolerance}, Allowed: {user.allowed_sectors})")

        # 2. Test Case 1: Manual Trade for Restricted Sector
        print("\n🧪 Test Case 1: Attempting trade in RESTRICTED sector (Automobile)...")
        context_restricted = {
            "user_id": 1,
            "symbol": "TATAMOTORS", # Automobile (Restricted if user is Finance/IT)
            "manual_override": {
                "action": "BUY",
                "symbol": "TATAMOTORS",
                "quantity": 5,
                "price": 950.0
            }
        }
        
        result_restricted = await orchestrator.run(context_restricted)
        print(f"Result: {result_restricted['status']} - {result_restricted.get('reason')}")
        
        # 3. Test Case 2: Manual Trade for ALLOWED Sector
        print("\n🧪 Test Case 2: Attempting trade in ALLOWED sector (Finance)...")
        # Ensure user allowed_sectors includes Finance for this test
        user.allowed_sectors = "Finance, IT"
        db.commit()
        
        context_allowed = {
            "user_id": 1,
            "symbol": "HDFCBANK",
            "manual_override": {
                "action": "BUY",
                "symbol": "HDFCBANK",
                "quantity": 2,
                "price": 1450.0
            }
        }
        
        result_allowed = await orchestrator.run(context_allowed)
        print(f"Result: {result_allowed['status']} - {result_allowed.get('reason')}")
        if result_allowed['status'] == 'EXECUTED':
            print(f"💰 Execution Details: {result_allowed.get('execution_result', {}).get('order_id')}")

        # 4. Test Case 3: Auto Mode with Groq Intelligence
        print("\n🧪 Test Case 3: Running Auto Mode with Groq Analytics...")
        context_auto = {
            "user_id": 1,
            "symbol": "RELIANCE",
            "execution_mode": "PAPER_TRADING"
        }
        
        result_auto = await orchestrator.run(context_auto)
        print(f"Result: {result_auto['status']} - {result_auto.get('reason')}")
        
        # Print the AI Rationale
        strategy_step = next((s for s in result_auto.get('trace', []) if s['step'] == 'StrategyAgent'), {})
        rationale = strategy_step.get('output', {}).get('strategy_signal', {}).get('rationale')
        print(f"🤖 Groq Rationale: {rationale}")

    finally:
        db.close()

if __name__ == "__main__":
    # Mock environment for testing logic without real keys
    from unittest import mock
    from app.services.kite_service import kite_service
    
    # Mock Kite Quote
    kite_service.get_quote = mock.Mock(return_value={
        "last_price": 1000.0,
        "volume": 500000,
        "ohlc": {"open": 980.0, "high": 1010.0, "low": 970.0, "close": 990.0}
    })
    
    # Mock Groq (inside StrategyAgent if it was imported)
    # Since StrategyAgent imports it locally, we might need a different approach, 
    # but for logic testing, the fallback is also informative.
    
    asyncio.run(run_end_to_end_test())
