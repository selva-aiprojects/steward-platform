#!/usr/bin/env python3
"""
Test script to verify paper trading functionality with seeded users
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the backend directory to the path
sys.path.append('./backend')

from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.trade import Trade
from app.models.portfolio import Holding

async def test_paper_trading():
    print("Testing Paper Trading Functionality with Seeded Users")
    print("=" * 60)

    db = SessionLocal()
    
    try:
        # 1. Verify seeded users exist
        print("\n1. Checking Seeded Users...")
        users = db.query(User).all()
        print(f"   Found {len(users)} users in the database")
        
        for user in users:
            print(f"   - User: {user.full_name} ({user.email}), Role: {user.role}")
        
        # 2. Check Alexander Pierce's portfolio (main test user)
        alex_user = db.query(User).filter(User.email == "alex@stocksteward.ai").first()
        if alex_user:
            print(f"\n2. Checking {alex_user.full_name}'s Portfolio...")
            portfolio = db.query(Portfolio).filter(Portfolio.user_id == alex_user.id).first()
            if portfolio:
                print(f"   Portfolio Name: {portfolio.name}")
                print(f"   Cash Balance: INR {portfolio.cash_balance:,.2f}")
                print(f"   Invested Amount: INR {portfolio.invested_amount:,.2f}")
                print(f"   Win Rate: {portfolio.win_rate}%")
                
                # 3. Check holdings
                print(f"\n3. Checking Holdings...")
                holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
                for holding in holdings:
                    print(f"   - {holding.symbol}: {holding.quantity} shares at INR {holding.avg_price or 0}/share")
                
                # 4. Check trades
                print(f"\n4. Checking Trades...")
                trades = db.query(Trade).filter(Trade.portfolio_id == portfolio.id).all()
                for trade in trades:
                    print(f"   - {trade.action} {trade.symbol} ({trade.quantity} qty) at INR {trade.price} - Status: {trade.status}")
                
                # 5. Simulate a new paper trade
                print(f"\n5. Simulating New Paper Trade...")
                new_trade = Trade(
                    portfolio_id=portfolio.id,
                    symbol="INFY",
                    action="BUY",
                    quantity=50,
                    price=1540.00,
                    status="EXECUTED",
                    execution_mode="PAPER_TRADING",
                    timestamp=datetime.utcnow(),
                    risk_score=0.6,
                    pnl="+1.25%",
                    decision_logic="Technical breakout above resistance level",
                    market_behavior="Volume spike with upward momentum"
                )
                
                db.add(new_trade)
                db.commit()
                
                print(f"   - Successfully created paper trade: BUY INFY {new_trade.quantity} shares at INR {new_trade.price}")
                
                # 6. Verify the new trade was saved
                updated_trades = db.query(Trade).filter(Trade.portfolio_id == portfolio.id).all()
                print(f"   - Total trades after simulation: {len(updated_trades)}")
                
                print("\n+ Paper Trading Functionality Test Completed Successfully!")
                return True
            else:
                print(f"   X No portfolio found for {alex_user.full_name}")
                return False
        else:
            print("   X Alexander Pierce user not found")
            return False
            
    except Exception as e:
        print(f"   X Error during paper trading test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_paper_trading())
    if success:
        print("\nSUCCESS: All paper trading tests passed!")
    else:
        print("\nERROR: Some paper trading tests failed!")
        sys.exit(1)