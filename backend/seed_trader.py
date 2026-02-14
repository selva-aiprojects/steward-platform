from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio, Holding
from app.models.trade import Trade
from app.models.strategy import Strategy
from app.core.auth import get_password_hash
import random
from datetime import datetime, timedelta

db = SessionLocal()
try:
    email = "trader@stocksteward.ai"
    # Case-insensitive search
    user = db.query(User).filter(User.email.ilike(email)).first()
    
    if not user:
        print(f"User {email} not found, creating...")
        try:
            user = User(
                email=email, # Force lowercase
                full_name="Trader User",
                hashed_password=get_password_hash("trader123"),
                is_active=True,
                role="TRADER",
                risk_tolerance="MODERATE",
                trading_mode="AUTO"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user ID: {user.id}")
        except Exception as e:
            db.rollback()
            print(f"Creation failed (likely race condition): {e}")
            user = db.query(User).filter(User.email.ilike(email)).first()
            if not user:
                print("Even after rollback, user not found. Bailing out.")
                exit(1)
    else:
        print(f"Found existing user ID: {user.id}")

    # Remove existing data for a clean slate
    existing_portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    if existing_portfolio:
        print("Cleaning up old portfolio/trades...")
        db.query(Trade).filter(Trade.portfolio_id == existing_portfolio.id).delete()
        db.query(Holding).filter(Holding.portfolio_id == existing_portfolio.id).delete()
        # Clean up strategies linked to this portfolio (if any)
        db.query(Strategy).filter(Strategy.portfolio_id == existing_portfolio.id).delete()
        db.delete(existing_portfolio)
        db.commit()
    
    # Create fresh Portfolio
    portfolio = Portfolio(
        user_id=user.id,
        cash_balance=500000.0,
        invested_amount=0.0,
        win_rate=65.5,
        name="Trader's Growth Vault"
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    print(f"Created Portfolio ID: {portfolio.id}")
    
    # Add Holdings
    holdings_data = [
        {"symbol": "RELIANCE", "quantity": 50, "avg_price": 2450.0, "current_price": 2500.0, "exchange": "NSE"},
        {"symbol": "TCS", "quantity": 30, "avg_price": 3200.0, "current_price": 3250.0, "exchange": "NSE"},
        {"symbol": "INFY", "quantity": 100, "avg_price": 1400.0, "current_price": 1420.0, "exchange": "NSE"},
        {"symbol": "HDFCBANK", "quantity": 75, "avg_price": 1600.0, "current_price": 1580.0, "exchange": "NSE"},
        {"symbol": "ICICIBANK", "quantity": 100, "avg_price": 950.0, "current_price": 980.0, "exchange": "NSE"}
    ]
    
    total_invested = 0
    for h in holdings_data:
        pnl_val = (h["current_price"] - h["avg_price"]) * h["quantity"]
        pnl_pct_val = ((h["current_price"] - h["avg_price"]) / h["avg_price"]) * 100.0

        holding = Holding(
            portfolio_id=portfolio.id,
            symbol=h["symbol"],
            quantity=h["quantity"],
            avg_price=h["avg_price"],
            current_price=h["current_price"],
            pnl=pnl_val,
            pnl_pct=pnl_pct_val
        )
        db.add(holding)
        total_invested += h["quantity"] * h["current_price"]
    
    portfolio.invested_amount = total_invested
    db.add(portfolio)

    # Add Trades
    trades_data = [
        {"symbol": "RELIANCE", "action": "BUY", "quantity": 50, "price": 2450.0, "pnl": 2500.0, "timestamp": datetime.utcnow() - timedelta(days=2)},
        {"symbol": "TCS", "action": "BUY", "quantity": 30, "price": 3200.0, "pnl": 1500.0, "timestamp": datetime.utcnow() - timedelta(days=1)},
        {"symbol": "INFY", "action": "BUY", "quantity": 100, "price": 1400.0, "pnl": 2000.0, "timestamp": datetime.utcnow() - timedelta(hours=4)},
        {"symbol": "TATAMOTORS", "action": "SELL", "quantity": 50, "price": 600.0, "pnl": 5000.0, "timestamp": datetime.utcnow() - timedelta(days=5)}
    ]
    
    for t in trades_data:
        trade = Trade(
            portfolio_id=portfolio.id,
            user_id=user.id,
            symbol=t["symbol"],
            action=t["action"],
            quantity=t["quantity"],
            price=t["price"],
            timestamp=t["timestamp"],
            pnl=str(t["pnl"]),
            status="EXECUTED",
            execution_mode="PAPER_TRADING",
            risk_score=0.1
        )
        db.add(trade)
    
    db.add(portfolio)

    # Adjust Strategy logic
    # Strategies are linked to Portfolio in the model
    existing_strategies = db.query(Strategy).filter(Strategy.portfolio_id == portfolio.id).count()
    if existing_strategies == 0:
        strategy = Strategy(
            portfolio_id=portfolio.id,
            name="Momentum Alpha",
            symbol="NIFTY",
            status="RUNNING",
            pnl="+5.2%",
            drawdown=1.2,
            execution_mode="PAPER_TRADING"
        )
        db.add(strategy)
    
    db.commit()
    print("Seed data for trader@stocksteward.ai populated successfully!")

except Exception as e:
    db.rollback()
    import traceback
    traceback.print_exc()
    print(f"Error seeding data: {e}")
    # exit(1) # Don't exit, let me see output
finally:
    db.close()
