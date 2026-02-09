import asyncio
import sys
import os
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the backend directory to the path
sys.path.insert(0, '.')

from app.services.social_media_service import social_media_service

async def test_ingestion():
    print('Testing social media ingestion for AAPL...')
    
    # Test Reddit data fetching specifically
    print('\\nTesting Reddit data fetch...')
    reddit_data = await social_media_service.fetch_reddit_data('AAPL', limit=3)
    print(f'Reddit data fetched: {len(reddit_data)} posts')
    
    if reddit_data:
        for i, post in enumerate(reddit_data[:2]):
            title = post.get("title", "")
            print(f'Reddit Post {i+1}: {title[:80]}...')
    
    # Test ingestion
    print('\\nStarting ingestion...')
    await social_media_service.ingest_social_media_data('AAPL', sources=['reddit'])
    print('Ingestion completed')

if __name__ == '__main__':
    asyncio.run(test_ingestion())