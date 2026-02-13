import sys
sys.path.append('.')

# Force the use of SQLite for local development
import os
os.environ['DATABASE_URL'] = 'sqlite:///./stocksteward_local.db'

from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio

db = SessionLocal()
try:
    user_count = db.query(User).count()
    print(f'Found {user_count} users in local database')
    
    portfolio_count = db.query(Portfolio).count()
    print(f'Found {portfolio_count} portfolios in local database')
    
    # Get specific user to verify
    alex_user = db.query(User).filter(User.email == 'alex@stocksteward.ai').first()
    if alex_user:
        print(f'Alexander Pierce found: {alex_user.full_name} - Role: {alex_user.role}')
        
        # Get his portfolio
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == alex_user.id).first()
        if portfolio:
            print(f'Portfolio: {portfolio.name} - Cash: {portfolio.cash_balance}, Invested: {portfolio.invested_amount}')
finally:
    db.close()