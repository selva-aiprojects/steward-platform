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

class ProviderInfo(BaseModel):
    provider: str
    models: List[str]

class AvailableModelsResponse(BaseModel):
    models: Dict[str, List[str]]

class AvailableProvidersResponse(BaseModel):
    providers: List[str]