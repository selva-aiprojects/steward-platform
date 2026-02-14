from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio, Holding
from app.models.trade import Trade

db = SessionLocal()
try:
    user = db.query(User).filter(User.id == 1).first()
    print(f"User: {user.email}, ID: {user.id}")
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    print(f"Portfolio found: {bool(portfolio)}")
    if portfolio:
        print(f"Cash: {portfolio.cash_balance}, Invested: {portfolio.invested_amount}")
        holdings_count = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).count()
        print(f"Holdings count: {holdings_count}")
        
    trades_count = db.query(Trade).filter(Trade.user_id == user.id).count()
    print(f"Trades count: {trades_count}")
finally:
    db.close()
