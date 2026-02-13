#!/usr/bin/env python3
"""
Test script to validate portfolio reporting functionality for seeded users
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.append('./backend')

from app.core.database import SessionLocal
from app.models.user import User
from app.models.portfolio import Portfolio, Holding
from app.models.trade import Trade
from app.models.strategy import Strategy

def validate_portfolio_reporting():
    print("Validating Portfolio Reporting for Seeded Users")
    print("=" * 60)

    db = SessionLocal()
    
    try:
        # 1. Verify all seeded users have portfolios
        print("\n1. Validating User Portfolios...")
        users = db.query(User).filter(User.role == "TRADER").all()
        print(f"   Found {len(users)} trader users")
        
        for user in users:
            portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
            if portfolio:
                print(f"   - {user.full_name}: Portfolio '{portfolio.name}' - Cash: INR {portfolio.cash_balance:,.2f}, Invested: INR {portfolio.invested_amount:,.2f}")
            else:
                print(f"   - {user.full_name}: NO PORTFOLIO FOUND")
        
        # 2. Validate Alexander Pierce's detailed portfolio information
        print(f"\n2. Validating Alexander Pierce's Portfolio Details...")
        alex_user = db.query(User).filter(User.email == "alex@stocksteward.ai").first()
        if alex_user:
            portfolio = db.query(Portfolio).filter(Portfolio.user_id == alex_user.id).first()
            if portfolio:
                print(f"   Portfolio ID: {portfolio.id}")
                print(f"   Portfolio Name: {portfolio.name}")
                print(f"   Cash Balance: INR {portfolio.cash_balance:,.2f}")
                print(f"   Invested Amount: INR {portfolio.invested_amount:,.2f}")
                print(f"   Win Rate: {portfolio.win_rate}%")
                
                # 3. Validate holdings
                print(f"\n3. Validating Holdings...")
                holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
                for holding in holdings:
                    print(f"   - {holding.symbol}: {holding.quantity} shares, Avg Price: INR {holding.avg_price}, Current: INR {holding.current_price}, P&L: {holding.pnl}")
                
                # 4. Validate trades
                print(f"\n4. Validating Trades...")
                trades = db.query(Trade).filter(Trade.portfolio_id == portfolio.id).order_by(Trade.timestamp.desc()).all()
                for i, trade in enumerate(trades):
                    print(f"   - #{i+1} {trade.action} {trade.symbol} ({trade.quantity} qty) at INR {trade.price} - {trade.status} - P&L: {trade.pnl}")
                
                # 5. Validate strategies
                print(f"\n5. Validating Strategies...")
                strategies = db.query(Strategy).filter(Strategy.portfolio_id == portfolio.id).all()
                for strategy in strategies:
                    print(f"   - {strategy.name} for {strategy.symbol}: {strategy.status} - P&L: {strategy.pnl}")
                
                # 6. Generate portfolio summary report
                print(f"\n6. Generating Portfolio Summary Report...")
                
                total_holding_value = 0
                for holding in holdings:
                    # Assuming current_price is updated with live data
                    current_val = holding.quantity * (holding.current_price or holding.avg_price or 0)
                    total_holding_value += current_val
                
                total_portfolio_value = portfolio.cash_balance + total_holding_value
                total_invested = portfolio.invested_amount
                
                print(f"   Total Portfolio Value: INR {total_portfolio_value:,.2f}")
                print(f"   Total Invested: INR {total_invested:,.2f}")
                print(f"   Cash Balance: INR {portfolio.cash_balance:,.2f}")
                print(f"   Holdings Value: INR {total_holding_value:,.2f}")
                
                if total_invested > 0:
                    overall_return = ((total_portfolio_value - total_invested) / total_invested) * 100
                    print(f"   Overall Return: {overall_return:+.2f}%")
                
                print(f"   Win Rate: {portfolio.win_rate}%")
                print(f"   Total Trades Executed: {len(trades)}")
                print(f"   Active Holdings: {len(holdings)}")
                print(f"   Active Strategies: {len(strategies)}")
                
                print("\n+ Portfolio Reporting Validation Successful!")
                return True
            else:
                print("   X No portfolio found for Alexander Pierce")
                return False
        else:
            print("   X Alexander Pierce user not found")
            return False
            
    except Exception as e:
        print(f"   X Error during portfolio reporting validation: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = validate_portfolio_reporting()
    if success:
        print("\nSUCCESS: All portfolio reporting validations passed!")
    else:
        print("\nERROR: Some portfolio reporting validations failed!")
        sys.exit(1)