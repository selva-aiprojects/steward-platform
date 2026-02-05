from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import os

_current_database_url = None
engine = None
SessionLocal = None
Base = declarative_base()


def _build_engine(db_url: str):
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)


def _ensure_engine():
    global engine, SessionLocal, _current_database_url
    db_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    if engine is None or db_url != _current_database_url:
        engine = _build_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        _current_database_url = db_url


_ensure_engine()

def get_db():
    _ensure_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
