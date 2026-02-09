"""
Simple test to verify StockTwits integration is working
"""

import asyncio
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, '.')

from app.services.social_media_service import social_media_service
from app.engines.ai_filter_engine import ai_filter_engine
from app.models.social_sentiment import SocialSentiment
from app.core.database import SessionLocal


async def simple_verification():
    print("STOCKTWITS INTEGRATION VERIFICATION")
    print("="*50)
    
    # Test 1: Database connectivity
    print("\n1. Testing database connectivity...")
    db = SessionLocal()
    try:
        count = db.query(SocialSentiment).count()
        print(f"   OK - SocialSentiment table exists, records: {count}")
    except Exception as e:
        print(f"   FAIL - Database error: {e}")
        return False
    finally:
        db.close()
    
    # Test 2: Service functionality
    print("\n2. Testing social media service...")
    try:
        symbol = "RELIANCE"
        data = await social_media_service.fetch_stocktwits_data(symbol, limit=2)
        print(f"   OK - Retrieved {len(data)} simulated posts for {symbol}")
        
        if data:
            processed = await social_media_service.process_social_media_post(data[0], 'stocktwits')
            if processed:
                print(f"   OK - Processed post with sentiment: {processed['sentiment_score']:.2f}")
            else:
                print("   FAIL - Could not process post")
                return False
    except Exception as e:
        print(f"   FAIL - Service error: {e}")
        return False
    
    # Test 3: Storage functionality
    print("\n3. Testing database storage...")
    try:
        db = SessionLocal()
        
        # Create test record
        test_record = SocialSentiment(
            symbol="TEST",
            source="verification",
            message_id="test_001",
            message_text="Test message for verification",
            author="test",
            sentiment_score=0.5,
            sentiment_label="neutral",
            engagement_score=1.0,
            timestamp=datetime.utcnow()
        )
        
        db.add(test_record)
        db.commit()
        print("   OK - Stored test record")
        
        # Retrieve it back
        retrieved = db.query(SocialSentiment).filter(SocialSentiment.message_id == "test_001").first()
        if retrieved:
            print(f"   OK - Retrieved record with sentiment: {retrieved.sentiment_score}")
        else:
            print("   FAIL - Could not retrieve record")
            return False
        
        # Clean up
        db.delete(test_record)
        db.commit()
        print("   OK - Cleaned up test record")
        
        db.close()
    except Exception as e:
        print(f"   FAIL - Storage error: {e}")
        return False
    
    # Test 4: AI integration
    print("\n4. Testing AI integration...")
    try:
        news_data = [{"title": "Test news", "content": "Test content"}]
        
        # This should work with the symbols parameter
        ai_result = await ai_filter_engine.analyze_market_sentiment(
            news_data=news_data,
            symbols=["RELIANCE"]
        )
        
        if ai_result["success"]:
            sentiment = ai_result["sentiment_analysis"]
            print(f"   OK - AI analysis completed, overall sentiment: {sentiment['overall_sentiment']:.2f}")
        else:
            print(f"   FAIL - AI analysis failed: {ai_result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   FAIL - AI integration error: {e}")
        return False
    
    print("\n" + "="*50)
    print("ALL TESTS PASSED - StockTwits integration is working!")
    print("="*50)
    return True


if __name__ == "__main__":
    success = asyncio.run(simple_verification())
    if not success:
        print("\nVERIFICATION FAILED!")
        exit(1)
    else:
        print("\nVERIFICATION SUCCESSFUL!")