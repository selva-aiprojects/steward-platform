from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio, Holding
from app.models.trade import Trade
from app.models.strategy import Strategy
import random
from datetime import datetime, timedelta

db = SessionLocal()
try:
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        print("User 1 not found")
        exit()
        
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    if not portfolio:
        portfolio = Portfolio(
            user_id=user.id,
            name="Alexander's Wealth Vault",
            cash_balance=500000.0,
            invested_amount=0.0,
            win_rate=65.0
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    
    # Update cash if low
    if portfolio.cash_balance < 100000:
        portfolio.cash_balance = 500000.0
        db.add(portfolio)
        db.commit()

    # Seed some trades over the last 30 days
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC"]
    for i in range(20):
        symbol = random.choice(symbols)
        action = "BUY" if i % 2 == 0 else "SELL"
        price = round(random.uniform(120, 2800), 2)
        qty = random.randint(5, 50)
        pnl_val = round(random.uniform(-1.5, 4.2), 2)
        
        trade = Trade(
            user_id=user.id,
            portfolio_id=portfolio.id,
            symbol=symbol,
            action=action,
            quantity=qty,
            price=price,
            status="EXECUTED",
            execution_mode="PAPER_TRADING",
            timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
            risk_score=round(random.uniform(10, 80), 2),
            pnl=f"{pnl_val}%",
            decision_logic="Auto-Steward rebalancing",
            market_behavior="bullish" if action == "BUY" else "volatile"
        )
        db.add(trade)
    
    # Ensure there are at least 3 active strategies
    existing_strats = db.query(Strategy).filter(Strategy.portfolio_id == portfolio.id).count()
    if existing_strats < 3:
        new_strats = [
            {"name": "Mean Reversion Bot", "symbol": "NIFTY", "status": "RUNNING"},
            {"name": "Sentiment Momentum", "symbol": "RELIANCE", "status": "RUNNING"},
            {"name": "Volatility Arbtirage", "symbol": "BANKNIFTY", "status": "RUNNING"}
        ]
        for ns in new_strats[existing_strats:]:
            s = Strategy(
                portfolio_id=portfolio.id,
                name=ns["name"],
                symbol=ns["symbol"],
                status=ns["status"],
                pnl=f"{round(random.uniform(-0.5, 2.5), 2)}%",
                drawdown=round(random.uniform(0.1, 1.2), 2),
                execution_mode="PAPER_TRADING"
            )
            db.add(s)
            
    db.commit()
    print("Seeding complete for Alex Pierce (ID 1)")
    
finally:
    db.close()
