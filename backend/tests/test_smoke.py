import pytest
import httpx
import asyncio
from unittest.mock import MagicMock

BASE_URL = "http://127.0.0.1:8000/api/v1"

@pytest.mark.asyncio
async def test_health_check():
    """Verify backend is operational."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_user_retrieval():
    """Verify we can fetch the default test user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/users/1")
        assert response.status_code == 200
        assert "email" in response.json()

@pytest.mark.asyncio
async def test_manual_trade_flow():
    """Verify end-to-end manual trade execution in the DB ledger."""
    trade_data = {
        "symbol": "HDFCBANK",
        "action": "BUY",
        "quantity": 5,
        "price": 1450.0,
        "type": "MANUAL",
        "decision_logic": "Smoke Test: Manual Execution"
    }
    
    async with httpx.AsyncClient() as client:
        # Execute Trade
        response = await client.post(f"{BASE_URL}/trades/?user_id=1", json=trade_data)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "EXECUTED"
        assert "execution_result" in result
        
        # Verify Portfolio Update (Summary)
        port_response = await client.get(f"{BASE_URL}/portfolio/?user_id=1")
        assert port_response.status_code == 200
        portfolios = port_response.json()
        assert len(portfolios) > 0
        
        # Verify Audit Log Entry
        audit_response = await client.get(f"{BASE_URL}/audit/?target_user_id=1")
        assert audit_response.status_code == 200
        logs = audit_response.json()
        assert any("HDFCBANK" in log["action"] for log in logs)

@pytest.mark.asyncio
async def test_strategy_agent_mock():
    """Verify Strategy Agent logic via direct endpoint call."""
    # This might trigger a real Groq call if configured, or fallback
    # We are testing the API response structure here
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/strategies/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
