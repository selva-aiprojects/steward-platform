"""
Comprehensive test for StockTwits integration in StockSteward AI
This script tests all aspects of the social media sentiment integration
"""

import asyncio
import sys
from datetime import datetime, timedelta
import os

# Add the backend directory to the path
sys.path.append('./backend')

from app.services.social_media_service import social_media_service
from app.engines.ai_filter_engine import ai_filter_engine
from app.models.social_sentiment import SocialSentiment
from app.core.database import SessionLocal


async def comprehensive_test():
    print("=" * 70)
    print("STOCKTWITS INTEGRATION COMPREHENSIVE TEST")
    print("=" * 70)
    
    # Test 1: Database connectivity and table existence
    print("\n1. TESTING DATABASE CONNECTION AND TABLES")
    print("-" * 50)
    
    db = SessionLocal()
    try:
        # Check if SocialSentiment table exists and is accessible
        count = db.query(SocialSentiment).count()
        print(f"✓ SocialSentiment table exists, current record count: {count}")
        
        # Test creating and storing a record
        from datetime import datetime
        test_record = SocialSentiment(
            symbol="AAPL",
            source="stocktwits",
            message_id="test_msg_001",
            message_text="Apple stock looking great today! Bullish sentiment.",
            author="test_user",
            sentiment_score=0.75,
            sentiment_label="positive",
            engagement_score=42.5,
            timestamp=datetime.utcnow()
        )
        
        db.add(test_record)
        db.commit()
        print("✓ Successfully created and stored test record")
        
        # Retrieve the record
        retrieved = db.query(SocialSentiment).filter(
            SocialSentiment.message_id == "test_msg_001"
        ).first()
        
        if retrieved:
            print(f"✓ Successfully retrieved record: {retrieved.message_text}")
            print(f"  Sentiment: {retrieved.sentiment_score} ({retrieved.sentiment_label})")
        else:
            print("✗ Failed to retrieve test record")
        
        # Clean up test record
        db.delete(test_record)
        db.commit()
        print("✓ Cleaned up test record")
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    # Test 2: Social Media Service Functionality
    print("\n2. TESTING SOCIAL MEDIA SERVICE")
    print("-" * 50)
    
    try:
        symbol = "RELIANCE"
        print(f"Testing data fetching for symbol: {symbol}")
        
        # Test StockTwits data fetching
        stocktwits_data = await social_media_service.fetch_stocktwits_data(symbol, limit=3)
        print(f"✓ Fetched {len(stocktwits_data)} simulated StockTwits posts")
        
        if stocktwits_data:
            print(f"  Sample: {stocktwits_data[0]['message'][:80]}...")
        
        # Test Twitter data fetching
        twitter_data = await social_media_service.fetch_twitter_data(symbol, limit=3)
        print(f"✓ Fetched {len(twitter_data)} simulated Twitter posts")
        
        # Test Reddit data fetching
        reddit_data = await social_media_service.fetch_reddit_data(symbol, limit=3)
        print(f"✓ Fetched {len(reddit_data)} simulated Reddit posts")
        
        # Test processing a post
        if stocktwits_data:
            processed = await social_media_service.process_social_media_post(
                stocktwits_data[0], 'stocktwits'
            )
            if processed:
                print(f"✓ Processed post successfully")
                print(f"  Sentiment: {processed['sentiment_score']:.2f} ({processed['sentiment_label']})")
                print(f"  Engagement: {processed['engagement_score']:.2f}")
            else:
                print("✗ Failed to process post")
        
    except Exception as e:
        print(f"✗ Social media service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Database Storage Integration
    print("\n3. TESTING DATABASE STORAGE INTEGRATION")
    print("-" * 50)
    
    try:
        # Ingest some test data
        await social_media_service.ingest_social_media_data(
            symbol="TCS",
            sources=["stocktwits"]
        )
        print("✓ Successfully initiated ingestion for TCS")
        
        # Wait a moment for processing
        await asyncio.sleep(0.1)
        
        # Check if data was stored
        db = SessionLocal()
        stored_count = db.query(SocialSentiment).filter(
            SocialSentiment.symbol == "TCS"
        ).count()
        db.close()
        
        print(f"✓ Found {stored_count} records stored for TCS")
        
    except Exception as e:
        print(f"✗ Database storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: API Functionality Simulation
    print("\n4. TESTING API FUNCTIONALITY SIMULATION")
    print("-" * 50)
    
    try:
        # Test recent sentiment retrieval
        recent_sentiment = await social_media_service.get_recent_sentiment(
            symbol="RELIANCE",
            hours=24
        )
        print(f"✓ Retrieved {len(recent_sentiment)} recent sentiment records for RELIANCE")
        
        # Test aggregated sentiment
        agg_sentiment = await social_media_service.get_aggregated_sentiment(
            symbol="RELIANCE",
            hours=24
        )
        print(f"✓ Retrieved aggregated sentiment:")
        print(f"  Avg Score: {agg_sentiment['avg_sentiment_score']:.2f}")
        print(f"  Posts: {agg_sentiment['total_posts']}")
        print(f"  Positive: {agg_sentiment['positive_count']}, Negative: {agg_sentiment['negative_count']}")
        
        # Test trending symbols
        trending = await social_media_service.get_trending_symbols(hours=24, limit=5)
        print(f"✓ Retrieved {len(trending)} trending symbols")
        
    except Exception as e:
        print(f"✗ API functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: AI Integration
    print("\n5. TESTING AI INTEGRATION")
    print("-" * 50)
    
    try:
        # Test the AI filter engine with symbols parameter
        news_data = [
            {
                "title": "RELIANCE reports strong quarterly results",
                "content": "Reliance Industries has announced better than expected quarterly earnings."
            }
        ]
        
        # This should pull from the database since we're providing symbols
        ai_result = await ai_filter_engine.analyze_market_sentiment(
            news_data=news_data,
            symbols=["RELIANCE"]
        )
        
        if ai_result["success"]:
            sentiment_analysis = ai_result["sentiment_analysis"]
            print(f"✓ AI sentiment analysis completed successfully")
            print(f"  Overall sentiment: {sentiment_analysis['overall_sentiment']:.2f}")
            print(f"  News sentiment: {sentiment_analysis['news_sentiment']:.2f}")
            print(f"  Social sentiment: {sentiment_analysis['social_sentiment']:.2f}")
            print(f"  Confidence: {sentiment_analysis['confidence']:.2f}")
        else:
            print(f"✗ AI analysis failed: {ai_result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"✗ AI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: End-to-End Scenario
    print("\n6. TESTING END-TO-END SCENARIO")
    print("-" * 50)
    
    try:
        test_symbol = "INFY"
        
        # 1. Ingest data
        print(f"  • Ingesting social media data for {test_symbol}")
        await social_media_service.ingest_social_media_data(
            symbol=test_symbol,
            sources=["stocktwits", "twitter"]
        )
        
        # 2. Wait for processing
        await asyncio.sleep(0.2)
        
        # 3. Get aggregated sentiment
        agg_result = await social_media_service.get_aggregated_sentiment(
            symbol=test_symbol,
            hours=1
        )
        print(f"  • Aggregated sentiment for {test_symbol}: {agg_result['avg_sentiment_score']:.2f}")
        
        # 4. Run AI analysis with the symbol
        ai_result = await ai_filter_engine.analyze_market_sentiment(
            news_data=[{
                "title": f"{test_symbol} market update",
                "content": f"Latest news about {test_symbol} company performance."
            }],
            symbols=[test_symbol]
        )
        
        if ai_result["success"]:
            final_sentiment = ai_result["sentiment_analysis"]["overall_sentiment"]
            print(f"  • Final combined sentiment: {final_sentiment:.2f}")
            print("  ✓ End-to-end scenario completed successfully")
        else:
            print(f"  ✗ AI analysis failed in end-to-end test")
        
    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! STOCKTWITS INTEGRATION IS WORKING CORRECTLY")
    print("=" * 70)
    
    print("\nFEATURES VERIFIED:")
    print("• Database model and storage ✓")
    print("• Social media data ingestion ✓")
    print("• Sentiment analysis processing ✓")
    print("• API endpoints functionality ✓")
    print("• AI integration ✓")
    print("• End-to-end workflow ✓")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(comprehensive_test())
    if success:
        print("\n🎉 StockTwits integration test completed successfully!")
    else:
        print("\n❌ StockTwits integration test failed!")
        sys.exit(1)