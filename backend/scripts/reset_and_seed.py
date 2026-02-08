import sys
import os
import random
from datetime import datetime, timedelta

# Add backend folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.portfolio import Portfolio, Holding
from app.models.trade import Trade
from app.models.strategy import Strategy
from app.models.projection import Projection
from app.models.activity import Activity
from app.models.audit_log import AuditLog
from app.models.watchlist import WatchlistItem
from app.core.security import get_password_hash

def reset_and_seed():
    print("Cleaning up existing data (Full Reset)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding Roles and Users...")

        # 1. Special Roles
        # Admin
        admin = User(
            id=999,
            full_name="Super Admin",
            email="admin@stocksteward.ai",
            hashed_password=get_password_hash("admin123"),
            is_superuser=True,
            role="SUPERADMIN",
            risk_tolerance="LOW"
        )
        db.add(admin)

        # Auditor
        auditor = User(
            id=888,
            full_name="Compliance Auditor",
            email="auditor@stocksteward.ai",  # Fixed: was "audit@stocksteward.ai", should be "auditor@stocksteward.ai"
            hashed_password=get_password_hash("audit123"),
            risk_tolerance="LOW",
            role="AUDITOR"
        )
        db.add(auditor)

        # Business Owner
        owner = User(
            id=777,
            full_name="Business Owner",
            email="owner@stocksteward.ai",
            hashed_password=get_password_hash("owner123"),
            risk_tolerance="MODERATE",
            role="BUSINESS_OWNER"
        )
        db.add(owner)
        db.flush()

        # 2. Demo Trade Users (5 users) - INR 10,000 invested with a few equities
        traders_data = [
            {"id": 1, "name": "Alexander Pierce", "email": "alex@stocksteward.ai", "risk": "MODERATE", "capital": 10000},
            {"id": 2, "name": "Sarah Connor", "email": "sarah.c@sky.net", "risk": "HIGH", "capital": 10000},
            {"id": 3, "name": "Tony Stark", "email": "tony@starkintl.ai", "risk": "AGGRESSIVE", "capital": 10000},
            {"id": 4, "name": "Bruce Wayne", "email": "bruce@waynecorp.com", "risk": "LOW", "capital": 10000},
            {"id": 5, "name": "Natasha Romanoff", "email": "nat@shield.gov", "risk": "MODERATE", "capital": 10000},
        ]

        holdings_seed = [
            {"symbol": "RELIANCE", "qty": 1, "price": 2500.0},
            {"symbol": "TCS", "qty": 1, "price": 3500.0},
            {"symbol": "HDFCBANK", "qty": 5, "price": 800.0},
        ]

        for t in traders_data:
            user = User(
                id=t["id"],
                full_name=t["name"],
                email=t["email"],
                hashed_password=get_password_hash("trader123"),
                risk_tolerance=t["risk"],
                trading_mode="AUTO" if random.random() > 0.3 else "MANUAL",
                role="TRADER"
            )
            db.add(user)
            db.flush()

            # Fund Addition Workflow: Initial Deposit
            deposit_amount = t["capital"]
            portfolio = Portfolio(
                user_id=user.id,
                name=f"{t['name']}'s Primary Portfolio",
                cash_balance=0.0,
                invested_amount=deposit_amount,
                win_rate=round(random.uniform(55, 85), 1)
            )
            db.add(portfolio)
            db.flush()

            # Log Fund Addition
            activity = Activity(
                user_id=user.id,
                activity_type="FUND_DEPOSIT",
                description=f"Initial capital injection of INR {deposit_amount:,} approved by system."
            )
            db.add(activity)

            # 3. Seed Holdings and Trades (Small demo history)
            for h in holdings_seed:
                holding = Holding(
                    portfolio_id=portfolio.id,
                    symbol=h["symbol"],
                    quantity=h["qty"],
                    avg_price=h["price"],
                    current_price=h["price"],
                    pnl=0.0,
                    pnl_pct=0.0
                )
                db.add(holding)

            trades_seed = [
                {"symbol": "RELIANCE", "action": "BUY", "qty": 1, "price": 2500.0, "pnl": "+1.2%"},
                {"symbol": "TCS", "action": "BUY", "qty": 1, "price": 3500.0, "pnl": "+0.8%"},
                {"symbol": "HDFCBANK", "action": "BUY", "qty": 5, "price": 800.0, "pnl": "+0.5%"},
            ]
            for entry in trades_seed:
                trade = Trade(
                    portfolio_id=portfolio.id,
                    symbol=entry["symbol"],
                    action=entry["action"],
                    quantity=entry["qty"],
                    price=entry["price"],
                    status="EXECUTED",
                    execution_mode="PAPER_TRADING",
                    timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                    risk_score=0.2,
                    pnl=entry["pnl"],
                    decision_logic=f"Seeded demo trade for {t['name']}.",
                    market_behavior="Seeded demo market behavior."
                )
                db.add(trade)

            # Watchlist
            for h in holdings_seed:
                wi = WatchlistItem(
                    user_id=user.id,
                    symbol=h["symbol"],
                    current_price=h["price"],
                    change="0.0%"
                )
                db.add(wi)

        # 4. Global Projections
        projections_data = [
            {"ticker": "RELIANCE", "move": "+4.2%", "action": "BUY", "logic": "Strong support at 2900 with volume spike."},
            {"ticker": "TCS", "move": "+2.5%", "action": "ACCUMULATE", "logic": "Steady recovery post-quarterly results."},
            {"ticker": "HDFCBANK", "move": "-1.8%", "action": "HOLD", "logic": "Short-term consolidation phase detected."},
            {"ticker": "INFY", "move": "+5.1%", "action": "BUY", "logic": "Breakout expected on AI-infrastructure growth."},
            {"ticker": "ICICIBANK", "move": "+3.0%", "action": "BUY", "logic": "Banking index rotation favor."},
        ]
        for p in projections_data:
            proj = Projection(
                ticker=p["ticker"],
                move_prediction=p["move"],
                action=p["action"],
                logic=p["logic"]
            )
            db.add(proj)

        db.commit()
        print(f"Database reset and seeded with {len(traders_data)} users and historical data!")

    except Exception as e:
        print(f"Error during reset and seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()
