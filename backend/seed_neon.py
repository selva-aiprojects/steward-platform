import os
import sys
import random
from datetime import datetime, timedelta

# Add the current directory (backend) to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.user import User
from app.models.portfolio import Portfolio, Holding
from app.models.trade import Trade
from app.models.watchlist import WatchlistItem
from app.models.strategy import Strategy
from app.models.projection import Projection
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash

def seed_neon_data():
    """
    Seed the Neon database with realistic demo data
    """
    print("Recreating database tables in Neon...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding Neon Demo Data...")
        
        # Create demo users with different roles
        demo_users = [
            {
                "id": 1,
                "full_name": "Alexander Pierce",
                "email": "alex@stocksteward.ai",
                "role": "TRADER",
                "risk_tolerance": "MODERATE"
            },
            {
                "id": 999,
                "full_name": "Super Admin",
                "email": "admin@stocksteward.ai",
                "role": "SUPERADMIN",
                "risk_tolerance": "LOW"
            },
            {
                "id": 777,
                "full_name": "Business Owner",
                "email": "owner@stocksteward.ai",
                "role": "BUSINESS_OWNER",
                "risk_tolerance": "MODERATE"
            }
        ]
        
        created_users = []
        for user_data in demo_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                print(f"User {user_data['email']} already exists, using existing...")
                created_users.append(existing_user)
                continue
                
            # Create new user
            user = User(
                id=user_data["id"],
                full_name=user_data["full_name"],
                email=user_data["email"],
                hashed_password=get_password_hash("admin123" if user_data["role"] == "SUPERADMIN" else "trader123"),
                role=user_data["role"],
                risk_tolerance=user_data["risk_tolerance"],
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users.append(user)
            print(f"Created user: {user_data['email']}")
        
        # Create portfolios
        for user in created_users:
            if user.role != "TRADER" and user.role != "SUPERADMIN":
                continue
                
            existing_portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
            if existing_portfolio:
                print(f"Portfolio for user {user.email} already exists...")
                continue
                
            portfolio = Portfolio(
                user_id=user.id,
                name=f"{user.full_name}'s Main Portfolio",
                cash_balance=50000.0,
                invested_amount=25000.0,
                win_rate=65.0
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
            print(f"Created portfolio for {user.email}")
            
            # Seed Holdings
            holdings_data = [
                {"symbol": "RELIANCE", "qty": 5, "price": 2987.50},
                {"symbol": "TCS", "qty": 3, "price": 3820.00},
                {"symbol": "INFY", "qty": 10, "price": 1540.00}
            ]
            for h in holdings_data:
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
                
                wl_item = WatchlistItem(
                    user_id=user.id,
                    symbol=h["symbol"],
                    current_price=h["price"],
                    change="+1.2%"
                )
                db.add(wl_item)

            # Strategies
            strats = [
                {"name": 'Llama-3 Trend Scalper', "symbol": 'RELIANCE', "status": 'RUNNING', "pnl": '+4.2%'},
                {"name": 'MACD Mean Reversion', "symbol": 'TCS', "status": 'PAUSED', "pnl": '-1.1%'},
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

        # Projections
        projections_data = [
            { "ticker": 'RELIANCE', "move": '+3.8%', "action": 'ACCUMULATE', "logic": 'Post-earnings momentum continuation' },
            { "ticker": 'INFY', "move": '-1.2%', "action": 'TRIM', "logic": 'Resistance at 1700 with volume decay' },
        ]
        for p in projections_data:
            existing = db.query(Projection).filter(Projection.ticker == p["ticker"]).first()
            if not existing:
                proj = Projection(
                    ticker=p["ticker"],
                    move_prediction=p["move"],
                    action=p["action"],
                    logic=p["logic"]
                )
                db.add(proj)

        db.commit()
        print("Neon Database Seeded Successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_neon_data()
