import sys
import os

# Add the project root and backend folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.trade import Trade
from app.models.strategy import Strategy
from app.models.projection import Projection
from datetime import datetime, timedelta

def seed_db():
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding Master Demo Data...")
        
        # 1. Users & Portfolios
        users_data = [
            {"name": "Alexander Pierce", "email": "alex@stocksteward.ai", "used": 125000, "unused": 45000, "risk": "MODERATE", "win_rate": 68.0},
            {"name": "Sarah Connor", "email": "sarah.c@sky.net", "used": 250000, "unused": 12000, "risk": "HIGH", "win_rate": 74.0},
            {"name": "Tony Stark", "email": "tony@starkintl.ai", "used": 840000, "unused": 50000, "risk": "AGGRESSIVE", "win_rate": 81.0},
            {"name": "Bruce Wayne", "email": "bruce@waynecorp.com", "used": 0, "unused": 1000000, "risk": "LOW", "win_rate": 0.0},
            {"name": "Natasha Romanoff", "email": "nat@shield.gov", "used": 95000, "unused": 5000, "risk": "MODERATE", "win_rate": 62.0},
        ]

        main_user_id = None
        for u in users_data:
            user = User(
                full_name=u["name"],
                email=u["email"],
                hashed_password="hashed_password_placeholder",
                risk_tolerance=u["risk"],
                is_active=True
            )
            db.add(user)
            db.flush() 
            if u["name"] == "Alexander Pierce":
                main_user_id = user.id

            portfolio = Portfolio(
                user_id=user.id,
                name=f"{u['name']}'s Main Portfolio",
                invested_amount=u["used"],
                cash_balance=u["unused"],
                win_rate=u["win_rate"]
            )
            db.add(portfolio)
            db.flush()

            # 2. Strategies (for the Trading Hub)
            if u["name"] == "Alexander Pierce":
                strats = [
                    {"name": 'Llama-3 Trend Scalper', "symbol": 'NVDA', "status": 'RUNNING', "pnl": '+4.2%'},
                    {"name": 'MACD Mean Reversion', "symbol": 'TSLA', "status": 'PAUSED', "pnl": '-1.1%'},
                    {"name": 'Sentiment Arbitrage', "symbol": 'BTC/USD', "status": 'IDLE', "pnl": '0.0%'},
                ]
                for s in strats:
                    strategy = Strategy(
                        portfolio_id=portfolio.id,
                        name=s["name"],
                        symbol=s["symbol"],
                        status=s["status"],
                        pnl=s["pnl"],
                        drawdown=1.2,
                        execution_mode="PAPER"
                    )
                    db.add(strategy)

                # 3. Intelligence Journal (Trades)
                journal_entries = [
                    { 
                        "ticker": 'NVDA', 
                        "action": 'BUY', 
                        "price": 782.10, 
                        "behavior": 'Breakout above V-WAP with high relative volume on 5-min candle.',
                        "decision": 'Algo detected institutional accumulation. Leveraged 1.2x on high-confidence breakout signal.',
                        "pnl": '+2.41%',
                        "time": datetime.utcnow() - timedelta(hours=4)
                    },
                    { 
                        "ticker": 'TSLA', 
                        "action": 'SELL', 
                        "price": 194.50, 
                        "behavior": 'Double top formation at resistance. RSI showing bearish divergence.',
                        "decision": 'Risk engine triggered hard exit to preserve alpha. Sentiment index dropped to 32/100.',
                        "pnl": '+1.10%',
                        "time": datetime.utcnow() - timedelta(hours=2)
                    },
                    { 
                        "ticker": 'AAPL', 
                        "action": 'HOLD', 
                        "price": 188.90, 
                        "behavior": 'Sideways consolidation. No clear direction in order flow.',
                        "decision": 'Strategy "Trend Follower" stayed neutral to avoid wash-trades during low volatility.',
                        "pnl": '0.00%',
                        "time": datetime.utcnow() - timedelta(minutes=30)
                    },
                ]
                for entry in journal_entries:
                    trade = Trade(
                        portfolio_id=portfolio.id,
                        symbol=entry["ticker"],
                        action=entry["action"],
                        quantity=100,
                        price=entry["price"],
                        status="EXECUTED",
                        execution_mode="PAPER",
                        timestamp=entry["time"],
                        risk_score=0.8,
                        pnl=entry["pnl"],
                        decision_logic=entry["decision"],
                        market_behavior=entry["behavior"]
                    )
                    db.add(trade)

        # 4. Projections
        projections_data = [
            { "ticker": 'NVDA', "move": '+3.8%', "action": 'ACCUMULATE', "logic": 'Post-earnings momentum continuation' },
            { "ticker": 'AAPL', "move": '-1.2%', "action": 'TRIM', "logic": 'Resistance at $195 with volume decay' },
            { "ticker": 'TSLA', "move": '+5.4%', "action": 'BUY', "logic": 'FSD V12 rollout hype cycle' },
        ]
        for p in projections_data:
            proj = Projection(
                ticker=p["ticker"],
                move_prediction=p["move"],
                action=p["action"],
                logic=p["logic"]
            )
            db.add(proj)

        db.commit()
        print("Portal Demo Data Seeded Successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
