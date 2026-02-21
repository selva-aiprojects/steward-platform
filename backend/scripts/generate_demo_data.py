#!/usr/bin/env python3
import random
from datetime import datetime, timedelta

from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio, Holding
from app.models.strategy import Strategy
from app.models.trade import Trade
from app.core.security import get_password_hash


def _now() -> datetime:
    return datetime.utcnow()


def _random_symbol() -> str:
    universe = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
        "SBIN", "ITC", "LT", "AXISBANK", "KOTAKBANK",
        "BAJFINANCE", "BAJAJFINSV", "MARUTI", "BHARTIARTL",
        "ADANIENT", "ADANIPORTS", "ASIANPAINT", "ULTRACEMCO",
        "WIPRO", "TECHM", "HCLTECH", "ONGC", "POWERGRID",
        "NTPC", "COALINDIA", "SUNPHARMA", "DRREDDY", "CIPLA",
        "HINDUNILVR"
    ]
    return random.choice(universe)


def generate_demo_data(trader_count: int = 20, trades_per_trader: int = 30) -> None:
    db = SessionLocal()
    try:
        max_user_id = db.query(func.max(User.id)).scalar() or 1000
        next_user_id = max(1001, max_user_id + 1)

        for i in range(trader_count):
            user_id = next_user_id + i
            email = f"trader{user_id}@stocksteward.local"
            if db.query(User).filter(User.email == email).first():
                continue
            user = User(
                id=user_id,
                full_name=f"Trader {user_id}",
                email=email,
                hashed_password=get_password_hash("trader123"),
                risk_tolerance=random.choice(["LOW", "MODERATE", "HIGH", "AGGRESSIVE"]),
                is_active=True,
                role="TRADER",
            )
            db.add(user)
            db.flush()

            portfolio = Portfolio(
                user_id=user.id,
                name=f"{user.full_name} Portfolio",
                invested_amount=random.uniform(5000, 250000),
                cash_balance=random.uniform(1000, 50000),
                win_rate=round(random.uniform(40, 85), 2),
            )
            db.add(portfolio)
            db.flush()

            for _ in range(random.randint(3, 8)):
                symbol = _random_symbol()
                avg_price = round(random.uniform(100, 4000), 2)
                qty = random.randint(1, 50)
                current_price = round(avg_price * random.uniform(0.9, 1.2), 2)
                pnl = round((current_price - avg_price) * qty, 2)
                pnl_pct = round(((current_price - avg_price) / max(avg_price, 0.01)) * 100, 2)
                db.add(Holding(
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    quantity=qty,
                    avg_price=avg_price,
                    current_price=current_price,
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                ))

            for _ in range(random.randint(1, 4)):
                symbol = _random_symbol()
                status = random.choice(["RUNNING", "PAUSED", "IDLE"])
                pnl_value = round(random.uniform(-6, 12), 2)
                db.add(Strategy(
                    portfolio_id=portfolio.id,
                    name=f"{symbol} Strategy {random.randint(1, 5)}",
                    symbol=symbol,
                    status=status,
                    pnl=f"{pnl_value:+.2f}%",
                    drawdown=round(random.uniform(0, 5), 2),
                    execution_mode="PAPER_TRADING",
                ))

            for _ in range(trades_per_trader):
                symbol = _random_symbol()
                action = random.choice(["BUY", "SELL"])
                price = round(random.uniform(100, 4000), 2)
                quantity = random.randint(1, 200)
                status = random.choice(["EXECUTED", "PENDING", "FAILED", "REJECTED"])
                timestamp = _now() - timedelta(minutes=random.randint(1, 1440))
                db.add(Trade(
                    user_id=user.id,
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    action=action,
                    quantity=quantity,
                    price=price,
                    status=status,
                    execution_mode="PAPER_TRADING",
                    timestamp=timestamp,
                    risk_score=round(random.uniform(0.1, 0.95), 2),
                    pnl=f"{random.uniform(-4, 8):+.2f}%",
                    decision_logic="Demo trade for observability metrics",
                    market_behavior="Synthetic market behavior",
                ))

        db.commit()
        print("Demo traders, portfolios, holdings, strategies, and trades generated.")
    except Exception as exc:
        db.rollback()
        print(f"Failed generating demo data: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_demo_data()
