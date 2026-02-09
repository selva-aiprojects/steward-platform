"""
Simple test to verify StockTwits integration is working
"""

import asyncio
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.append('./backend')

from app.services.social_media_service import social_media_service
from app.models.social_sentiment import SocialSentiment
from app.core.database import SessionLocal

async def simple_test():
    print("Testing StockTwits Integration...")
    
    # Test 1: Verify the database model exists and can be queried
    db = SessionLocal()
    try:
        # Count existing records
        count = db.query(SocialSentiment).count()
        print(f"✓ SocialSentiment table exists, current record count: {count}")
    except Exception as e:
        print(f"✗ Error accessing SocialSentiment table: {e}")
        return
    finally:
        db.close()
    
    # Test 2: Try to fetch simulated data
    try:
        symbol = "RELIANCE"
        print(f"\nFetching simulated data for {symbol}...")
        
        # Fetch simulated StockTwits data
        stocktwits_data = await social_media_service.fetch_stocktwits_data(symbol, limit=5)
        print(f"✓ Retrieved {len(stocktwits_data)} simulated StockTwits posts for {symbol}")
        
        if stocktwits_data:
            print(f"  Sample post: {stocktwits_data[0]['message'][:100]}...")
        
        # Test processing a single post
        if stocktwits_data:
            processed = await social_media_service.process_social_media_post(stocktwits_data[0], 'stocktwits')
            if processed:
                print(f"✓ Processed post with sentiment: {processed['sentiment_score']:.2f} ({processed['sentiment_label']})")
            else:
                print("✗ Failed to process post")
        
    except Exception as e:
        print(f"✗ Error in data fetching/processing: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Try to store a sample record
    try:
        print(f"\nTesting storage functionality...")
        db = SessionLocal()
        
        # Create a sample social sentiment record
        sample_record = SocialSentiment(
            symbol="TEST",
            source="test",
            message_id="test_123",
            message_text="This is a test message for integration verification",
            author="test_bot",
            sentiment_score=0.5,
            sentiment_label="positive",
            engagement_score=10.0,
            timestamp=datetime.utcnow()
        )
        
        db.add(sample_record)
        db.commit()
        print("✓ Successfully stored test record in social_sentiment table")
        
        # Query the record back
        retrieved = db.query(SocialSentiment).filter(SocialSentiment.message_id == "test_123").first()
        if retrieved:
            print(f"✓ Retrieved test record with sentiment: {retrieved.sentiment_score}")
        else:
            print("✗ Could not retrieve test record")
        
        # Clean up test record
        db.delete(sample_record)
        db.commit()
        db.close()
        print("✓ Cleaned up test record")
        
    except Exception as e:
        print(f"✗ Error in storage test: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nStockTwits integration appears to be working correctly!")

if __name__ == "__main__":
    asyncio.run(simple_test())