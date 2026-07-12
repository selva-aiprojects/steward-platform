from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

_current_database_url = None
engine = None
SessionLocal = None
Base = declarative_base()


def _build_engine(db_url: str):
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)


def _auto_seed_if_empty():
    global SessionLocal, engine
    if SessionLocal is None or engine is None:
        return
    try:
        import app.models  # Ensure all tables are registered with Base.metadata before create_all
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            from app.models.user import User
            if db.query(User).count() == 0:
                import logging
                logging.info("Database empty on cold boot. Seeding default demo credentials...")
                from app.core.security import get_password_hash
                from app.models.portfolio import Portfolio, Holding
                from app.models.watchlist import WatchlistItem

                demo_users = [
                    {"id": 999, "name": "Super Admin", "email": "admin@stocksteward.ai", "pass": "admin123", "role": "SUPERADMIN", "risk": "LOW"},
                    {"id": 777, "name": "Business Owner", "email": "owner@stocksteward.ai", "pass": "owner123", "role": "BUSINESS_OWNER", "risk": "MODERATE"},
                    {"id": 888, "name": "Compliance Auditor", "email": "auditor@stocksteward.ai", "pass": "audit123", "role": "AUDITOR", "risk": "LOW"},
                    {"id": 100, "name": "Rahul Mehta", "email": "trader@stocksteward.ai", "pass": "trader123", "role": "TRADER", "risk": "MODERATE"},
                    {"id": 1, "name": "Alexander Pierce", "email": "alex@stocksteward.ai", "pass": "trader123", "role": "TRADER", "risk": "MODERATE"},
                    {"id": 2, "name": "Sarah Connor", "email": "sarah.c@sky.net", "pass": "trader123", "role": "TRADER", "risk": "HIGH"},
                ]

                for u in demo_users:
                    user = User(
                        id=u["id"],
                        full_name=u["name"],
                        email=u["email"],
                        hashed_password=get_password_hash(u["pass"]),
                        risk_tolerance=u["risk"],
                        is_active=True,
                        role=u["role"]
                    )
                    db.add(user)
                    db.flush()

                    if u["role"] == "TRADER" or u["id"] == 1:
                        port = Portfolio(
                            user_id=user.id,
                            name=f"{u['name']}'s Portfolio",
                            invested_amount=10000.0,
                            cash_balance=5000.0,
                            win_rate=68.0
                        )
                        db.add(port)
                        db.flush()
                        db.add(Holding(portfolio_id=port.id, symbol="RELIANCE", quantity=10, avg_price=2850.0, current_price=2920.0, pnl=700.0, pnl_pct=2.45))
                        db.add(Holding(portfolio_id=port.id, symbol="TCS", quantity=5, avg_price=3900.0, current_price=3950.0, pnl=250.0, pnl_pct=1.28))
                        db.add(WatchlistItem(user_id=user.id, symbol="RELIANCE", current_price=2920.0, change="+2.4%"))
                        db.add(WatchlistItem(user_id=user.id, symbol="TCS", current_price=3950.0, change="+1.3%"))

                db.commit()
                logging.info("Demo credentials auto-seeded successfully!")
        finally:
            db.close()
    except Exception as e:
        import logging
        logging.warning(f"Auto-seed check skip/error: {e}")


def _ensure_engine():
    global engine, SessionLocal, _current_database_url

    import os
    db_url = settings.DATABASE_URL
    if os.getenv("VERCEL") and ("stocksteward.db" in db_url or "sqlite" in db_url):
        if not db_url.startswith("sqlite:////tmp/"):
            db_url = "sqlite:////tmp/stocksteward.db"

    if engine is None or db_url != _current_database_url:
        engine = _build_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        _current_database_url = db_url
        _auto_seed_if_empty()


_ensure_engine()


def get_db():
    _ensure_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()