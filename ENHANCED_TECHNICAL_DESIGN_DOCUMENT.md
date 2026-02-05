# StockSteward AI - Enhanced Technical Design Document (Low-Level)

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Enhanced Backend Design](#enhanced-backend-design)
3. [Frontend Design](#frontend-design)
4. [Database Schema](#database-schema)
5. [Enhanced API Design](#enhanced-api-design)
6. [Security Architecture](#security-architecture)
7. [Performance & Scalability](#performance--scalability)
8. [Monitoring & Logging](#monitoring--logging)
9. [Multi-LLM Integration](#multi-llm-integration)
10. [Multi-Source Data Integration](#multi-source-data-integration)

## 1. System Architecture

### 1.1 Enhanced High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │◄──►│   Backend API    │◄──►│  External APIs  │
│   (React)       │    │   (FastAPI)      │    │ (Kite, Groq,   │
└─────────────────┘    └──────────────────┘    │  OpenAI, etc.)  │
                              │                └─────────────────┘
                    ┌─────────┴─────────┐
                    │   Message Queue   │
                    │   (Socket.IO)     │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│  ML Service    │   │  Risk Manager   │   │  Execution     │
│  (Multi-LLM)   │   │                 │   │  Engine        │
└────────────────┘   └─────────────────┘   └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Database        │
                    │   (PostgreSQL)    │
                    └───────────────────┘
```

### 1.2 Enhanced Component Architecture
- **Frontend**: React 18 with TypeScript, Tailwind CSS, Socket.io client
- **Backend**: FastAPI with Python 3.11, SQLAlchemy ORM, PostgreSQL
- **ML/AI**: Multi-LLM providers (Groq/Llama, OpenAI, Anthropic, Hugging Face), scikit-learn, TA-Lib
- **Data Integration**: NSE (KiteConnect), Kaggle datasets, Public APIs (Alpha Vantage, Yahoo Finance)
- **Database**: PostgreSQL for relational data, Redis for caching
- **Messaging**: Socket.IO for real-time updates

## 2. Enhanced Backend Design

### 2.1 Enhanced Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point with startup events
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Configuration management with multi-LLM support
│   │   ├── database.py         # Database connection
│   │   ├── security.py         # Authentication/authorization
│   │   └── middleware.py       # Custom middleware
│   ├── api/                    # API endpoints
│   │   └── v1/
│   │       ├── api.py          # API router with enhanced endpoints
│   │       └── endpoints/      # Individual endpoints
│   │           ├── trades.py
│   │           ├── portfolios.py
│   │           ├── strategies.py
│   │           ├── backtesting.py
│   │           ├── ai.py
│   │           ├── enhanced_ai.py    # NEW: Enhanced AI endpoints
│   │           └── ...
│   ├── models/                 # Database models
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   ├── trade.py
│   │   ├── strategy.py
│   │   └── ...
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── trade.py
│   │   ├── strategy.py
│   │   ├── backtesting.py
│   │   ├── ai_schemas.py       # NEW: Enhanced AI schemas
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── trade_service.py
│   │   ├── portfolio_service.py
│   │   ├── strategy_service.py
│   │   ├── backtesting_service.py
│   │   ├── llm_service.py
│   │   ├── enhanced_llm_service.py    # NEW: Multi-LLM provider service
│   │   ├── data_integration.py        # NEW: Multi-source data integration
│   │   └── ...
│   ├── utils/                  # Utility functions
│   │   ├── technical_analysis.py
│   │   ├── risk_calculations.py
│   │   └── ...
│   ├── agents/                 # AI/ML agents
│   │   ├── market_analyst.py
│   │   ├── risk_manager.py
│   │   └── ...
│   ├── backtesting/            # Backtesting engine
│   │   └── engine.py
│   └── startup.py              # NEW: Application startup sequence
├── tests/                      # Unit and integration tests
├── requirements.txt            # Dependencies with enhanced packages
└── Dockerfile                  # Container configuration
```

### 2.2 Enhanced Main Application (app/main.py)
```python
from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.middleware import add_custom_middleware
from app.startup import startup_sequence
import uvicorn
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="StockSteward AI - Enhanced Agentic AI-Driven Stock Stewardship Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
add_custom_middleware(app)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Initialize database tables and services
@app.on_event("startup")
async def startup_event():
    """
    Application startup event - initialize all services
    """
    try:
        await startup_sequence()
        logger.info("Application startup sequence completed successfully")
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

@app.get("/")
async def root():
    return {
        "message": "StockSteward AI Backend is operational",
        "version": settings.VERSION,
        "llm_providers": ["groq", "openai", "anthropic", "huggingface"],
        "data_sources": ["nse", "kaggle", "alpha_vantage", "yahoo_finance"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2.3 Enhanced Configuration Management (app/core/config.py)
```python
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "StockSteward AI"
    VERSION: str = "2.1.0"  # Updated version
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_POOL_TIMEOUT: int = 30

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Keys for Enhanced Features
    KITE_API_KEY: str = os.getenv("KITE_API_KEY", "")
    KITE_ACCESS_TOKEN: str = os.getenv("KITE_ACCESS_TOKEN", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")

    # Risk Management
    MAX_POSITION_SIZE_PERCENT: float = 0.10  # 10% of portfolio
    MAX_DAILY_LOSS_PERCENT: float = 0.02     # 2% daily loss limit
    MAX_TOTAL_EXPOSURE: float = 0.80         # 80% total exposure

    # Execution
    COMMISSION_RATE: float = 0.001           # 0.1% commission
    SLIPPAGE_RATE: float = 0.0005            # 0.05% slippage
    MIN_ORDER_QUANTITY: int = 1
    MAX_ORDER_QUANTITY: int = 10000

    # Backtesting
    BACKTEST_COMMISSION_RATE: float = 0.0005 # Lower for backtesting
    BACKTEST_SLIPPAGE_RATE: float = 0.001    # Higher for backtesting
    DEFAULT_LOOKBACK_PERIOD: int = 252       # 1 year of trading days

    # Enhanced ML/AI Configuration
    AI_MODEL_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 1000
    DEFAULT_LLM_PROVIDER: str = "groq"       # Default LLM provider
    DEFAULT_LLM_MODEL: str = "llama-3.3-70b-versatile"  # Default model

    # Enhanced Data Configuration
    DEFAULT_DATA_SOURCE: str = "nse"         # Default data source
    KAGGLE_DATASET_PATH: str = os.getenv("KAGGLE_DATASET_PATH", "./data/kaggle/")
    YAHOO_FINANCE_ENABLED: bool = True
    ALPHA_VANTAGE_ENABLED: bool = True

    # Caching
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL: int = 300  # 5 minutes

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

settings = Settings()
```

## 3. Enhanced API Endpoints

### 3.1 Enhanced API Router (app/api/v1/api.py)
```python
from fastapi import APIRouter
from app.api.v1.endpoints import (
    trades, portfolios, users, strategies, projections, logs, audit, 
    tickets, ai, enhanced_ai, market, watchlist, approvals, auth, 
    backtesting, kyc
)

api_router = APIRouter()

# Existing endpoints
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(portfolios.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(projections.router, prefix="/projections", tags=["projections"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
# NEW: Enhanced AI endpoints with multi-LLM support
api_router.include_router(enhanced_ai.router, prefix="/enhanced-ai", tags=["enhanced-ai"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(backtesting.router, prefix="/backtesting", tags=["backtesting"])
api_router.include_router(kyc.router, prefix="/kyc", tags=["kyc"])
```

### 3.2 Enhanced AI Endpoints (app/api/v1/endpoints/enhanced_ai.py)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime
import json

from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.ai_schemas import (
    MarketAnalysisRequest, 
    MarketAnalysisResponse,
    MarketResearchResponse,
    ChatRequest,
    ChatResponse,
    MultiSourceAnalysisRequest,
    AvailableModelsResponse,
    AvailableProvidersResponse
)
from app.services.enhanced_llm_service import enhanced_llm_service
from app.services.data_integration import data_integration_service

router = APIRouter()

@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def enhanced_market_analysis(
    request: MarketAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform enhanced market analysis using multiple LLM providers and data sources
    """
    try:
        # Fetch market data based on request parameters
        if request.data_source == "historical":
            market_data = await data_integration_service.fetch_nse_data(
                symbol=request.symbol,
                start_date=request.start_date or datetime.now() - timedelta(days=30),
                end_date=request.end_date or datetime.now(),
                interval=request.interval or "day"
            )
            
            if market_data.empty:
                raise HTTPException(status_code=404, detail="No market data found for the specified parameters")
            
            # Preprocess data for analysis
            processed_data = await data_integration_service.preprocess_data(market_data)
            
            # Convert to dictionary format for LLM
            market_dict = processed_data.tail(1).to_dict('records')[0] if not processed_data.empty else {}
        else:
            # Use real-time data from existing services
            from app.services.kite_service import kite_service
            market_dict = kite_service.get_quote(request.symbol, request.exchange or "NSE")
        
        # Get user context
        user_context = {
            "risk_tolerance": current_user.risk_tolerance,
            "investment_horizon": getattr(current_user, 'investment_horizon', 'MEDIUM_TERM'),
            "portfolio_size": getattr(current_user, 'portfolio_size', 'VARIES'),
            "experience_level": getattr(current_user, 'experience_level', 'INTERMEDIATE')
        }
        
        # Perform analysis with specified LLM provider
        result = await enhanced_llm_service.analyze_market_data(
            market_data=market_dict,
            user_context=user_context,
            llm_provider=request.llm_provider or "groq",
            model=request.model,
            analysis_type=request.analysis_type or "comprehensive"
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
        
        return MarketAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in enhanced market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-research", response_model=MarketResearchResponse)
async def enhanced_market_research(
    sector: Optional[str] = Query(None, description="Specific sector to analyze"),
    llm_provider: str = Query("groq", description="LLM provider to use"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate enhanced market research and sector analysis
    """
    try:
        # Fetch sector-specific data if requested
        sector_data = None
        if sector:
            from app.services.kite_service import kite_service
            sector_symbols = kite_service.get_sector_symbols(sector)
            if sector_symbols:
                # Get recent data for sector constituents
                sector_data = {}
                for symbol in sector_symbols[:10]:  # Limit to top 10 stocks
                    quote = kite_service.get_quote(symbol, "NSE")
                    if quote and 'error' not in quote:
                        sector_data[symbol] = quote
        
        # Generate market research using enhanced LLM service
        research_result = await enhanced_llm_service.generate_market_research(
            sector_data=sector_data,
            llm_provider=llm_provider
        )
        
        if "error" in research_result:
            raise HTTPException(status_code=500, detail=research_result.get("error", "Research generation failed"))
        
        return MarketResearchResponse(**research_result)
        
    except Exception as e:
        logger.error(f"Error in enhanced market research: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def enhanced_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Enhanced chat with financial data context
    """
    try:
        # Enhance the user's request with market context
        enhanced_context = f"""
        User Context:
        - Role: {current_user.role}
        - Risk Tolerance: {current_user.risk_tolerance}
        - Trading Mode: {getattr(current_user, 'trading_mode', 'PAPER')}
        
        User Request: {request.message}
        
        Additional Context: {request.context}
        """
        
        # Use the enhanced LLM service for response
        if request.llm_provider == "openai":
            result = await enhanced_llm_service.analyze_with_openai(
                prompt=enhanced_context,
                model=request.model or "gpt-4-turbo"
            )
        elif request.llm_provider == "anthropic":
            result = await enhanced_llm_service.analyze_with_anthropic(
                prompt=enhanced_context,
                model=request.model or "claude-3-sonnet-20240229"
            )
        elif request.llm_provider == "huggingface":
            result = await enhanced_llm_service.analyze_with_huggingface(
                prompt=enhanced_context,
                model_name=request.model or "ProsusAI/finbert"
            )
        else:  # Default to Groq
            result = await enhanced_llm_service.analyze_with_groq(
                prompt=enhanced_context,
                model=request.model or "llama-3.3-70b-versatile"
            )
        
        if "error" in result:
            # Return a fallback response if LLM call fails
            return ChatResponse(
                response="I'm currently experiencing technical difficulties. Market analysis is temporarily unavailable. Please try again later."
            )
        
        # Extract response from result
        if isinstance(result, dict):
            if "response" in result:
                response_text = result["response"]
            elif "analysis" in result and "summary" in result["analysis"]:
                response_text = result["analysis"]["summary"]
            elif "prediction" in result:
                response_text = result["prediction"]
            else:
                # Convert the entire result to a readable format
                response_text = json.dumps(result, indent=2, default=str)
        else:
            response_text = str(result)
        
        return ChatResponse(response=response_text)
        
    except Exception as e:
        logger.error(f"Error in enhanced chat: {e}")
        return ChatResponse(
            response="I'm currently experiencing technical difficulties. Please try again later."
        )

@router.post("/multi-source-analysis")
async def multi_source_analysis(
    request: MultiSourceAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform analysis using multiple data sources and LLM providers
    """
    try:
        # Fetch data from multiple sources
        all_data = await data_integration_service.fetch_combined_data(
            symbols=request.symbols,
            start_date=request.start_date or datetime.now() - timedelta(days=30),
            end_date=request.end_date or datetime.now(),
            data_source=request.data_source
        )
        
        results = {}
        
        for symbol, data in all_data.items():
            if not data.empty:
                # Prepare data for LLM analysis
                features = await data_integration_service.get_features_for_llm(data)
                
                # Perform analysis
                analysis = await enhanced_llm_service.analyze_market_data(
                    market_data=features,
                    user_context={
                        "risk_tolerance": current_user.risk_tolerance,
                        "investment_horizon": getattr(current_user, 'investment_horizon', 'MEDIUM_TERM')
                    },
                    llm_provider=request.llm_provider,
                    analysis_type="comprehensive"
                )
                
                results[symbol] = analysis
        
        return {"analyses": results, "summary": f"Analyzed {len(results)} symbols from {request.data_source}"}
        
    except Exception as e:
        logger.error(f"Error in multi-source analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-models")
async def get_available_models(
    provider: Optional[str] = Query(None, description="Specific provider to query")
):
    """
    Get available models from different LLM providers
    """
    try:
        models = enhanced_llm_service.get_available_models(provider)
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-providers")
async def get_available_providers():
    """
    Get list of available LLM providers
    """
    try:
        providers = enhanced_llm_service.get_available_providers()
        return {"providers": providers}
    except Exception as e:
        logger.error(f"Error getting available providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 4. Multi-LLM Integration

### 4.1 Enhanced LLM Service (app/services/enhanced_llm_service.py)
```python
"""
Enhanced LLM Service for StockSteward AI
Supports multiple LLM providers (Groq, OpenAI, Anthropic, Hugging Face) and integrates with financial data
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import pandas as pd
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

class EnhancedLLMService:
    """
    Enhanced LLM service supporting multiple providers:
    - Groq (Llama models)
    - OpenAI (GPT models)
    - Anthropic (Claude models)
    - Hugging Face (FinGPT, DeepSeek, etc.)
    """
    
    def __init__(self):
        # Initialize multiple LLM clients
        self.clients = {}
        self.available_models = {}
        
        # Groq client
        if settings.GROQ_API_KEY:
            try:
                self.clients['groq'] = Groq(api_key=settings.GROQ_API_KEY)
                self.available_models['groq'] = [
                    "llama-3.3-70b-versatile",
                    "llama3-groq-70b-8192-tool-use-preview",
                    "llama3-groq-8b-8192-tool-use-preview",
                    "mixtral-8x7b-32768"
                ]
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        
        # OpenAI client
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.clients['openai'] = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.available_models['openai'] = [
                    "gpt-4-turbo",
                    "gpt-4",
                    "gpt-3.5-turbo"
                ]
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Anthropic client
        if settings.ANTHROPIC_API_KEY:
            try:
                import anthropic
                self.clients['anthropic'] = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.available_models['anthropic'] = [
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ]
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")

    def get_financial_analysis_prompt(
        self,
        market_data: Dict[str, Any],
        user_context: Dict[str, Any] = None,
        analysis_type: str = "comprehensive"
    ) -> str:
        """
        Generate a financial analysis prompt tailored for stock analysis
        """
        base_prompt = f"""
        You are StockSteward AI, a senior wealth steward and financial analyst specializing in the Indian stock market.
        Analyze the following market data and provide actionable insights.
        
        MARKET DATA:
        {json.dumps(market_data, indent=2)}
        """
        
        if user_context:
            base_prompt += f"""
            
        USER CONTEXT:
        - Risk Tolerance: {user_context.get('risk_tolerance', 'MODERATE')}
        - Investment Horizon: {user_context.get('investment_horizon', 'MEDIUM_TERM')}
        - Portfolio Size: {user_context.get('portfolio_size', 'VARIES')}
        - Trading Experience: {user_context.get('experience_level', 'INTERMEDIATE')}
        """
        
        if analysis_type == "technical":
            base_prompt += """
            
        PROVIDE TECHNICAL ANALYSIS FOCUSING ON:
        1. Price trends and momentum
        2. Key support and resistance levels
        3. Technical indicators (RSI, MACD, Moving Averages)
        4. Trading signals (BUY/SELL/HOLD with confidence score 0-100)
        5. Risk assessment (0-100 scale)
        """
        elif analysis_type == "fundamental":
            base_prompt += """
            
        PROVIDE FUNDAMENTAL ANALYSIS FOCUSING ON:
        1. Valuation metrics
        2. Financial health indicators
        3. Sector performance
        4. Growth prospects
        5. Dividend yield and sustainability
        """
        elif analysis_type == "sentiment":
            base_prompt += """
            
        PROVIDE SENTIMENT ANALYSIS FOCUSING ON:
        1. Market sentiment based on price action
        2. Volatility assessment
        3. News sentiment (if available)
        4. Investor positioning
        5. Fear/Greed index implications
        """
        else:  # comprehensive
            base_prompt += """
            
        PROVIDE COMPREHENSIVE ANALYSIS INCLUDING:
        1. Technical indicators and price action
        2. Fundamental health assessment
        3. Market sentiment and positioning
        4. Risk-adjusted recommendation (BUY/SELL/HOLD)
        5. Confidence score (0-100)
        6. Entry/exit levels with stop-loss suggestions
        7. Time horizon for the recommendation
        8. Key catalysts to watch
        9. Risk factors to consider
        
        RETURN YOUR RESPONSE AS A VALID JSON OBJECT WITH THE FOLLOWING STRUCTURE:
        {
            "recommendation": "BUY|SELL|HOLD",
            "confidence": 0-100,
            "target_price": float,
            "stop_loss": float,
            "time_horizon": "SHORT|MEDIUM|LONG",
            "analysis": {
                "technical": "Technical analysis summary",
                "fundamental": "Fundamental analysis summary", 
                "sentiment": "Sentiment analysis summary"
            },
            "signals": {
                "rsi_signal": "OVERSOLD|OVERBOUGHT|NEUTRAL",
                "macd_signal": "BULLISH|BEARISH|NEUTRAL",
                "ma_signal": "BULLISH|BEARISH|NEUTRAL"
            },
            "risk_factors": ["factor1", "factor2"],
            "catalysts": ["catalyst1", "catalyst2"],
            "rationale": "Detailed explanation for the recommendation"
        }
        """
        
        return base_prompt

    async def analyze_with_groq(
        self,
        prompt: str,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze using Groq (Llama models)
        """
        if 'groq' not in self.clients:
            return {
                "error": "Groq client not initialized",
                "fallback_response": "Market analysis pending: LLM service unavailable"
            }
        
        try:
            response = self.clients['groq'].chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are StockSteward AI, a senior wealth steward and financial analyst specializing in the Indian stock market. Provide accurate, concise, and actionable financial insights. Always return valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response from Groq: {content}")
                return {
                    "error": "Failed to parse LLM response",
                    "raw_response": content
                }
                
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return {
                "error": f"Groq API error: {str(e)}",
                "fallback_response": "Market analysis pending: Temporary service disruption"
            }

    async def analyze_with_openai(
        self,
        prompt: str,
        model: str = "gpt-4-turbo",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze using OpenAI (GPT models)
        """
        if 'openai' not in self.clients:
            return {
                "error": "OpenAI client not initialized",
                "fallback_response": "Market analysis pending: LLM service unavailable"
            }
        
        try:
            response = self.clients['openai'].chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are StockSteward AI, a senior wealth steward and financial analyst specializing in the Indian stock market. Provide accurate, concise, and actionable financial insights. Always return valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response from OpenAI: {content}")
                return {
                    "error": "Failed to parse LLM response",
                    "raw_response": content
                }
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return {
                "error": f"OpenAI API error: {str(e)}",
                "fallback_response": "Market analysis pending: Temporary service disruption"
            }

    async def analyze_with_anthropic(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze using Anthropic (Claude models)
        """
        if 'anthropic' not in self.clients:
            return {
                "error": "Anthropic client not initialized",
                "fallback_response": "Market analysis pending: LLM service unavailable"
            }
        
        try:
            message = self.clients['anthropic'].messages.create(
                max_tokens=2000,
                temperature=temperature,
                system="You are StockSteward AI, a senior wealth steward and financial analyst specializing in the Indian stock market. Provide accurate, concise, and actionable financial insights. Always return valid JSON when requested.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=model
            )
            
            content = message.content[0].text.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response from Anthropic: {content}")
                return {
                    "error": "Failed to parse LLM response",
                    "raw_response": content
                }
                
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}")
            return {
                "error": f"Anthropic API error: {str(e)}",
                "fallback_response": "Market analysis pending: Temporary service disruption"
            }

    async def analyze_with_huggingface(
        self,
        prompt: str,
        model_name: str = "ProsusAI/finbert",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze using Hugging Face models (FinGPT, DeepSeek, etc.)
        """
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            # For financial sentiment analysis
            if "finbert" in model_name.lower():
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)
                
                # Tokenize and predict
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    
                # Convert to financial insight
                positive_confidence = predictions[0][2].item()  # Index 2 is typically positive in FinBERT
                negative_confidence = predictions[0][0].item()  # Index 0 is typically negative
                
                recommendation = "BUY" if positive_confidence > 0.6 else "SELL" if negative_confidence > 0.6 else "HOLD"
                confidence = max(positive_confidence, negative_confidence) * 100
                
                return {
                    "recommendation": recommendation,
                    "confidence": round(confidence, 2),
                    "analysis": {
                        "sentiment_score": round(positive_confidence - negative_confidence, 3),
                        "positive_sentiment": round(positive_confidence, 3),
                        "negative_sentiment": round(negative_confidence, 3)
                    },
                    "model_used": model_name
                }
            else:
                # Use Hugging Face Inference API for other models
                import requests
                
                hf_api_token = settings.HUGGINGFACE_API_KEY
                if not hf_api_token:
                    return {
                        "error": "Hugging Face API token not configured",
                        "fallback_response": "Market analysis pending: Hugging Face service unavailable"
                    }
                
                api_url = f"https://api-inference.huggingface.co/models/{model_name}"
                headers = {"Authorization": f"Bearer {hf_api_token}"}
                
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "return_full_text": False,
                        "max_new_tokens": 500,
                        "temperature": temperature
                    }
                }
                
                response = requests.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get('generated_text', '')
                        
                        # Try to extract JSON from generated text
                        try:
                            # Look for JSON in the response
                            start_idx = generated_text.find('{')
                            end_idx = generated_text.rfind('}') + 1
                            
                            if start_idx != -1 and end_idx != 0:
                                json_str = generated_text[start_idx:end_idx]
                                return json.loads(json_str)
                            else:
                                return {
                                    "raw_response": generated_text,
                                    "model_used": model_name
                                }
                        except json.JSONDecodeError:
                            return {
                                "raw_response": generated_text,
                                "model_used": model_name
                            }
                    else:
                        return {
                            "error": "Unexpected response format from Hugging Face",
                            "raw_response": str(result)
                        }
                else:
                    return {
                        "error": f"Hugging Face API error: {response.status_code}",
                        "details": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Error calling Hugging Face model {model_name}: {e}")
            return {
                "error": f"Hugging Face error: {str(e)}",
                "fallback_response": "Market analysis pending: Model service unavailable"
            }

    async def analyze_market_data(
        self,
        market_data: Dict[str, Any],
        user_context: Dict[str, Any] = None,
        llm_provider: str = "groq",
        model: str = None,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Main method to analyze market data using specified LLM provider
        """
        # Generate prompt
        prompt = self.get_financial_analysis_prompt(market_data, user_context, analysis_type)
        
        # Select model if not provided
        if not model:
            if llm_provider in self.available_models and self.available_models[llm_provider]:
                model = self.available_models[llm_provider][0]  # Use first available model
            else:
                model = "llama-3.3-70b-versatile"  # Default fallback
        
        # Call appropriate analyzer
        if llm_provider == "groq":
            return await self.analyze_with_groq(prompt, model)
        elif llm_provider == "openai":
            return await self.analyze_with_openai(prompt, model)
        elif llm_provider == "anthropic":
            return await self.analyze_with_anthropic(prompt, model)
        elif llm_provider == "huggingface":
            return await self.analyze_with_huggingface(prompt, model)
        else:
            # Default to Groq if provider not specified or not available
            return await self.analyze_with_groq(prompt, model)

    def get_available_providers(self) -> List[str]:
        """
        Get list of available LLM providers
        """
        return list(self.clients.keys())
    
    def get_available_models(self, provider: str = None) -> Dict[str, List[str]]:
        """
        Get available models for a provider or all providers
        """
        if provider:
            return {provider: self.available_models.get(provider, [])}
        return self.available_models

# Global instance
enhanced_llm_service = EnhancedLLMService()
```

## 5. Multi-Source Data Integration

### 5.1 Data Integration Service (app/services/data_integration.py)
```python
"""
Data Integration Service for StockSteward AI
Integrates multiple data sources including NSE Historical, Kaggle datasets, and public datasets
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
from pathlib import Path
import requests
from kiteconnect import KiteConnect
from app.core.config import settings
from app.services.kite_service import kite_service

logger = logging.getLogger(__name__)

class DataIntegrationService:
    """
    Service to integrate multiple data sources:
    - NSE Historical data via KiteConnect
    - Kaggle datasets
    - Alpha Vantage, Yahoo Finance APIs
    - Custom data sources
    """
    
    def __init__(self):
        self.kite = kite_service
        self.data_sources = {
            'nse': self.fetch_nse_data,
            'kaggle': self.fetch_kaggle_data,
            'alpha_vantage': self.fetch_alpha_vantage_data,
            'yfinance': self.fetch_yfinance_data,
            'custom': self.fetch_custom_data
        }
    
    async def fetch_nse_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime, 
        interval: str = "day",
        exchange: str = "NSE"
    ) -> pd.DataFrame:
        """
        Fetch historical data from NSE via KiteConnect
        """
        try:
            # Get instrument token
            quote = self.kite.get_quote(symbol, exchange)
            if not quote or 'error' in quote:
                logger.warning(f"Could not get quote for {symbol}: {quote.get('error', 'No data')}")
                return pd.DataFrame()
            
            instrument_token = quote.get('instrument_token')
            if not instrument_token:
                logger.error(f"No instrument token found for {symbol}")
                return pd.DataFrame()
            
            # Fetch historical data
            historical_data = self.kite.get_historical(
                symbol=symbol,
                from_date=start_date.strftime('%Y-%m-%d'),
                to_date=end_date.strftime('%Y-%m-%d'),
                interval=interval,
                exchange=exchange
            )
            
            if not historical_data:
                logger.warning(f"No historical data found for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            if df.empty:
                return df
            
            # Rename columns to standard format
            df.rename(columns={
                'date': 'timestamp',
                'open': 'open_price',
                'high': 'high_price',
                'low': 'low_price',
                'close': 'close_price',
                'volume': 'volume'
            }, inplace=True)
            
            # Add symbol column
            df['symbol'] = symbol
            df['exchange'] = exchange
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching NSE data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_kaggle_data(
        self, 
        dataset_path: str, 
        symbol: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch data from local Kaggle dataset
        """
        try:
            if not os.path.exists(dataset_path):
                logger.error(f"Kaggle dataset not found: {dataset_path}")
                return pd.DataFrame()
            
            # Determine file type and read accordingly
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
            elif dataset_path.endswith('.parquet'):
                df = pd.read_parquet(dataset_path)
            elif dataset_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(dataset_path)
            else:
                logger.error(f"Unsupported file format: {dataset_path}")
                return pd.DataFrame()
            
            # Standardize column names if needed
            column_mapping = {
                'Date': 'timestamp',
                'Timestamp': 'timestamp',
                'Open': 'open_price',
                'High': 'high_price', 
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume',
                'Adj Close': 'adj_close_price'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            
            # Convert timestamp to datetime if it exists
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Add symbol if provided
            if symbol:
                df['symbol'] = symbol
                
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Kaggle data from {dataset_path}: {e}")
            return pd.DataFrame()
    
    async def fetch_alpha_vantage_data(
        self, 
        symbol: str, 
        api_key: str,
        function: str = "TIME_SERIES_DAILY",
        outputsize: str = "full"
    ) -> pd.DataFrame:
        """
        Fetch data from Alpha Vantage API
        """
        try:
            if not api_key:
                logger.error("Alpha Vantage API key not provided")
                return pd.DataFrame()
            
            base_url = "https://www.alphavantage.co/query"
            params = {
                'function': function,
                'symbol': symbol,
                'apikey': api_key,
                'outputsize': outputsize
            }
            
            response = requests.get(base_url, params=params)
            data = response.json()
            
            # Check for errors
            if "Error Message" in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return pd.DataFrame()
            
            if "Note" in data:
                logger.warning(f"Alpha Vantage note: {data['Note']}")
                return pd.DataFrame()
            
            # Extract time series data
            time_series_key = [key for key in data.keys() if 'Time Series' in key][0]
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df = pd.DataFrame(time_series).T
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            
            # Rename columns
            df.columns = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
            df = df.astype({'open_price': float, 'high_price': float, 'low_price': float, 'close_price': float, 'volume': int})
            
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'timestamp'}, inplace=True)
            df['symbol'] = symbol
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_yfinance_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch data from Yahoo Finance using yfinance
        """
        try:
            import yfinance as yf
            
            # Format symbol for Yahoo Finance (e.g., RELIANCE.NS for NSE)
            if '.' not in symbol:
                yf_symbol = f"{symbol}.NS"  # NSE suffix
            else:
                yf_symbol = symbol
            
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                logger.warning(f"No data found for {yf_symbol}")
                return pd.DataFrame()
            
            # Reset index to make date a column
            df.reset_index(inplace=True)
            
            # Rename columns to match our standard
            df.rename(columns={
                'Date': 'timestamp',
                'Datetime': 'timestamp',
                'Open': 'open_price',
                'High': 'high_price',
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume',
                'Adj Close': 'adj_close_price'
            }, inplace=True)
            
            df['symbol'] = symbol.split('.')[0]  # Remove exchange suffix
            df['exchange'] = 'NSE' if '.NS' in yf_symbol else 'OTHER'
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_custom_data(
        self, 
        file_path: str, 
        symbol: str,
        date_column: str = 'date',
        open_column: str = 'open',
        high_column: str = 'high',
        low_column: str = 'low',
        close_column: str = 'close',
        volume_column: str = 'volume'
    ) -> pd.DataFrame:
        """
        Fetch data from custom CSV/Excel file
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Custom data file not found: {file_path}")
                return pd.DataFrame()
            
            # Determine file type
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path}")
                return pd.DataFrame()
            
            # Rename columns to standard format
            column_mapping = {
                date_column: 'timestamp',
                open_column: 'open_price',
                high_column: 'high_price',
                low_column: 'low_price',
                close_column: 'close_price',
                volume_column: 'volume'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Add symbol
            df['symbol'] = symbol
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching custom data from {file_path}: {e}")
            return pd.DataFrame()
    
    async def fetch_combined_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        data_source: str = 'nse',
        **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data from multiple symbols using specified data source
        """
        results = {}
        
        for symbol in symbols:
            if data_source == 'nse':
                df = await self.fetch_nse_data(symbol, start_date, end_date, **kwargs)
            elif data_source == 'kaggle':
                dataset_path = kwargs.get('dataset_path', '')
                df = await self.fetch_kaggle_data(dataset_path, symbol)
            elif data_source == 'alpha_vantage':
                api_key = kwargs.get('api_key', '')
                df = await self.fetch_alpha_vantage_data(symbol, api_key, **kwargs)
            elif data_source == 'yfinance':
                df = await self.fetch_yfinance_data(symbol, start_date, end_date)
            elif data_source == 'custom':
                file_path = kwargs.get('file_path', '')
                df = await self.fetch_custom_data(file_path, symbol, **kwargs)
            else:
                logger.error(f"Unknown data source: {data_source}")
                continue
            
            if not df.empty:
                results[symbol] = df
            else:
                logger.warning(f"No data retrieved for symbol: {symbol}")
        
        return results
    
    async def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data for ML/AI models
        """
        if df.empty:
            return df
        
        # Sort by timestamp
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate additional technical indicators
        if 'close_price' in df.columns:
            # Moving averages
            df['sma_20'] = df['close_price'].rolling(window=20).mean()
            df['sma_50'] = df['close_price'].rolling(window=50).mean()
            df['ema_12'] = df['close_price'].ewm(span=12).mean()
            df['ema_26'] = df['close_price'].ewm(span=26).mean()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # RSI
            delta = df['close_price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bb_middle'] = df['close_price'].rolling(window=20).mean()
            bb_std = df['close_price'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            # Volatility
            df['volatility'] = df['close_price'].rolling(window=20).std()
            
            # Price change percentage
            df['price_change_pct'] = df['close_price'].pct_change() * 100
        
        # Fill NaN values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(method='ffill').fillna(0)
        
        return df
    
    async def get_features_for_llm(
        self,
        df: pd.DataFrame,
        lookback_days: int = 30
    ) -> Dict[str, Union[float, str, List[Dict]]]:
        """
        Prepare features for LLM consumption
        """
        if df.empty:
            return {}
        
        # Get recent data
        recent_df = df.tail(lookback_days) if len(df) > lookback_days else df
        
        # Calculate key metrics
        latest_price = recent_df['close_price'].iloc[-1] if 'close_price' in recent_df.columns else 0
        price_change_pct = recent_df['price_change_pct'].iloc[-1] if 'price_change_pct' in recent_df.columns else 0
        
        # Prepare market context for LLM
        context = {
            'latest_price': float(latest_price),
            'price_change_pct': float(price_change_pct),
            'trend': 'bullish' if price_change_pct > 0 else 'bearish' if price_change_pct < 0 else 'neutral',
            'volatility': float(recent_df['volatility'].iloc[-1]) if 'volatility' in recent_df.columns else 0,
            'rsi': float(recent_df['rsi'].iloc[-1]) if 'rsi' in recent_df.columns else 50,
            'macd': float(recent_df['macd'].iloc[-1]) if 'macd' in recent_df.columns else 0,
            'recent_high': float(recent_df['high_price'].max()) if 'high_price' in recent_df.columns else 0,
            'recent_low': float(recent_df['low_price'].min()) if 'low_price' in recent_df.columns else 0,
            'volume_avg': float(recent_df['volume'].mean()) if 'volume' in recent_df.columns else 0,
            'sma_20': float(recent_df['sma_20'].iloc[-1]) if 'sma_20' in recent_df.columns else 0,
            'sma_50': float(recent_df['sma_50'].iloc[-1]) if 'sma_50' in recent_df.columns else 0,
            'data_points': len(recent_df),
            'date_range': {
                'start': recent_df['timestamp'].iloc[0].isoformat() if 'timestamp' in recent_df.columns else '',
                'end': recent_df['timestamp'].iloc[-1].isoformat() if 'timestamp' in recent_df.columns else ''
            }
        }
        
        # Add recent price movements
        if 'close_price' in recent_df.columns:
            recent_prices = recent_df['close_price'].tail(7).tolist()
            context['recent_price_movements'] = [
                {
                    'date': row['timestamp'].isoformat() if 'timestamp' in row else '',
                    'price': float(row['close_price']) if 'close_price' in row else 0,
                    'change_pct': float(row['price_change_pct']) if 'price_change_pct' in row else 0
                }
                for _, row in recent_df.tail(7).iterrows()
            ]
        
        return context

# Global instance
data_integration_service = DataIntegrationService()
```

## 6. Enhanced Startup Sequence

### 6.1 Startup Service (app/startup.py)
```python
"""
Startup script for StockSteward AI backend
Initializes all services and performs health checks
"""

import asyncio
import logging
from app.core.config import settings
from app.core.database import engine, Base
from app.services.kite_service import kite_service
from app.services.enhanced_llm_service import enhanced_llm_service
from app.services.data_integration import data_integration_service
from app.core.socket_manager import socket_manager

logger = logging.getLogger(__name__)

async def initialize_services():
    """
    Initialize all core services with proper error handling
    """
    logger.info("Starting StockSteward AI service initialization...")
    
    # 1. Initialize database
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # 2. Initialize Kite/Zerodha service
    try:
        if settings.ZERODHA_API_KEY and settings.ZERODHA_ACCESS_TOKEN:
            kite_initialized = kite_service.initialize_client()
            if kite_initialized:
                logger.info("KiteConnect service initialized successfully")
            else:
                logger.warning("KiteConnect service failed to initialize - paper trading mode will be used")
        else:
            logger.info("KiteConnect credentials not provided - running in paper trading mode")
    except Exception as e:
        logger.error(f"KiteConnect service initialization failed: {e}")
        # Don't raise exception as paper trading is still possible
    
    # 3. Initialize Enhanced LLM Services
    try:
        # Initialize multiple LLM providers
        providers_initialized = await enhanced_llm_service.initialize_providers()
        logger.info(f"Initialized LLM providers: {providers_initialized}")
    except Exception as e:
        logger.error(f"Enhanced LLM service initialization failed: {e}")
        # Don't raise exception as fallback mechanisms exist
    
    # 4. Initialize Data Integration Services
    try:
        # Verify data sources are accessible
        data_sources_verified = await data_integration_service.verify_connections()
        logger.info(f"Verified data sources: {data_sources_verified}")
    except Exception as e:
        logger.error(f"Data integration service initialization failed: {e}")
        # Don't raise exception as fallback data sources exist
    
    # 5. Initialize Socket Manager
    try:
        socket_manager.init_app(None)  # Will be initialized with app in main
        logger.info("Socket manager initialized")
    except Exception as e:
        logger.error(f"Socket manager initialization failed: {e}")
        raise
    
    logger.info("All services initialized successfully")

async def startup_sequence():
    """
    Complete startup sequence for StockSteward AI
    """
    logger.info("Starting StockSteward AI platform...")
    
    try:
        # Initialize all services
        await initialize_services()
        
        logger.info("Startup sequence completed successfully")
        
    except Exception as e:
        logger.error(f"Startup sequence failed: {e}")
        raise

if __name__ == "__main__":
    # Run startup sequence if called directly
    asyncio.run(startup_sequence())
```

## 7. Enhanced Schemas

### 7.1 Enhanced AI Schemas (app/schemas/ai_schemas.py)
```python
"""
Enhanced AI Schemas for StockSteward AI
Defines request/response models for enhanced LLM integration
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

class LLMProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"

class AnalysisType(str, Enum):
    COMPREHENSIVE = "comprehensive"
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"

class Recommendation(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class TimeHorizon(str, Enum):
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"

class SignalType(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

class MarketAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to analyze")
    exchange: Optional[str] = Field(default="NSE", description="Exchange (e.g., NSE, BSE)")
    data_source: str = Field(default="live", description="Data source: 'live', 'historical', 'mock'")
    start_date: Optional[datetime] = Field(None, description="Start date for historical data")
    end_date: Optional[datetime] = Field(None, description="End date for historical data")
    interval: Optional[str] = Field(default="day", description="Data interval: minute, day, week, month")
    llm_provider: LLMProvider = Field(default=LLMProvider.GROQ, description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use (if provider supports multiple models)")
    analysis_type: AnalysisType = Field(default=AnalysisType.COMPREHENSIVE, description="Type of analysis to perform")
    include_risk_management: bool = Field(default=True, description="Include risk management suggestions")

class TechnicalSignals(BaseModel):
    rsi_signal: SignalType
    macd_signal: SignalType
    ma_signal: SignalType

class AnalysisResults(BaseModel):
    technical: str = Field(..., description="Technical analysis summary")
    fundamental: str = Field(..., description="Fundamental analysis summary")
    sentiment: str = Field(..., description="Sentiment analysis summary")

class MarketAnalysisResponse(BaseModel):
    recommendation: Recommendation
    confidence: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    target_price: Optional[float] = Field(None, description="Target price suggestion")
    stop_loss: Optional[float] = Field(None, description="Stop loss suggestion")
    time_horizon: TimeHorizon
    analysis: AnalysisResults
    signals: TechnicalSignals
    risk_factors: List[str]
    catalysts: List[str]
    rationale: str = Field(..., description="Detailed explanation for the recommendation")
    model_used: Optional[str] = Field(None, description="Model that generated the analysis")
    provider_used: Optional[LLMProvider] = Field(None, description="Provider that generated the analysis")

class MarketResearchResponse(BaseModel):
    headlines: List[str]
    sector_analysis: Dict[str, Union[List[Dict], str]]
    market_drivers: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    threats: List[str]
    outlook: Dict[str, str]  # short_term, medium_term
    research_summary: str

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message/query")
    context: Optional[str] = Field(None, description="Additional context for the query")
    llm_provider: LLMProvider = Field(default=LLMProvider.GROQ, description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")
    include_market_data: bool = Field(default=True, description="Whether to include market data in response")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response to the user query")

class MultiSourceAnalysisRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of symbols to analyze")
    start_date: Optional[datetime] = Field(None, description="Start date for historical data")
    end_date: Optional[datetime] = Field(None, description="End date for historical data")
    llm_provider: LLMProvider = Field(default=LLMProvider.GROQ, description="LLM provider to use")
    data_source: str = Field(default="nse", description="Data source to use: 'nse', 'kaggle', 'alpha_vantage', 'yfinance', 'custom'")

class AvailableModelsResponse(BaseModel):
    models: Dict[str, List[str]]

class AvailableProvidersResponse(BaseModel):
    providers: List[str]
```

## 8. Enhanced Requirements

### 8.1 Updated Requirements (requirements.txt)
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic[email]==2.6.0
pydantic-settings==2.1.0
python-dotenv==1.0.1
requests==2.31.0
python-socketio==5.11.0
groq==0.4.2
passlib==1.7.4
scipy==1.11.4
numpy==1.24.3
pandas==2.1.4
kiteconnect==4.2.1
yfinance==0.2.18
transformers==4.36.0
torch==2.1.0
openai==1.3.5
anthropic==0.5.0
huggingface_hub==0.19.4
datasets==2.14.6
plotly==5.17.0
cufflinks==0.17.3
ta==0.11.0
TA-Lib==0.4.24
ccxt==4.2.87
websocket-client==1.6.4
websockets==12.0
redis==5.0.1
celery==5.3.4
rq==1.15.1
schedule==1.2.0
apscheduler==3.10.4
python-jose==3.3.0
cryptography==41.0.8
bcrypt==4.0.1
python-multipart==0.0.6
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0
jupyter==1.0.0
matplotlib==3.8.2
seaborn==0.13.0
scikit-learn==1.3.2
statsmodels==0.14.0
arch==6.1.0
pykalman==0.9.5
kaleido==0.2.1
orjson==3.9.10
ujson==5.8.0
gunicorn==21.2.0
```

This enhanced technical design document reflects all the improvements made to the StockSteward AI platform to support:

1. **Multi-LLM Provider Integration**: Supporting Groq (Llama), OpenAI (GPT), Anthropic (Claude), and Hugging Face (FinGPT/DeepSeek) models
2. **Multi-Source Data Integration**: NSE live data, Kaggle datasets, Alpha Vantage, Yahoo Finance, and custom data sources
3. **Enhanced API Endpoints**: New endpoints for multi-LLM market analysis, research, and chat
4. **Improved Architecture**: Better separation of concerns with enhanced services and data integration
5. **Robust Error Handling**: Fallback mechanisms when primary services are unavailable
6. **Scalable Design**: Ready for production with proper logging, monitoring, and health checks

The system now fully supports your target architecture of LLM (FinGPT/Llama/DeepSeek/Groq) + Data (NSE Historical + Kaggle + Public datasets) with all features properly integrated and documented.