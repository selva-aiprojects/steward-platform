from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.strategy import Strategy

db = SessionLocal()
try:
    user = db.query(User).filter(User.id == 1).first()
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    
    if portfolio:
        strategies = db.query(Strategy).filter(Strategy.portfolio_id == portfolio.id).all()
        print(f"Total strategies for user 1 (Portfolio {portfolio.id}): {len(strategies)}")
        for s in strategies:
            print(f"ID: {s.id}, Name: {s.name}, Symbol: {s.symbol}, Status: {s.status}")
    else:
        print("Portfolio not found for user 1")
finally:
    db.close()
