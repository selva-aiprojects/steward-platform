from typing import Literal
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StockSteward AI"
    PROJECT_VERSION: str = "0.1.0"
    
    # Execution Mode: CRITICAL for architecture compliance
    # Start in PAPER_TRADING by default for safety
    EXECUTION_MODE: str = "PAPER_TRADING"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/stocksteward"
    
    # Security & API Keys
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
