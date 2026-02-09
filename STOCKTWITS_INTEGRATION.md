# StockTwits Social Media Sentiment Integration

## Overview
The StockSteward AI platform now includes a comprehensive social media sentiment analysis module that integrates data from StockTwits, Twitter, and Reddit to enhance trading decisions with crowd sentiment signals.

## Features

### 1. Multi-Source Data Ingestion
- **StockTwits**: Real-time social media posts about stocks
- **Twitter/X**: Financial tweets and discussions
- **Reddit**: Investment discussions from finance-focused subreddits
- Configurable data sources for flexibility

### 2. Advanced Sentiment Analysis
- **LLM-Powered Analysis**: Uses advanced language models for nuanced sentiment scoring
- **Keyword-Based Fallback**: Robust fallback mechanism for when LLM is unavailable
- **Engagement Scoring**: Factors in likes, shares, and comments for weighted sentiment
- **Real-Time Processing**: Near real-time ingestion and analysis pipeline

### 3. Database Storage
- **SocialSentiment Model**: Dedicated database table for storing social media data
- **Metadata Capture**: Stores all relevant post metadata for analysis
- **Duplicate Prevention**: Intelligent deduplication to avoid redundant processing

### 4. API Endpoints
- `/social-media/ingest`: Trigger data ingestion for specific symbols
- `/social-media/recent/{symbol}`: Get recent sentiment for a symbol
- `/social-media/aggregate/{symbol}`: Get aggregated sentiment metrics
- `/social-media/trending`: Get trending symbols based on social activity

### 5. AI Integration
- Seamless integration with existing AI filter engine
- Pulls social sentiment from database when symbols are provided
- Combines social sentiment with news and technical analysis
- Weighted scoring system (60% news, 40% social)

## Architecture

```
Social Media Sources (StockTwits, Twitter, Reddit)
         ↓
Social Media Service (Ingestion & Processing)
         ↓
Database (SocialSentiment Table)
         ↓
AI Filter Engine (Sentiment Analysis)
         ↓
Trading Infrastructure (Decision Making)
```

## Configuration

### Environment Variables
```bash
# StockTwits API (if available)
STOCKTWITS_API_KEY=your_stocktwits_api_key

# Twitter API (if available)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# LLM Provider Keys (for advanced sentiment analysis)
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Database Schema
The system creates the following table:
- `social_sentiment`: Stores processed social media posts with sentiment scores

## Usage Examples

### 1. Ingest Social Media Data
```python
from app.services.social_media_service import social_media_service

# Ingest data for a specific symbol
await social_media_service.ingest_social_media_data(
    symbol="RELIANCE",
    sources=["stocktwits", "twitter", "reddit"]
)
```

### 2. Get Recent Sentiment
```python
# Get recent sentiment for a symbol
recent_sentiment = await social_media_service.get_recent_sentiment(
    symbol="RELIANCE",
    hours=24
)
```

### 3. Get Aggregated Metrics
```python
# Get aggregated sentiment metrics
agg_sentiment = await social_media_service.get_aggregated_sentiment(
    symbol="RELIANCE",
    hours=24
)
```

### 4. API Usage
```bash
# Ingest data via API
curl -X POST http://localhost:8000/api/v1/social-media/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE", "sources": ["stocktwits", "twitter"]}'

# Get recent sentiment
curl http://localhost:8000/api/v1/social-media/recent/RELIANCE?hours=24 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get aggregated sentiment
curl http://localhost:8000/api/v1/social-media/aggregate/RELIANCE?hours=24 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Integration with Trading System

The social sentiment data is automatically integrated into the trading decision pipeline:

1. During market analysis, the AI filter engine pulls social sentiment from the database
2. Sentiment scores are combined with news sentiment and technical indicators
3. The composite signal influences trading decisions and risk assessments
4. All social media data contributes to the overall market sentiment score

## Benefits

- **Enhanced Decision Making**: Incorporates crowd sentiment into trading algorithms
- **Real-Time Insights**: Near real-time processing of social media data
- **Risk Management**: Helps identify potential market sentiment shifts
- **Scalable Architecture**: Designed to handle multiple data sources efficiently
- **Robust Fallbacks**: Maintains functionality even when external APIs are unavailable

## Testing

Run the integration test:
```bash
python test_stocktwits_integration.py
```

## Future Enhancements

- Additional social media sources (Discord, Telegram, etc.)
- Advanced NLP models for more accurate sentiment analysis
- Sentiment trend analysis and forecasting
- Influencer identification and weighting
- Sector-specific sentiment analysis