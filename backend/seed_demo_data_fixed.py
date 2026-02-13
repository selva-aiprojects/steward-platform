import os
import sys
import random
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.trade import Trade
from app.models.watchlist import WatchlistItem
from app.models.strategy import Strategy
from app.models.projection import Projection
from app.core.database import SessionLocal
from app.core.security import get_password_hash

def seed_demo_data():
    """
    Seed the database with realistic demo data including users with investments
    """
    db = SessionLocal()
    
    try:
        print("Seeding demo data...")
        
        # Create demo users with different roles
        demo_users = [
            {
                "full_name": "Rajesh Kumar",
                "email": "rajesh.trader@stocksteward.ai",
                "role": "TRADER",
                "risk_tolerance": "MODERATE"
            },
            {
                "full_name": "Priya Sharma",
                "email": "priya.investor@stocksteward.ai",
                "role": "TRADER",
                "risk_tolerance": "CONSERVATIVE"
            },
            {
                "full_name": "Amit Patel",
                "email": "amit.scalper@stocksteward.ai",
                "role": "TRADER",
                "risk_tolerance": "AGGRESSIVE"
            },
            {
                "full_name": "Sunita Reddy",
                "email": "sunita.longterm@stocksteward.ai",
                "role": "TRADER",
                "risk_tolerance": "CONSERVATIVE"
            }
        ]
        
        created_users = []
        for user_data in demo_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                print(f"User {user_data['email']} already exists, using existing...")
                created_users.append(existing_user)
                continue
                
            # Create new user
            user = User(
                full_name=user_data["full_name"],
                email=user_data["email"],
                hashed_password=get_password_hash("Demo@123"),
                role=user_data["role"],
                risk_tolerance=user_data["risk_tolerance"],
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users.append(user)
            print(f"Created user: {user_data['email']}")
        
        # Create portfolios for each user with ₹100,000 initial investment
        for user in created_users:
            # Check if portfolio already exists
            existing_portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
            if existing_portfolio:
                print(f"Portfolio for user {user.email} already exists, using existing...")
                continue
                
            portfolio = Portfolio(
                user_id=user.id,
                name=f"{user.full_name}'s Investment Portfolio",
                cash_balance=100000.0,  # Start with ₹100,000
                invested_amount=0.0,
                win_rate=0.0,
                total_trades=0
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
            print(f"Created portfolio for {user.email} with ₹100,000")
        
        # Define stock universe with realistic prices
        stock_universe = {
            "RELIANCE": {"price": 2987.50, "exchange": "NSE", "sector": "Energy"},
            "TCS": {"price": 3820.00, "exchange": "NSE", "sector": "IT"},
            "HDFCBANK": {"price": 1675.00, "exchange": "NSE", "sector": "Banking"},
            "INFY": {"price": 1540.00, "exchange": "NSE", "sector": "IT"},
            "ICICIBANK": {"price": 1042.00, "exchange": "NSE", "sector": "Banking"},
            "SBIN": {"price": 580.00, "exchange": "NSE", "sector": "Banking"},
            "ITC": {"price": 438.00, "exchange": "NSE", "sector": "FMCG"},
            "LT": {"price": 2200.00, "exchange": "NSE", "sector": "Construction"},
            "AXISBANK": {"price": 1125.00, "exchange": "NSE", "sector": "Banking"},
            "KOTAKBANK": {"price": 1800.00, "exchange": "NSE", "sector": "Banking"},
            "BAJFINANCE": {"price": 7200.00, "exchange": "NSE", "sector": "Finance"},
            "MARUTI": {"price": 8500.00, "exchange": "NSE", "sector": "Auto"},
            "WIPRO": {"price": 750.00, "exchange": "NSE", "sector": "IT"},
            "SUNPHARMA": {"price": 950.00, "exchange": "NSE", "sector": "Pharma"},
            "TATAMOTORS": {"price": 750.00, "exchange": "NSE", "sector": "Auto"},
            "HINDUNILVR": {"price": 2850.00, "exchange": "NSE", "sector": "FMCG"},
            "NESTLEIND": {"price": 22000.00, "exchange": "NSE", "sector": "FMCG"},
            "ASIANPAINT": {"price": 3200.00, "exchange": "NSE", "sector": "Consumer Goods"},
            "ULTRACEMCO": {"price": 8200.00, "exchange": "NSE", "sector": "Construction"},
            "TITAN": {"price": 3400.00, "exchange": "NSE", "sector": "Consumer Goods"}
        }
        
        # Execute trades for each user to populate their portfolios
        for user in created_users:
            portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
            
            # Randomly select 5-8 stocks for each user
            selected_stocks = random.sample(list(stock_universe.items()), random.randint(5, 8))
            
            invested_amount = 0
            holdings_value = 0
            
            for stock_symbol, stock_info in selected_stocks:
                # Determine quantity based on available cash and stock price
                max_affordable = int(portfolio.cash_balance / stock_info["price"])
                if max_affordable == 0:
                    continue
                    
                # Buy between 5-20 shares (or however many can be afforded)
                quantity = min(random.randint(5, 20), max_affordable)
                investment_amount = quantity * stock_info["price"]
                
                if investment_amount > portfolio.cash_balance:
                    continue  # Skip if not enough cash
                
                # Create trade record
                trade = Trade(
                    portfolio_id=portfolio.id,
                    symbol=stock_symbol,
                    action="BUY",
                    quantity=quantity,
                    price=stock_info["price"],
                    status="COMPLETED",
                    execution_mode="PAPER_TRADING",
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)),  # Random date in last month
                    risk_score=random.uniform(0.1, 0.9),
                    pnl=0.0,  # Will be calculated based on current vs purchase price
                    decision_logic="AI-driven algorithmic selection",
                    market_behavior=f"Technical breakout above resistance at {stock_info['price']*0.95}"
                )
                db.add(trade)
                
                # Create holding record
                holding = Holding(
                    portfolio_id=portfolio.id,
                    symbol=stock_symbol,
                    quantity=quantity,
                    avg_price=stock_info["price"],
                    current_price=stock_info["price"],  # Initially same as purchase price
                    pnl=0.0,
                    pnl_pct=0.0
                )
                db.add(holding)
                
                # Update portfolio amounts
                portfolio.invested_amount += investment_amount
                portfolio.cash_balance -= investment_amount
                invested_amount += investment_amount
                holdings_value += investment_amount
                
                print(f"User {user.email}: Bought {quantity} shares of {stock_symbol} at ₹{stock_info['price']} each")
            
            # Update portfolio totals
            portfolio.total_value = portfolio.cash_balance + holdings_value
            db.add(portfolio)
        
        # Create some watchlist items
        watchlist_symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "AXISBANK", "LT"]
        for user in created_users:
            for symbol in random.sample(watchlist_symbols, random.randint(3, 6)):
                stock_info = stock_universe.get(symbol)
                if stock_info:
                    # Check if watchlist item already exists
                    existing_wl = db.query(WatchlistItem).filter(
                        WatchlistItem.user_id == user.id,
                        WatchlistItem.symbol == symbol
                    ).first()
                    
                    if not existing_wl:
                        wl_item = WatchlistItem(
                            user_id=user.id,
                            symbol=symbol,
                            current_price=stock_info["price"],
                            change=f"{random.uniform(-2, 2):+.2f}%",
                            exchange=stock_info["exchange"]
                        )
                        db.add(wl_item)
        
        # Create some strategy records
        strategy_types = ["Mean Reversion", "Momentum", "Trend Following", "Breakout", "Options Spread"]
        for user in created_users:
            portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
            
            for i in range(random.randint(1, 3)):  # Each user gets 1-3 strategies
                strategy = Strategy(
                    portfolio_id=portfolio.id,
                    name=random.choice(strategy_types),
                    symbol=random.choice(list(stock_universe.keys())),
                    status=random.choice(["RUNNING", "PAUSED", "IDLE"]),
                    pnl=f"{random.uniform(-5, 15):+.2f}%",
                    drawdown=random.uniform(0.5, 5.0),
                    execution_mode="PAPER_TRADING"
                )
                db.add(strategy)
        
        # Create some market projections
        for symbol, info in list(stock_universe.items())[:10]:  # First 10 symbols
            projection = Projection(
                ticker=symbol,
                move_prediction=f"{random.uniform(-3, 5):+.2f}%",
                action=random.choice(["BUY", "SELL", "HOLD"]),
                logic=f"Technical analysis shows {random.choice(['momentum', 'reversal', 'breakout'])} pattern for {symbol}"
            )
            db.add(projection)
        
        # Commit all changes
        db.commit()
        print("Demo data seeding completed successfully!")
        
        # Print summary
        total_users = len(created_users)
        total_portfolios = db.query(Portfolio).count()
        total_holdings = db.query(Holding).count()
        total_trades = db.query(Trade).count()
        
        print(f"\nSummary:")
        print(f"- Created {total_users} demo users")
        print(f"- Created {total_portfolios} portfolios")
        print(f"- Created {total_holdings} holdings")
        print(f"- Created {total_trades} trades")
        
    except Exception as e:
        print(f"Error seeding demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()