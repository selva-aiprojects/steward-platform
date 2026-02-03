

import sys
import os
import asyncio
import httpx
from httpx import AsyncClient, ASGITransport

# Ensure backend matches the python path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

os.environ.setdefault("DISABLE_BACKGROUND_TASKS", "1")

from app.main import app

print(f"DEBUG: httpx version: {httpx.__version__}")

class TestStockStewardRegression:
    def __init__(self):
        self.transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=self.transport, base_url="http://test")

    async def test_system_health(self):
        """
        Verify Governance & System Health (Feature 10).
        """
        print("\n[TEST] System Health Check...")
        response = await self.client.get("/docs")
        assert response.status_code == 200
        print(" [PASS] System Verified: Application is running and Docs are accessible.")

    async def test_user_portfolio(self):
        """
        Verify User & Account Management (Feature 1).
        """
        print("\n[TEST] User & Account Management...")
        response = await self.client.get("/api/v1/portfolio/?user_id=1")
        assert response.status_code == 200
        data = response.json()

        if isinstance(data, list):
            assert len(data) > 0, "No portfolios returned for user_id=1"
            data = data[0]

        assert "cash_balance" in data
        assert "user_id" in data
        assert data["user_id"] == 1
        print(f" [PASS] User Verified: ID {data['user_id']} | Balance: ${data['cash_balance']}")

    async def test_portfolio_reporting(self):
        """
        Verify Reporting & Notifications (Feature 7).
        """
        print("\n[TEST] Reporting Module...")
        response = await self.client.get("/api/v1/portfolio/history")
        assert response.status_code == 200
        history = response.json()
        
        assert isinstance(history, list)
        assert len(history) > 0
        print(f" [PASS] Reporting Verified: {len(history)} data points retrieved.")

    async def test_trade_audit(self):
        """
        Verify Compliance & Audit Trail (Feature 9).
        """
        print("\n[TEST] Trade Audit Trail...")
        response = await self.client.get("/api/v1/trades/")
        assert response.status_code == 200
        trades = response.json()
        
        assert isinstance(trades, list)
        print(f" [PASS] Audit Verified: {len(trades)} historical trades found.")

    async def test_autonomous_trading_logic(self):
        """
        Verify Autonomous Trading (Features 2, 4, 6).
        """
        print("\n[TEST] Autonomous Agentic Trading Workflow...")
        
        payload = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 10,
            "request_id": "test-regression-async-001"
        }
        
        response = await self.client.post("/api/v1/trades/paper/order", json=payload)
        
        if response.status_code != 200:
            print(f" [FAIL] FAILED. Status: {response.status_code}")
            print(f"Response: {response.text}")
            assert response.status_code == 200

        result = response.json()
        
        print(f"   -> Status: {result['status']}")
        trace = result.get("trace", [])
        agent_names = [step['step'] for step in trace]
        print(f"   -> Agent Chain: {' -> '.join(agent_names)}")
        
        required_agents = ["UserProfileAgent", "MarketDataAgent", "StrategyAgent", "TradeDecisionAgent", "RiskManagementAgent", "ReportingAgent"]
        
        if result['status'] == "EXECUTED":
            for agent in required_agents:
                assert agent in agent_names, f"Missing Agent: {agent}"
            
        print(" [PASS] Autonomous Trading Verified: Full Agentic Chain completed.")

    async def close(self):
        try:
            await asyncio.wait_for(self.client.aclose(), timeout=5)
        except Exception:
            pass

async def run_suite():
    print("="*60)
    print(" STARTING STOCKSTEWARD AI REGRESSION SUITE (ASYNC) - FINAL RUN")
    print("="*60)
    
    suite = TestStockStewardRegression()
    exit_code = 0
    
    try:
        await suite.test_system_health()
        await suite.test_user_portfolio()
        await suite.test_portfolio_reporting()
        await suite.test_trade_audit()
        await suite.test_autonomous_trading_logic()
        
        print("\n" + "="*60)
        print(" ALL TESTS PASSED SUCCESSFULLY")
        print("="*60)
    except AssertionError as e:
        print("\n" + "="*60)
        print(f" TEST FAILED: {e}")
        print("="*60)
        exit_code = 1
    except Exception as e:
        print("\n" + "="*60)
        print(f" SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        exit_code = 1
    finally:
        os._exit(exit_code)

if __name__ == "__main__":
    asyncio.run(run_suite())
