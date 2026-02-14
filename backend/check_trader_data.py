from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.trade import Trade

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == 'trader@stocksteward.ai').first()
    if not user:
        print("User not found")
    else:
        print(f"User: {user.email}, ID: {user.id}, Role: {user.role}")
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
        print(f"Portfolio found: {bool(portfolio)}")
        if portfolio:
            print(f"Cash: {portfolio.cash_balance}, Invested: {portfolio.invested_amount}")
        
        trades_count = db.query(Trade).filter(Trade.user_id == user.id).count()
        print(f"Trades count: {trades_count}")
        
        if trades_count > 0:
            last_trade = db.query(Trade).filter(Trade.user_id == user.id).order_by(Trade.timestamp.desc()).first()
            print(f"Last trade: {last_trade.symbol} {last_trade.action} on {last_trade.timestamp}")
finally:
    db.close()
