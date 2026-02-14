import sys
import os

# Add the project root and backend folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from sqlalchemy import text
from app.models.user import User
from app.models.portfolio import Portfolio, Holding
from app.models.watchlist import WatchlistItem
from app.models.trade import Trade
from app.models.strategy import Strategy
from app.models.projection import Projection
from app.models.social_sentiment import SocialSentiment
from app.models.activity import Activity
from app.models.audit_log import AuditLog
from app.models.kyc import KYCApplication
from app.models.optimization import PortfolioOptimizationResult, StrategyOptimizationResult
from app.models.trade_approval import TradeApproval
from app.models.ticket import Ticket, TicketMessage
from datetime import datetime, timedelta

def seed_db():
    print("Recreating database tables...")
    # Drop all tables with cascade to handle foreign key constraints
    with engine.connect() as conn:
        # Execute raw SQL to drop all tables with CASCADE
        conn.execute(text("DROP SCHEMA IF EXISTS algo CASCADE"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS algo"))
        conn.execute(text("SET search_path TO algo, public"))
        conn.commit()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding Master Demo Data...")
        
        # 1. Users & Portfolios
        users_data = [
            {"id": 1, "name": "Alexander Pierce", "email": "alex@stocksteward.ai", "used": 10000, "unused": 0, "risk": "MODERATE", "win_rate": 68.0},
            {"id": 2, "name": "Sarah Connor", "email": "sarah.c@sky.net", "used": 10000, "unused": 0, "risk": "HIGH", "win_rate": 74.0},
            {"id": 3, "name": "Tony Stark", "email": "tony@starkintl.ai", "used": 10000, "unused": 0, "risk": "AGGRESSIVE", "win_rate": 81.0},
            {"id": 4, "name": "Bruce Wayne", "email": "bruce@waynecorp.com", "used": 10000, "unused": 0, "risk": "LOW", "win_rate": 55.0},
            {"id": 5, "name": "Natasha Romanoff", "email": "nat@shield.gov", "used": 10000, "unused": 0, "risk": "MODERATE", "win_rate": 62.0},
        ]

        # Add Superadmin explicitly (ID 999)
        from app.core.security import get_password_hash
        admin = User(id=999, full_name="Super Admin", email="admin@stocksteward.ai", hashed_password=get_password_hash("admin123"), risk_tolerance="LOW", is_active=True, role="SUPERADMIN")
        db.add(admin)
        db.flush()

        owner = User(
            id=777,
            full_name="Business Owner",
            email="owner@stocksteward.ai",
            hashed_password=get_password_hash("owner123"),
            risk_tolerance="MODERATE",
            is_active=True,
            role="BUSINESS_OWNER"
        )
        db.add(owner)

        auditor = User(
            id=888,
            full_name="Compliance Auditor",
            email="auditor@stocksteward.ai",  # Fixed: was "audit@stocksteward.ai", should be "auditor@stocksteward.ai"
            hashed_password=get_password_hash("audit123"),
            risk_tolerance="LOW",
            is_active=True,
            role="AUDITOR"
        )
        db.add(auditor)

        for u in users_data:
            user = User(
                id=u["id"],
                full_name=u["name"],
                email=u["email"],
                hashed_password=get_password_hash("trader123"),
                risk_tolerance=u["risk"],
                is_active=True,
                role="TRADER"
            )
            db.add(user)
            db.flush() 
            if u["name"] == "Alexander Pierce":
                main_user_id = user.id

            portfolio = Portfolio(
                user_id=user.id,
                name=f"{u['name']}'s Main Portfolio",
                invested_amount=u["used"],
                cash_balance=u["unused"],
                win_rate=u["win_rate"]
            )
            db.add(portfolio)
            db.flush()

            # Seed Holdings (INR 10,000 invested across 3 equities)
            holdings_seed = [
                {"symbol": "RELIANCE", "qty": 1, "price": 0.0},  # Will be updated with live data
                {"symbol": "TCS", "qty": 1, "price": 0.0},      # Will be updated with live data
                {"symbol": "HDFCBANK", "qty": 5, "price": 0.0},  # Will be updated with live data
            ]
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

                wi = WatchlistItem(
                    user_id=user.id,
                    symbol=h["symbol"],
                    current_price=h["price"],
                    change="0.0%"
                )
                db.add(wi)

            # 2. Strategies (for the Trading Hub)
            if u["name"] == "Alexander Pierce":
                strats = [
                    {"name": 'Llama-3 Trend Scalper', "symbol": 'RELIANCE', "status": 'RUNNING', "pnl": '+4.2%'},
                    {"name": 'MACD Mean Reversion', "symbol": 'TCS', "status": 'PAUSED', "pnl": '-1.1%'},
                    {"name": 'Sentiment Arbitrage', "symbol": 'HDFCBANK', "status": 'IDLE', "pnl": '0.0%'},
                ]
                for s in strats:
                    strategy = Strategy(
                        portfolio_id=portfolio.id,
                        name=s["name"],
                        symbol=s["symbol"],
                        status=s["status"],
                        pnl=s["pnl"],
                        drawdown=1.2,
                        execution_mode="PAPER_TRADING"
                    )
                    db.add(strategy)

                # 3. Intelligence Journal (Trades)
                journal_entries = [
                    { 
                        "ticker": 'RELIANCE', 
                        "action": 'BUY', 
                        "price": 2987.10, 
                        "behavior": 'Breakout above V-WAP with high relative volume on 5-min candle.',
                        "decision": 'Algo detected institutional accumulation. Leveraged 1.2x on high-confidence breakout signal.',
                        "pnl": '+2.41%',
                        "time": datetime.utcnow() - timedelta(hours=4)
                    },
                    { 
                        "ticker": 'TCS', 
                        "action": 'SELL', 
                        "price": 3450.50, 
                        "behavior": 'Double top formation at resistance. RSI showing bearish divergence.',
                        "decision": 'Risk engine triggered hard exit to preserve alpha. Sentiment index dropped to 32/100.',
                        "pnl": '+1.10%',
                        "time": datetime.utcnow() - timedelta(hours=2)
                    },
                    { 
                        "ticker": 'INFY', 
                        "action": 'HOLD', 
                        "price": 1670.90, 
                        "behavior": 'Sideways consolidation. No clear direction in order flow.',
                        "decision": 'Strategy "Trend Follower" stayed neutral to avoid wash-trades during low volatility.',
                        "pnl": '0.00%',
                        "time": datetime.utcnow() - timedelta(minutes=30)
                    },
                ]
                for entry in journal_entries:
                    trade = Trade(
                        portfolio_id=portfolio.id,
                        symbol=entry["ticker"],
                        action=entry["action"],
                        quantity=100,
                        price=entry["price"],
                        status="EXECUTED",
                        execution_mode="PAPER_TRADING",
                        timestamp=entry["time"],
                        risk_score=0.8,
                        pnl=entry["pnl"],
                        decision_logic=entry["decision"],
                        market_behavior=entry["behavior"]
                    )
                    db.add(trade)

        # 4. Projections
        projections_data = [
            { "ticker": 'RELIANCE', "move": '+3.8%', "action": 'ACCUMULATE', "logic": 'Post-earnings momentum continuation' },
            { "ticker": 'INFY', "move": '-1.2%', "action": 'TRIM', "logic": 'Resistance at 1700 with volume decay' },
            { "ticker": 'TCS', "move": '+5.4%', "action": 'BUY', "logic": 'Cloud Deal rollout hype cycle' },
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
        print("Portal Demo Data Seeded Successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
