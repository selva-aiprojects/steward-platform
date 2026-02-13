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
    print("=== ALL USERS IN DATABASE ===")
    users = db.query(User).all()
    for user in users:
        print(f"ID: {user.id}, Name: {user.full_name}, Email: {user.email}, Role: {user.role}")
        
    print("\n=== USER LOGIN CREDENTIALS ===")
    for user in users:
        if user.role == "SUPERADMIN":
            print(f"Super Admin: {user.email} / admin123")
        elif user.role == "TRADER":
            print(f"Trader: {user.email} / trader123")
        elif user.role == "BUSINESS_OWNER":
            print(f"Business Owner: {user.email} / owner123")
        elif user.role == "AUDITOR":
            print(f"Auditor: {user.email} / audit123")
    
    print("\n=== PORTFOLIO SUMMARY ===")
    portfolios = db.query(Portfolio).all()
    for portfolio in portfolios:
        user = db.query(User).filter(User.id == portfolio.user_id).first()
        if user:
            print(f"{user.full_name}: Cash={portfolio.cash_balance}, Invested={portfolio.invested_amount}, WinRate={portfolio.win_rate}%")
            
finally:
    db.close()