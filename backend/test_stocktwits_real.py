import asyncio
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the backend directory to the path
sys.path.insert(0, '.')

from app.services.social_media_service import social_media_service

async def test_aapl():
    print('Testing AAPL with updated StockTwits service...')
    result = await social_media_service.fetch_stocktwits_data('AAPL', limit=5)
    print(f'Result type: {type(result)}')
    print(f'Number of posts: {len(result)}')
    if result:
        for i, post in enumerate(result[:2]):  # Show first 2 posts
            print(f'Post {i+1}: Message ID: {post.get("id")}')
            print(f'         Message: {post.get("message", "")[:100]}...')
            print(f'         Author: {post.get("author")}')
            print(f'         Timestamp: {post.get("timestamp")}')
    else:
        print('No results returned - this could be due to API access restrictions or network issues')

if __name__ == "__main__":
    asyncio.run(test_aapl())