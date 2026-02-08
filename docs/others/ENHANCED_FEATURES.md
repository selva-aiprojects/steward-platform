# StockSteward AI - Enhanced Features Documentation

## Overview

StockSteward AI is an advanced agentic AI-driven stock stewardship platform that combines multiple LLM providers with real-time financial data integration. This document outlines the enhanced features that align with your target architecture of LLM (FinGPT/Llama/DeepSeek/Groq) + Data (NSE Historical + Kaggle + Public datasets).

## Enhanced Architecture

### 1. Multi-LLM Provider Support

The system now supports multiple LLM providers for robust financial analysis:

- **Groq** (Llama models): Primary provider for fast inference
- **OpenAI** (GPT models): Alternative provider for advanced reasoning
- **Anthropic** (Claude models): For safety and accuracy
- **Hugging Face** (FinGPT, DeepSeek, etc.): For specialized financial models

### 2. Multi-Source Data Integration

The system integrates multiple data sources:

- **NSE Live Data**: Via Zerodha KiteConnect API
- **Historical Data**: NSE historical datasets
- **Kaggle Datasets**: Financial and market datasets
- **Public Financial APIs**: Alpha Vantage, Yahoo Finance
- **Custom Data Sources**: CSV, Excel, Parquet files

### 3. Enhanced AI Endpoints

New endpoints provide advanced AI capabilities:

- `/enhanced-ai/market-analysis`: Comprehensive market analysis with multiple LLM providers
- `/enhanced-ai/market-research`: Sector and market research analysis
- `/enhanced-ai/chat`: Financial chat with contextual awareness
- `/enhanced-ai/multi-source-analysis`: Cross-referenced analysis from multiple sources

## Key Features

### 1. Intelligent Market Analysis

- Technical analysis with RSI, MACD, Moving Averages
- Fundamental analysis with valuation metrics
- Sentiment analysis from market data
- Risk-adjusted recommendations with confidence scoring

### 2. Multi-Provider LLM Selection

Choose the optimal LLM provider based on:
- Response time requirements
- Accuracy needs
- Cost considerations
- Specialized financial models

### 3. Real-time Data Integration

- Live market data from NSE via KiteConnect
- Historical data for backtesting
- Sector-wise performance analysis
- Market sentiment tracking

### 4. Advanced Risk Management

- Dynamic risk assessment
- Portfolio-level risk monitoring
- Automated stop-loss suggestions
- Position sizing recommendations

## Configuration

### Environment Variables

Add these to your `.env` file for enhanced functionality:

```env
# LLM Provider Keys
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key

# Data Sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
YAHOO_FINANCE_ENABLED=true

# Zerodha KiteConnect
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret
ZERODHA_ACCESS_TOKEN=your_access_token
```

### Usage Examples

#### Market Analysis with Specific LLM Provider

```bash
curl -X POST "http://localhost:8000/api/v1/enhanced-ai/market-analysis" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{
    "symbol": "RELIANCE",
    "llm_provider": "groq",
    "model": "llama-3.3-70b-versatile",
    "analysis_type": "comprehensive"
  }'
```

#### Multi-Source Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/enhanced-ai/multi-source-analysis" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{
    "symbols": ["RELIANCE", "TCS", "HDFCBANK"],
    "llm_provider": "openai",
    "data_source": "nse"
  }'
```

## Technical Implementation

### Data Pipeline

1. **Data Collection**: Fetch from multiple sources (NSE, Kaggle, public APIs)
2. **Data Processing**: Clean, normalize, and enrich data
3. **Feature Engineering**: Calculate technical indicators and financial metrics
4. **LLM Analysis**: Process data through selected LLM provider
5. **Response Generation**: Format results as structured JSON

### AI Service Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Data Service   │───▶│  LLM Service    │
│  (NSE/Kaggle/   │    │ (Integration &  │    │ (Multi-Provider │
│   Public)       │    │  Preprocessing) │    │  Support)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Response      │
                                               │   Formatter     │
                                               └─────────────────┘
```

## Benefits

1. **Robustness**: Fallback mechanisms when primary LLM provider is unavailable
2. **Flexibility**: Choose optimal provider based on use case
3. **Accuracy**: Cross-validation across multiple data sources
4. **Performance**: Fast inference with Groq's Llama models
5. **Compliance**: Proper audit trails and risk management

## Future Enhancements

- Integration with more financial data sources
- Support for additional LLM providers
- Advanced backtesting with multiple data sources
- Real-time sentiment analysis from news sources
- Custom financial models fine-tuned on Indian market data

## Troubleshooting

If you encounter issues:

1. Verify all API keys are properly configured
2. Check network connectivity to data sources
3. Review logs for specific error messages
4. Ensure sufficient rate limits for API calls
5. Validate data source availability

For support, please contact the development team or check the main README for additional resources.