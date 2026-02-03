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
            v = v.strip()
            if v.startswith("psql "):
                v = v.replace("psql ", "", 1).strip("'").strip('"')
            if v.startswith("'") and v.endswith("'"):
                v = v.strip("'")
            # Ensure it starts with postgresql:// or postgres://
            # SQLAlchemy 1.4+ requires postgresql://
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql://", 1)
        return v

    # Security & API Keys
    API_V1_STR: str = "/api/v1"
    
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
