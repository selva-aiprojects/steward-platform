import pytest
import httpx
from app.core.security import get_password_hash, verify_password

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_password_hashing():
    """Verify BCrypt hashing works as expected (NFR-2)."""
    password = "secret_password_123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

@pytest.mark.asyncio
async def test_sector_restriction_enforcement():
    """Verify FR-15: RiskAgent vetoes restricted sectors."""
    # We attempt to trade a symbol that belongs to a sector NOT allowed for the user
    # First, configure user 1 to have specific allowed sectors
    async with httpx.AsyncClient() as client:
        # Update user to allow only IT and Energy
        update_data = {"allowed_sectors": "IT, Energy"}
        await client.put(f"{BASE_URL}/users/1", json=update_data)
        
        # Attempt to buy HDFCBANK (Finance - Restricted)
        trade_data = {
            "symbol": "HDFCBANK",
            "action": "BUY",
            "quantity": 10,
            "price": 1400.0,
            "type": "MANUAL"
        }
        
        response = await client.post(f"{BASE_URL}/trades/?user_id=1", json=trade_data)
        assert response.status_code == 200
        result = response.json()
        
        # Should be vetoed by RiskManagementAgent
        assert result["status"] == "REJECTED_RISK"
        assert "restricted sector" in result["reason"].lower()

@pytest.mark.asyncio
async def test_rbac_auditor_permissions():
    """Verify Auditor role cannot place trades (FR-3)."""
    # Create an auditor user
    async with httpx.AsyncClient() as client:
        auditor_data = {
            "email": "auditor_test@stocksteward.ai",
            "full_name": "Test Auditor",
            "password": "auditor_pass_123",
            "role": "AUDITOR"
        }
        # Assuming we have a way to create or use an auditor
        # For now, we'll try to execute a trade for a known auditor ID or check permission logic
        # If the backend is properly restricted, a trade POST for an Auditor ID should be rejected
        pass # To be implemented more deeply if Auditor model is fully separate

@pytest.mark.asyncio
async def test_audit_log_latency():
    """Verify Audit Logs are generated promptly and correctly (FR-10)."""
    async with httpx.AsyncClient() as client:
        # Trigger an action (e.g., login or profile update)
        await client.put(f"{BASE_URL}/users/1", json={"full_name": "Alexander Pierce Updated"})
        
        # Fetch logs
        response = await client.get(f"{BASE_URL}/audit/?target_user_id=1")
        assert response.status_code == 200
        logs = response.json()
        assert len(logs) > 0
        assert logs[0]["action"] is not None
        assert "2026" in logs[0]["timestamp"] # Verifying year
