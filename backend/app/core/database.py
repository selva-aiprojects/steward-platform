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

    # Handle malformed database URLs that start with 'psql ' prefix
    # This is a common issue when copying database URLs from command line interfaces
    if isinstance(db_url, str):
        # Clean up the URL by removing 'psql ' prefix and surrounding quotes
        cleaned_db_url = db_url.strip()

        # Handle the specific case: 'psql postgresql://...' (with quotes)
        if cleaned_db_url.startswith("'psql postgresql://") and cleaned_db_url.endswith("'"):
            start_pos = len("'psql ")
            end_pos = len(cleaned_db_url) - 1
            cleaned_db_url = cleaned_db_url[start_pos:end_pos].strip()
        elif cleaned_db_url.startswith("psql postgresql://"):
            # Handle case without outer quotes: psql postgresql://...
            start_pos = len("psql ")
            cleaned_db_url = cleaned_db_url[start_pos:].strip()
        elif cleaned_db_url.startswith("'psql ") and "postgresql://" in cleaned_db_url:
            # Handle case: 'psql postgresql://...' (with leading quote but maybe trailing quote)
            start_pos = len("'psql ")
            cleaned_db_url = cleaned_db_url[start_pos:].strip()
            if cleaned_db_url.endswith("'"):
                cleaned_db_url = cleaned_db_url[:-1].strip()

        # Remove any surrounding quotes
        cleaned_db_url = cleaned_db_url.strip("'\"")

        # Log the cleaning process for debugging
        if cleaned_db_url != db_url:
            print(f"DEBUG: Cleaned DATABASE_URL from: '{db_url}' to: '{cleaned_db_url}'")

        db_url = cleaned_db_url

    print(f"DEBUG: About to create engine with URL: '{db_url}'")  # Debug print
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
