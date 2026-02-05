from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Literal
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "StockSteward AI"
    PROJECT_VERSION: str = "0.1.0"
    
    # Execution Mode: CRITICAL for architecture compliance
    # Start in PAPER_TRADING by default for safety
    EXECUTION_MODE: Literal["PAPER_TRADING", "LIVE_TRADING"] = "PAPER_TRADING"
    APP_ENV: Literal["DEV", "QA", "UAT", "PROD"] = "DEV"
    ENABLE_LIVE_TRADING: bool = False
    GLOBAL_KILL_SWITCH: bool = False
    HIGH_VALUE_TRADE_THRESHOLD: float = 100000.0
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.6
    
    # Database
    # Default to local SQLite to avoid startup failures when DATABASE_URL is not provided.
    DATABASE_URL: str = "sqlite:///./stocksteward.db"
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if isinstance(v, str):
            # Strip common copy-paste artifacts from Neon/Postgres shells
            original_v = v
            v = v.strip()
            print(f"DEBUG: Raw DATABASE_URL: '{v}'")  # Debug print

            # Handle the specific case from the error: 'psql postgresql://...'
            # The error shows the string is: 'psql postgresql://...' (with quotes included)
            # So the actual string starts with 'psql and ends with '
            if "'psql postgresql://" in v:
                # Handle the case where the entire string is like: 'psql postgresql://...'
                # This means the string starts with 'psql postgresql:// and ends with '
                if v.startswith("'psql postgresql://") and v.endswith("'"):
                    # Extract the URL part between 'psql and the final '
                    # Format: 'psql postgresql://...user:pass@host/db?params'
                    start_pos = len("'psql ")
                    end_pos = len(v) - 1  # Remove the final quote
                    v = v[start_pos:end_pos].strip()
                elif v.startswith("'psql ") and "postgresql://" in v:
                    # Handle case where it's like: 'psql postgresql://user:pass@host/db?params'
                    start_pos = len("'psql ")
                    v = v[start_pos:].strip()
                    # Remove trailing quote if present
                    if v.endswith("'"):
                        v = v[:-1].strip()

            # Remove 'psql ' prefix if present (multiple variations)
            while v.startswith("psql "):
                v = v[5:].strip()

            # Remove other common prefixes that might be accidentally copied
            if v.startswith("postgresql://") or v.startswith("postgres://"):
                pass  # Already correct format
            elif v.startswith("psql ") or v.startswith("PG ") or v.startswith("DB "):
                # Extract the actual URL part
                parts = v.split()
                for part in parts:
                    if part.startswith("postgresql://") or part.startswith("postgres://"):
                        v = part
                        break

            # Remove surrounding quotes if present
            v = v.strip("'\"")

            # Ensure it starts with postgresql:// or postgres://
            # SQLAlchemy 1.4+ requires postgresql://
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql://", 1)

            print(f"DEBUG: Processed DATABASE_URL: '{v}'")  # Debug print
        return v

    # Security & API Keys
    API_V1_STR: str = "/api/v1"
    # CORS (comma-separated list or "*")
    CORS_ORIGINS: str = "*"
    
    # Zerodha KiteConnect
    ZERODHA_API_KEY: Optional[str] = None
    ZERODHA_API_SECRET: Optional[str] = None
    ZERODHA_ACCESS_TOKEN: Optional[str] = None
    
    # AI Keys
    GROQ_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("EXECUTION_MODE", mode="before")
    @classmethod
    def normalize_execution_mode(cls, v: str) -> str:
        if v is None:
            return "PAPER_TRADING"
        if not isinstance(v, str):
            raise ValueError("EXECUTION_MODE must be a string")
        normalized = v.strip().upper()
        if normalized in {"PAPER", "PAPER_TRADING"}:
            return "PAPER_TRADING"
        if normalized in {"LIVE", "LIVE_TRADING"}:
            return "LIVE_TRADING"
        raise ValueError("EXECUTION_MODE must be PAPER_TRADING or LIVE_TRADING")

    @field_validator("APP_ENV", mode="before")
    @classmethod
    def normalize_app_env(cls, v: str) -> str:
        if v is None:
            return "DEV"
        if not isinstance(v, str):
            raise ValueError("APP_ENV must be a string")
        normalized = v.strip().upper()
        if normalized in {"DEV", "QA", "UAT", "PROD"}:
            return normalized
        raise ValueError("APP_ENV must be DEV, QA, UAT, or PROD")

settings = Settings()
