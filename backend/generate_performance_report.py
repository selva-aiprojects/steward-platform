
import os
import sys
from sqlalchemy import text
from decimal import Decimal

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import SessionLocal

def generate_report():
    print("Aggregating Performance Report for 10 Traders...\n")
    db = SessionLocal()
    try:
        db.execute(text("SET search_path TO algo, public"))
        
        # Get all traders
        results = db.execute(text("""
            SELECT u.id, u.email, u.full_name, p.cash_balance, p.invested_amount, p.win_rate, s.name, s.symbol, s.pnl
            FROM users u
            JOIN portfolios p ON u.id = p.user_id
            JOIN strategies s ON p.id = s.portfolio_id
            WHERE u.email LIKE 'trader%@example.com'
            ORDER BY u.id ASC
        """)).all()
        
        total_pnl_pct = 0.0
        total_invested = 0.0
        
        print(f"{'Trader':<25} | {'Strategy':<20} | {'Inv (₹)':<10} | {'Win%':<6} | {'PnL%'}")
        print("-" * 80)
        
        for r in results:
            # Parse pnl string "+6.44%"
            pnl_str = r[8].replace('%', '').replace('+', '')
            pnl_val = float(pnl_str)
            total_pnl_pct += pnl_val
            total_invested += float(r[4])
            
            print(f"{r[1]:<25} | {r[6]:<20} | {r[4]:<10.2f} | {r[5]:<6.1f} | {r[8]}")
            
        avg_pnl = total_pnl_pct / len(results) if results else 0
        total_equity = sum([float(r[3]) + float(r[4]) for r in results])
        
        print("-" * 80)
        print(f"Aggregated Performance:")
        print(f"  Total Assets Under Management (AUM): ₹{total_equity:,.2f}")
        print(f"  Total Capital Invested: ₹{total_invested:,.2f}")
        print(f"  Average Strategy Performance: {avg_pnl:+.2f}%")
        print(f"  Overall Sentiment: {'Bullish' if avg_pnl > 0 else 'Neutral'}")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_report()
