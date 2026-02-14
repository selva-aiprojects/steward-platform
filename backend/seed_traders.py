
import os
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.portfolio import Portfolio, Holding
from app.models.strategy import Strategy
from app.models.trade import Trade
from app.core.security import get_password_hash

def seed_traders():
    print("Starting process: Seeding 10 traders...")
    db = SessionLocal()
    
    try:
        # Explicitly set search path for this session
        db.execute(text("SET search_path TO algo, public"))
        db.commit()
        
        symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
            "SBIN.NS", "ITC.NS", "LT.NS", "AXISBANK.NS", "KOTAKBANK.NS"
        ]
        
        strategy_names = [
            "Momentum Alpha", "Mean Reversion Pro", "Volume Scalper", 
            "Trend Follower Elite", "Volatility Breakout", "RSI Oscillator", 
            "MACD Divergence", "Smart Money Flow", "Golden Cross", "Quant Edge"
        ]

        for i in range(1, 11):
            email = f"trader{i}@example.com"
            full_name = f"Trader {i}"
            password = "password123"
            
            print(f"[{i}/10] Processing {email}...")
            
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            if not user:
                print(f"  Creating user...")
                user = User(
                    email=email,
                    full_name=full_name,
                    hashed_password=get_password_hash(password),
                    role="TRADER",
                    is_active=True,
                    is_superuser=False
                )
                db.add(user)
                db.flush()
            else:
                print(f"  User already exists (ID: {user.id}).")

            # Portfolio Setup
            portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
            if not portfolio:
                print(f"  Creating portfolio...")
                portfolio = Portfolio(
                    user_id=user.id,
                    name="Primary Wealth Vault",
                    cash_balance=100000.0,
                    invested_amount=0.0
                )
                db.add(portfolio)
                db.flush()
            else:
                print(f"  Portfolio already exists.")
                # We update cash to 100k if instructed, but here we just ensure basic state
                portfolio.cash_balance = 100000.0
                portfolio.invested_amount = 0.0
                # Delete existing holdings/trades to have a fresh state for the seed
                db.execute(text(f"DELETE FROM holdings WHERE portfolio_id = {portfolio.id}"))
                db.execute(text(f"DELETE FROM trades WHERE portfolio_id = {portfolio.id}"))
                db.flush()

            # Strategy Setup
            strategy = db.query(Strategy).filter(Strategy.portfolio_id == portfolio.id).first()
            symbol = symbols[i-1]
            strat_name = strategy_names[i-1]
            if not strategy:
                print(f"  Creating strategy: {strat_name} ({symbol})")
                strategy = Strategy(
                    portfolio_id=portfolio.id,
                    name=strat_name,
                    symbol=symbol,
                    status="RUNNING",
                    pnl="0%",
                    drawdown=0.0,
                    execution_mode="PAPER_TRADING"
                )
                db.add(strategy)
                db.flush()
            else:
                print(f"  Strategy already exists. Updating...")
                strategy.name = strat_name
                strategy.symbol = symbol
                strategy.status = "RUNNING"
                strategy.pnl = "0%"

            # Seed some holdings and trades
            print(f"  Seeding dashboard data...")
            entry_price = round(random.uniform(1000, 3000), 2)
            quantity = random.randint(10, 20)
            invested = round(entry_price * quantity, 2)
            last_price = round(entry_price * random.uniform(1.02, 1.12), 2)
            pnl_abs = round((last_price - entry_price) * quantity, 2)
            pnl_pct = round((pnl_abs / invested) * 100 if invested else 0, 2)

            holding = Holding(
                portfolio_id=portfolio.id,
                symbol=symbol,
                quantity=quantity,
                avg_price=entry_price,
                current_price=last_price,
                pnl=pnl_abs,
                pnl_pct=pnl_pct
            )
            db.add(holding)

            # Seed Trades
            now = datetime.utcnow()
            for t_idx in range(4):
                trade = Trade(
                    user_id=user.id,
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    action="BUY" if t_idx % 2 == 0 else "SELL",
                    quantity=max(1, quantity // 2),
                    price=round(entry_price * random.uniform(0.98, 1.02), 2),
                    status="EXECUTED",
                    execution_mode="PAPER_TRADING",
                    timestamp=now - timedelta(days=t_idx+1),
                    pnl=f"{round(random.uniform(-1, 3), 2)}%"
                )
                db.add(trade)

            # Update portfolio
            portfolio.invested_amount = invested
            portfolio.cash_balance = round(100000.0 - invested, 2)
            portfolio.win_rate = round(random.uniform(50, 80), 2)
            strategy.pnl = f"+{pnl_pct}%"
            
            db.commit()
            print(f"  Done.")

        print("\nSUCCESS: 10 traders seeded successfully.")
        
    except Exception as e:
        db.rollback()
        print(f"\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_traders()
