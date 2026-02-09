"""
Test script for StockTwits integration with StockSteward AI
Demonstrates how to ingest and analyze social media sentiment data
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.social_media_service import social_media_service
from app.engines.ai_filter_engine import ai_filter_engine


async def test_stocktwits_integration():
    """
    Test the StockTwits integration functionality
    """
    print("Testing StockTwits Integration with StockSteward AI")
    print("=" * 60)
    
    # Test symbol
    symbol = "RELIANCE"
    
    print(f"\n1. Ingesting social media data for {symbol}...")
    await social_media_service.ingest_social_media_data(
        symbol=symbol,
        sources=['stocktwits', 'twitter', 'reddit']
    )
    print(f"✓ Completed ingestion for {symbol}")
    
    print(f"\n2. Retrieving recent sentiment for {symbol}...")
    recent_sentiment = await social_media_service.get_recent_sentiment(
        symbol=symbol,
        hours=24
    )
    print(f"Retrieved {len(recent_sentiment)} recent sentiment records")
    
    if recent_sentiment:
        print(f"Most recent post: {recent_sentiment[0]['message_text'][:100]}...")
        print(f"Sentiment: {recent_sentiment[0]['sentiment_label']} (Score: {recent_sentiment[0]['sentiment_score']:.2f})")
    
    print(f"\n3. Getting aggregated sentiment for {symbol}...")
    agg_sentiment = await social_media_service.get_aggregated_sentiment(
        symbol=symbol,
        hours=24
    )
    print(f"Aggregated sentiment: {agg_sentiment}")
    
    print(f"\n4. Testing AI sentiment analysis with social data...")
    # Simulate news data
    news_data = [
        {
            "title": f"{symbol} announces strong quarterly results",
            "content": f"{symbol} reported better than expected earnings, with revenue growing 15% year-over-year."
        }
    ]
    
    # Use the AI filter engine with the symbol to pull from DB
    ai_result = await ai_filter_engine.analyze_market_sentiment(
        news_data=news_data,
        symbols=[symbol]
    )
    
    if ai_result["success"]:
        sentiment_analysis = ai_result["sentiment_analysis"]
        print(f"Overall sentiment: {sentiment_analysis['overall_sentiment']:.2f}")
        print(f"News sentiment: {sentiment_analysis['news_sentiment']:.2f}")
        print(f"Social sentiment: {sentiment_analysis['social_sentiment']:.2f}")
        print(f"Confidence: {sentiment_analysis['confidence']:.2f}")
    else:
        print(f"AI analysis failed: {ai_result.get('error', 'Unknown error')}")
    
    print(f"\n5. Testing trending symbols endpoint...")
    trending = await social_media_service.get_trending_symbols(hours=24, limit=5)
    print(f"Trending symbols: {trending}")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_stocktwits_integration())
    print("\nStockTwits integration test completed successfully!")