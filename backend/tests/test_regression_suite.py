import os
from pathlib import Path
import sys

import pytest
from httpx import AsyncClient, ASGITransport

DB_PATH = Path(__file__).with_name("test_regression.db")

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
from app.core.security import get_password_hash  # noqa: E402
from app.main import app  # noqa: E402


def seed_user():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 10).first()
        if not user:
            user = User(
                id=10,
                email="trader@stocksteward.ai",
                full_name="Regression Trader",
                hashed_password=get_password_hash("trader123"),
                risk_tolerance="MODERATE",
                trading_mode="AUTO",
                allowed_sectors="ALL",
                is_active=True,
                role="TRADER",
            )
            db.add(user)
            db.commit()

        portfolio = db.query(Portfolio).filter(Portfolio.user_id == 10).first()
        if not portfolio:
            portfolio = Portfolio(
                user_id=10,
                name="Regression Vault",
                cash_balance=10000.0,
                invested_amount=0.0,
                win_rate=0.0,
            )
            db.add(portfolio)
            db.commit()
    finally:
        db.close()


seed_user()


@pytest.mark.asyncio
async def test_login_success_and_failure():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        ok = await client.post("/api/v1/auth/login", json={
            "email": "trader@stocksteward.ai",
            "password": "trader123",
        })
        assert ok.status_code == 200
        data = ok.json()
        assert data["email"] == "trader@stocksteward.ai"
        assert data["role"] == "TRADER"

        bad = await client.post("/api/v1/auth/login", json={
            "email": "trader@stocksteward.ai",
            "password": "wrong",
        })
        assert bad.status_code == 401


@pytest.mark.asyncio
async def test_withdraw_funds_and_overdraft_blocked():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        ok = await client.post("/api/v1/portfolio/withdraw", json={
            "user_id": 10,
            "amount": 2000,
        })
        assert ok.status_code == 200
        data = ok.json()
        assert data["cash_balance"] == 8000.0

        bad = await client.post("/api/v1/portfolio/withdraw", json={
            "user_id": 10,
            "amount": 20000,
        })
        assert bad.status_code == 400


@pytest.mark.asyncio
async def test_user_role_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create = await client.post("/api/v1/users/", json={
            "email": "badrole@stocksteward.ai",
            "full_name": "Bad Role",
            "password": "pass123",
            "role": "ROOT",
        })
        assert create.status_code == 400

        update = await client.put("/api/v1/users/10", json={
            "role": "ROOT",
        })
        assert update.status_code == 400
