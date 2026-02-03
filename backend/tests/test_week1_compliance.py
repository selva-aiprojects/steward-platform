import os
from pathlib import Path
import sys

import pytest
from httpx import AsyncClient, ASGITransport


DB_PATH = Path(__file__).with_name("test_week1.db")

if DB_PATH.exists():
    DB_PATH.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
os.environ["APP_ENV"] = "DEV"
os.environ["ENABLE_LIVE_TRADING"] = "false"
os.environ["GLOBAL_KILL_SWITCH"] = "false"
os.environ["EXECUTION_MODE"] = "PAPER_TRADING"
os.environ["DISABLE_BACKGROUND_TASKS"] = "1"

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, engine, SessionLocal  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.portfolio import Portfolio  # noqa: E402
from app.main import app  # noqa: E402


def seed_user():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(
                id=1,
                email="admin@stocksteward.ai",
                full_name="Admin User",
                hashed_password="test",
                risk_tolerance="MODERATE",
                trading_mode="AUTO",
                allowed_sectors="ALL",
                is_active=True,
                is_superuser=True,
                role="SUPERADMIN",
            )
            db.add(user)
            db.commit()

        portfolio = db.query(Portfolio).filter(Portfolio.user_id == 1).first()
        if not portfolio:
            portfolio = Portfolio(
                user_id=1,
                name="Primary Vault",
                cash_balance=200000.0,
                invested_amount=0.0,
                win_rate=0.0,
            )
            db.add(portfolio)
            db.commit()
    finally:
        db.close()


seed_user()


@pytest.mark.asyncio
async def test_kill_switch_blocks_trade():
    from app.core.config import settings

    settings.GLOBAL_KILL_SWITCH = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/trades/paper/order", json={
            "symbol": "TCS",
            "action": "BUY",
            "quantity": 1,
            "price": 100.0,
            "user_id": 1,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "SUSPENDED"
    settings.GLOBAL_KILL_SWITCH = False


@pytest.mark.asyncio
async def test_high_value_trade_requires_approval():
    from app.core.config import settings

    settings.HIGH_VALUE_TRADE_THRESHOLD = 1.0
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/trades/paper/order", json={
            "symbol": "TCS",
            "action": "BUY",
            "quantity": 1,
            "price": 100.0,
            "user_id": 1,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "PENDING_APPROVAL"
        approval_id = data.get("approval_id")
        assert approval_id is not None

        approve = await client.post(
            f"/api/v1/approvals/{approval_id}/approve?approver_id=1",
            headers={"X-User-Id": "1", "X-User-Role": "SUPERADMIN"},
        )
        assert approve.status_code == 200
        approve_data = approve.json()
        assert approve_data["status"] == "EXECUTED"
    settings.HIGH_VALUE_TRADE_THRESHOLD = 100000.0
