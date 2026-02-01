from pydantic import field_validator
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "StockSteward AI"
    PROJECT_VERSION: str = "0.1.0"
    
    # Execution Mode: CRITICAL for architecture compliance
    # Start in PAPER_TRADING by default for safety
    EXECUTION_MODE: str = "PAPER_TRADING"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/stocksteward"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
