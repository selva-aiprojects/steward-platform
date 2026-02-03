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
    print("🧹 Cleaning up existing data (Full Reset)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("🌱 Seeding Roles and Users...")
        
        # 1. Special Roles
        # Admin
        admin = User(
            id=999,
            full_name="Super Admin",
            email="admin@stocksteward.ai",
            hashed_password=get_password_hash("admin123"),
            is_superuser=True,
            risk_tolerance="LOW"
        )
        db.add(admin)
        
        # Auditor
        auditor = User(
            id=888,
            full_name="Compliance Auditor",
            email="audit@stocksteward.ai",
            hashed_password=get_password_hash("audit123"),
            risk_tolerance="LOW"
        )
        db.add(auditor)
        
        # Business Owner
        owner = User(
            id=777,
            full_name="Business Owner",
            email="owner@stocksteward.ai",
            hashed_password=get_password_hash("owner123"),
            risk_tolerance="MODERATE"
        )
        db.add(owner)
        db.flush()

        # 2. Synthetic Trade Users (10 users)
        traders_data = [
            {"id": 1, "name": "Alexander Pierce", "email": "alex@stocksteward.ai", "risk": "MODERATE", "capital": 500000},
            {"id": 2, "name": "Sarah Connor", "email": "sarah.c@sky.net", "risk": "HIGH", "capital": 1200000},
            {"id": 3, "name": "Tony Stark", "email": "tony@starkintl.ai", "risk": "AGGRESSIVE", "capital": 5000000},
            {"id": 4, "name": "Emily Blunt", "email": "emily@example.com", "risk": "MODERATE", "capital": 800000},
            {"id": 5, "name": "James Bond", "email": "007@mi6.gov.uk", "risk": "HIGH", "capital": 2500000},
            {"id": 6, "name": "Wanda Maximoff", "email": "wanda@avengers.org", "risk": "AGGRESSIVE", "capital": 1500000},
            {"id": 7, "name": "Peter Parker", "email": "peter.p@dailybugle.com", "risk": "LOW", "capital": 300000},
            {"id": 8, "name": "Diana Prince", "email": "diana@themyscira.gov", "risk": "MODERATE", "capital": 4000000},
            {"id": 9, "name": "Clark Kent", "email": "clark@dailyplanet.com", "risk": "LOW", "capital": 600000},
            {"id": 10, "name": "Bruce Banner", "email": "bruce.b@gamma.edu", "risk": "HIGH", "capital": 2000000},
        ]

        symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK']
        
        for t in traders_data:
            user = User(
                id=t["id"],
                full_name=t["name"],
                email=t["email"],
                hashed_password=get_password_hash("trader123"),
                risk_tolerance=t["risk"],
                trading_mode="AUTO" if random.random() > 0.3 else "MANUAL"
            )
            db.add(user)
            db.flush()

            # Fund Addition Workflow: Initial Deposit
            deposit_amount = t["capital"]
            portfolio = Portfolio(
                user_id=user.id,
                name=f"{t['name']}'s Primary Portfolio",
                cash_balance=deposit_amount,
                invested_amount=0.0,
                win_rate=round(random.uniform(55, 85), 1)
            )
            db.add(portfolio)
            db.flush()

            # Log Fund Addition
            activity = Activity(
                user_id=user.id,
                activity_type="FUND_DEPOSIT",
                description=f"Initial capital injection of ₹{deposit_amount:,} approved by system."
            )
            db.add(activity)

            # 3. Seed Holdings and Trades (Synthetic History)
            num_trades = random.randint(15, 25)
            invested_so_far = 0
            
            for _ in range(num_trades):
                symbol = random.choice(symbols)
                action = random.choice(['BUY', 'SELL'])
                qty = random.randint(10, 100)
                price = round(random.uniform(500, 3500), 2)
                
                # Simple logic to simulate past trades
                trade = Trade(
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    action=action,
                    quantity=qty,
                    price=price,
                    status="EXECUTED",
                    execution_mode="PAPER_TRADING",
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30), hours=random.randint(1, 23)),
                    risk_score=round(random.uniform(0.1, 0.9), 2),
                    pnl=f"{random.choice(['+', '-'])}{round(random.uniform(0, 5), 2)}%",
                    decision_logic=f"Synthetic trade generated for {t['name']} based on {t['risk']} profile.",
                    market_behavior="Simulated market volatility."
                )
                db.add(trade)

            # Seed some active holdings
            for symbol in random.sample(symbols, k=3):
                qty = random.randint(5, 50)
                avg_p = round(random.uniform(500, 3500), 2)
                curr_p = avg_p * random.uniform(0.9, 1.1)
                h_pnl = (curr_p - avg_p) * qty
                h_pnl_pct = ((curr_p / avg_p) - 1) * 100
                
                holding = Holding(
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    quantity=qty,
                    avg_price=avg_p,
                    current_price=curr_p,
                    pnl=h_pnl,
                    pnl_pct=h_pnl_pct
                )
                db.add(holding)
                invested_so_far += (qty * avg_p)

            # Update portfolio summary
            portfolio.invested_amount = invested_so_far
            portfolio.cash_balance -= invested_so_far
            
            # Watchlist
            for symbol in random.sample(symbols, k=4):
                wi = WatchlistItem(
                    user_id=user.id,
                    symbol=symbol
                )
                db.add(wi)

        # 4. Global Projections
        projections_data = [
            { "ticker": 'RELIANCE', "move": '+4.2%', "action": 'BUY', "logic": 'Strong support at 2900 with volume spike.' },
            { "ticker": 'TCS', "move": '+2.5%', "action": 'ACCUMULATE', "logic": 'Steady recovery post-quarterly results.' },
            { "ticker": 'HDFCBANK', "move": '-1.8%', "action": 'HOLD', "logic": 'Short-term consolidation phase detected.' },
            { "ticker": 'INFY', "move": '+5.1%', "action": 'BUY', "logic": 'Breakout expected on AI-infrastructure growth.' },
            { "ticker": 'ICICIBANK', "move": '+3.0%', "action": 'BUY', "logic": 'Banking index rotation favor.' },
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
        print(f"✅ Database reset and seeded with {len(traders_data)} users and historical data!")
        
    except Exception as e:
        print(f"❌ Error during reset and seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()
