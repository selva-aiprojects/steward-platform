import os
import uuid

import httpx
import pytest

BASE_API_URL = os.getenv("SMOKE_BASE_API_URL", "http://127.0.0.1:8000/api/v1")
HEALTH_URL = os.getenv("SMOKE_HEALTH_URL", "http://127.0.0.1:8000/health")
SMOKE_EMAIL = os.getenv("SMOKE_EMAIL", "admin@stocksteward.ai")
SMOKE_PASSWORD = os.getenv("SMOKE_PASSWORD", "admin123")
REQUEST_TIMEOUT = float(os.getenv("SMOKE_TIMEOUT_SEC", "20"))


async def _login_and_headers(client: httpx.AsyncClient) -> tuple[dict, int]:
    response = await client.post(
        f"{BASE_API_URL}/auth/login",
        json={"email": SMOKE_EMAIL, "password": SMOKE_PASSWORD},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    token = payload.get("access_token")
    user_id = int(payload.get("id"))
    assert token, "Missing access token in login response"
    return {"Authorization": f"Bearer {token}"}, user_id


@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(HEALTH_URL)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_user_retrieval():
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        headers, user_id = await _login_and_headers(client)
        response = await client.get(f"{BASE_API_URL}/users/{user_id}", headers=headers)
        assert response.status_code == 200, response.text
        assert "email" in response.json()


@pytest.mark.asyncio
async def test_manual_trade_flow():
    trade_data = {
        "symbol": "HDFCBANK",
        "action": "BUY",
        "quantity": 1,
        "price": 1450.0,
        "decision_logic": "Smoke Test: Manual Execution",
    }

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        headers, user_id = await _login_and_headers(client)
        idempotency_key = f"smoke-{uuid.uuid4()}"

        response = await client.post(
            f"{BASE_API_URL}/trades/paper/order",
            json={**trade_data, "user_id": user_id},
            headers={**headers, "Idempotency-Key": idempotency_key},
        )
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["status"] in {"EXECUTED", "APPROVAL_REQUIRED"}

        trades_response = await client.get(f"{BASE_API_URL}/trades/?user_id={user_id}", headers=headers)
        assert trades_response.status_code == 200, trades_response.text
        assert isinstance(trades_response.json(), list)


@pytest.mark.asyncio
async def test_strategy_endpoint_access():
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        headers, _ = await _login_and_headers(client)
        response = await client.get(f"{BASE_API_URL}/strategies/", headers=headers)
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)
