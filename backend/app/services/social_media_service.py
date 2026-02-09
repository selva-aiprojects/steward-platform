"""
Social Media Data Service for StockSteward AI
Handles ingestion and processing of social media data from various sources including StockTwits
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import requests
import aiohttp
from app.core.database import SessionLocal
from app.models.social_sentiment import SocialSentiment
from app.services.enhanced_llm_service import EnhancedLLMService

logger = logging.getLogger(__name__)

class SocialMediaService:
    """
    Service to handle social media data ingestion and processing
    """
    
    def __init__(self):
        self.enhanced_llm_service = EnhancedLLMService()
        self.stocktwits_api_url = "https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
        self.twitter_api_url = "https://api.twitter.com/2/tweets/search/recent"  # Placeholder
        self.reddit_api_url = "https://www.reddit.com/r/{subreddit}/search.json"  # Placeholder
        
    async def fetch_stocktwits_data(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch social media data from StockTwits for a given symbol
        """
        try:
            logger.info(f"Fetching StockTwits data for symbol: {symbol}")

            # Get API key from environment variables
            stocktwits_api_key = os.getenv("STOCKTWITS_API_KEY")

            # Construct the API URL
            url = self.stocktwits_api_url.format(symbol=symbol.upper())

            # Add API key to parameters if available
            params = {}
            if stocktwits_api_key:
                params['access_token'] = stocktwits_api_key

            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Check if the response contains messages
                        if 'messages' in data:
                            posts = []
                            for msg in data['messages']:
                                if len(posts) >= limit:
                                    break

                                # Extract message information
                                post = {
                                    "id": str(msg.get('id', '')),
                                    "message": msg.get('body', ''),
                                    "author": msg.get('user', {}).get('username', 'unknown'),
                                    "timestamp": msg.get('created_at', datetime.utcnow().isoformat()),
                                    "engagement": {
                                        "likes": msg.get('likes', {}).get('total', 0),
                                        "reshares": msg.get('reshares', {}).get('total', 0),
                                        "replies": msg.get('reply_count', 0)
                                    },
                                    "symbols": [tag.get('symbol', '') for tag in msg.get('symbols', [])]
                                }
                                posts.append(post)

                            logger.info(f"Successfully fetched {len(posts)} posts from StockTwits for {symbol}")
                            return posts
                        else:
                            logger.warning(f"No messages found in StockTwits response for {symbol}")
                            return []
                    elif response.status == 401:
                        logger.warning(f"Unauthorized access to StockTwits API for {symbol} - check API key")
                        return []
                    elif response.status == 403:
                        logger.warning(f"Forbidden access to StockTwits API for {symbol} - partner access required")
                        # The streams/symbol endpoint requires Partner-Level Access
                        # Return empty list but log the limitation
                        return []
                    elif response.status == 429:
                        logger.warning(f"Rate limit exceeded for StockTwits API for {symbol}")
                        return []
                    else:
                        logger.error(f"HTTP {response.status} error fetching StockTwits data for {symbol}")
                        return []

        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching StockTwits data for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching StockTwits data for {symbol}: {e}")
            return []
    
    async def fetch_twitter_data(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch social media data from Twitter/X for a given symbol
        """
        try:
            logger.info(f"Fetching Twitter data for symbol: {symbol}")

            # Get Twitter Bearer Token from environment variables
            twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

            if not twitter_bearer_token:
                logger.warning("TWITTER_BEARER_TOKEN not set, skipping Twitter data fetch")
                return []

            # Twitter API v2 endpoint for searching tweets
            url = "https://api.twitter.com/2/tweets/search/recent"

            headers = {
                "Authorization": f"Bearer {twitter_bearer_token}"
            }

            # Query for tweets containing the symbol (with $ prefix or as standalone)
            query = f"$${symbol} OR {symbol} lang:en"

            params = {
                "query": query,
                "max_results": min(limit, 100),  # Twitter API max is 100
                "tweet.fields": "created_at,public_metrics,author_id",
                "expansions": "author_id",
                "user.fields": "username,name"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if 'data' in data:
                            tweets = []
                            # Create a mapping of users for reference
                            users_map = {}
                            if 'includes' in data and 'users' in data['includes']:
                                for user in data['includes']['users']:
                                    users_map[user['id']] = user

                            for tweet in data['data']:
                                if len(tweets) >= limit:
                                    break

                                # Get author info
                                author_info = users_map.get(tweet.get('author_id', ''), {})
                                username = author_info.get('username', 'unknown')

                                # Extract engagement metrics
                                public_metrics = tweet.get('public_metrics', {})

                                post = {
                                    "id": tweet.get('id', ''),
                                    "text": tweet.get('text', ''),
                                    "author": username,
                                    "timestamp": tweet.get('created_at', datetime.utcnow().isoformat()),
                                    "engagement": {
                                        "likes": public_metrics.get('like_count', 0),
                                        "retweets": public_metrics.get('retweet_count', 0),
                                        "replies": public_metrics.get('reply_count', 0),
                                        "quotes": public_metrics.get('quote_count', 0)
                                    },
                                    "symbols": [symbol]  # Will need to extract from text in real implementation
                                }
                                tweets.append(post)

                            logger.info(f"Successfully fetched {len(tweets)} tweets for {symbol}")
                            return tweets
                        else:
                            logger.warning(f"No tweets found in Twitter response for {symbol}")
                            return []
                    elif response.status == 401:
                        logger.warning(f"Unauthorized access to Twitter API for {symbol} - check bearer token")
                        return []
                    elif response.status == 429:
                        logger.warning(f"Rate limit exceeded for Twitter API for {symbol}")
                        return []
                    else:
                        logger.error(f"HTTP {response.status} error fetching Twitter data for {symbol}")
                        return []

        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching Twitter data for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Twitter data for {symbol}: {e}")
            return []
    
    async def fetch_reddit_data(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch social media data from Reddit for a given symbol
        """
        try:
            logger.info(f"Fetching Reddit data for symbol: {symbol}")

            # Search in popular finance-related subreddits
            finance_subreddits = ['wallstreetbets', 'stocks', 'investing', 'securityanalysis', 'options']

            all_posts = []

            for subreddit in finance_subreddits:
                # Reddit API endpoint for searching posts
                url = f"https://www.reddit.com/r/{subreddit}/search.json"

                params = {
                    'q': symbol,
                    'limit': min(25, limit - len(all_posts)),  # Don't exceed total limit
                    'sort': 'new',
                    'restrict_sr': 'on'  # Restrict search to this subreddit
                }

                headers = {
                    'User-Agent': 'StockStewardAI/1.0 by StockStewardTeam'
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()

                            if 'data' in data and 'children' in data['data']:
                                for child in data['data']['children']:
                                    if len(all_posts) >= limit:
                                        break

                                    post = child['data']  # 'data' field contains the actual post data

                                    # Extract post information
                                    post_data = {
                                        "id": post.get('id', ''),
                                        "title": post.get('title', ''),
                                        "text": post.get('selftext', ''),
                                        "author": post.get('author', 'unknown'),
                                        "timestamp": datetime.utcfromtimestamp(post.get('created_utc', 0)).isoformat(),
                                        "engagement": {
                                            "upvotes": post.get('ups', 0),
                                            "comments": post.get('num_comments', 0),
                                            "downvotes": post.get('downs', 0)
                                        },
                                        "symbols": [symbol],  # Will need to extract from title/text in real implementation
                                        "subreddit": post.get('subreddit', subreddit)
                                    }
                                    all_posts.append(post_data)

                                if len(all_posts) >= limit:
                                    break
                        elif response.status == 429:
                            logger.warning(f"Rate limited by Reddit API for {symbol}, pausing...")
                            # Wait before trying next subreddit
                            await asyncio.sleep(2)
                        else:
                            logger.warning(f"HTTP {response.status} error fetching Reddit data from r/{subreddit} for {symbol}")

            logger.info(f"Successfully fetched {len(all_posts)} Reddit posts for {symbol}")
            return all_posts

        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching Reddit data for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Reddit data for {symbol}: {e}")
            return []
    
    async def process_social_media_post(self, post_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Process a single social media post and extract sentiment
        """
        try:
            # Extract relevant information from the post
            message_text = post_data.get('text', post_data.get('message', post_data.get('title', '')))
            if not message_text:
                return None
                
            # Calculate engagement score based on likes, shares, etc.
            engagement = post_data.get('engagement', {})
            engagement_score = (
                engagement.get('likes', 0) * 0.5 +
                engagement.get('retweets', 0) * 1.0 +
                engagement.get('replies', 0) * 0.3 +
                engagement.get('upvotes', 0) * 0.4
            )
            
            # Use LLM to analyze sentiment
            sentiment_result = await self.analyze_sentiment_with_llm(message_text)
            
            processed_post = {
                'message_id': post_data.get('id'),
                'message_text': message_text,
                'author': post_data.get('author', 'unknown'),
                'sentiment_score': sentiment_result.get('score', 0.0),
                'sentiment_label': sentiment_result.get('label', 'neutral'),
                'engagement_score': engagement_score,
                'timestamp': datetime.fromisoformat(post_data.get('timestamp', datetime.utcnow().isoformat())),
                'additional_data': post_data
            }
            
            return processed_post
            
        except Exception as e:
            logger.error(f"Error processing social media post: {e}")
            return None
    
    async def analyze_sentiment_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using LLM
        """
        try:
            # Prepare prompt for sentiment analysis
            prompt = f"""
            Analyze the sentiment of the following financial social media post:
            
            "{text}"
            
            Return a JSON object with:
            - "score": A sentiment score from -1 (very negative) to 1 (very positive)
            - "label": The sentiment label ("positive", "negative", or "neutral")
            - "confidence": Confidence level from 0 to 1
            """
            
            # Use the enhanced LLM service for sentiment analysis
            # Check if the method exists
            if hasattr(self.enhanced_llm_service, 'process_request'):
                result = await self.enhanced_llm_service.process_request(
                    prompt=prompt,
                    analysis_type="sentiment",
                    provider=None  # Use default provider
                )

                # Parse the result
                if isinstance(result, dict) and 'sentiment' in result:
                    return result['sentiment']

            # If LLM method doesn't exist or fails, use simple analysis
            return self.simple_sentiment_analysis(text)
                
        except Exception as e:
            logger.error(f"Error in LLM sentiment analysis: {e}")
            # Fallback to simple sentiment analysis
            return self.simple_sentiment_analysis(text)
    
    def simple_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Simple keyword-based sentiment analysis as fallback
        """
        text_lower = text.lower()
        
        # Positive keywords
        positive_keywords = [
            'bullish', 'buy', 'strong', 'great', 'amazing', 'profit', 'gain', 'up', 'positive', 
            'breakout', 'momentum', 'rally', 'bull', 'accummulation', 'upgrade', 'target raised'
        ]
        
        # Negative keywords
        negative_keywords = [
            'bearish', 'sell', 'weak', 'terrible', 'loss', 'crash', 'down', 'negative', 
            'dump', 'crisis', 'concern', 'decline', 'fall', 'bear', 'downgrade', 'target lowered'
        ]
        
        pos_count = sum(1 for word in positive_keywords if word in text_lower)
        neg_count = sum(1 for word in negative_keywords if word in text_lower)
        
        # Calculate sentiment score
        total_words = len(text_lower.split())
        if total_words == 0:
            score = 0.0
        else:
            score = (pos_count - neg_count) / max(1, (pos_count + neg_count + 1))
            # Normalize to -1 to 1 range
            score = max(-1.0, min(1.0, score))
        
        # Determine label
        if score > 0.1:
            label = 'positive'
        elif score < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'score': score,
            'label': label,
            'confidence': 0.6  # Default confidence for simple analysis
        }
    
    async def store_social_sentiment(self, db: Session, symbol: str, source: str, processed_post: Dict[str, Any]):
        """
        Store processed social media post in the database
        """
        try:
            # Check if this post already exists (avoid duplicates)
            existing_post = db.query(SocialSentiment).filter(
                SocialSentiment.message_id == processed_post['message_id'],
                SocialSentiment.source == source
            ).first()
            
            if existing_post:
                logger.info(f"Duplicate post found: {processed_post['message_id']}, skipping")
                return
            
            # Create new SocialSentiment record
            social_sentiment = SocialSentiment(
                symbol=symbol,
                source=source,
                message_id=processed_post['message_id'],
                message_text=processed_post['message_text'],
                author=processed_post['author'],
                sentiment_score=processed_post['sentiment_score'],
                sentiment_label=processed_post['sentiment_label'],
                engagement_score=processed_post['engagement_score'],
                timestamp=processed_post['timestamp'],
                additional_data=processed_post['additional_data']
            )
            
            db.add(social_sentiment)
            db.commit()
            db.refresh(social_sentiment)
            
            logger.info(f"Stored social sentiment for {symbol} from {source}")
            
        except IntegrityError:
            # Handle duplicate key constraint
            db.rollback()
            logger.info(f"Duplicate post found: {processed_post['message_id']}, skipping")
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing social sentiment: {e}")
    
    async def ingest_social_media_data(self, symbol: str, sources: List[str] = None):
        """
        Main method to ingest social media data for a given symbol
        """
        if sources is None:
            sources = ['stocktwits', 'twitter', 'reddit']
        
        logger.info(f"Starting social media data ingestion for {symbol} from sources: {sources}")
        
        db = SessionLocal()
        try:
            for source in sources:
                logger.info(f"Ingesting data from {source} for {symbol}")
                
                # Fetch data based on source
                if source == 'stocktwits':
                    posts = await self.fetch_stocktwits_data(symbol)
                elif source == 'twitter':
                    posts = await self.fetch_twitter_data(symbol)
                elif source == 'reddit':
                    posts = await self.fetch_reddit_data(symbol)
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue
                
                # Process and store each post
                for post in posts:
                    processed_post = await self.process_social_media_post(post, source)
                    if processed_post:
                        await self.store_social_sentiment(db, symbol, source, processed_post)
                        
                    # Small delay to avoid overwhelming the DB
                    await asyncio.sleep(0.01)
                    
        except Exception as e:
            logger.error(f"Error during social media data ingestion: {e}")
        finally:
            db.close()
    
    async def get_recent_sentiment(self, symbol: str, hours: int = 24, source: str = None) -> List[Dict[str, Any]]:
        """
        Get recent sentiment data for a symbol
        """
        db = SessionLocal()
        try:
            query = db.query(SocialSentiment).filter(
                SocialSentiment.symbol == symbol,
                SocialSentiment.timestamp >= datetime.utcnow() - timedelta(hours=hours)
            )
            
            if source:
                query = query.filter(SocialSentiment.source == source)
            
            results = query.order_by(SocialSentiment.timestamp.desc()).all()
            
            return [
                {
                    'id': r.id,
                    'message_id': r.message_id,
                    'message_text': r.message_text,
                    'author': r.author,
                    'sentiment_score': r.sentiment_score,
                    'sentiment_label': r.sentiment_label,
                    'engagement_score': r.engagement_score,
                    'timestamp': r.timestamp.isoformat(),
                    'source': r.source
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error retrieving recent sentiment for {symbol}: {e}")
            return []
        finally:
            db.close()
    
    async def get_aggregated_sentiment(self, symbol: str, hours: int = 24, source: str = None) -> Dict[str, Any]:
        """
        Get aggregated sentiment metrics for a symbol
        """
        db = SessionLocal()
        try:
            query = db.query(SocialSentiment).filter(
                SocialSentiment.symbol == symbol,
                SocialSentiment.timestamp >= datetime.utcnow() - timedelta(hours=hours)
            )
            
            if source:
                query = query.filter(SocialSentiment.source == source)
            
            results = query.all()
            
            if not results:
                return {
                    'symbol': symbol,
                    'avg_sentiment_score': 0.0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'total_posts': 0,
                    'avg_engagement_score': 0.0,
                    'timeframe_hours': hours
                }
            
            # Calculate aggregates
            sentiment_scores = [r.sentiment_score for r in results]
            engagement_scores = [r.engagement_score for r in results if r.engagement_score]
            
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0
            
            positive_count = sum(1 for r in results if r.sentiment_label == 'positive')
            negative_count = sum(1 for r in results if r.sentiment_label == 'negative')
            neutral_count = sum(1 for r in results if r.sentiment_label == 'neutral')
            
            return {
                'symbol': symbol,
                'avg_sentiment_score': avg_sentiment,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_posts': len(results),
                'avg_engagement_score': avg_engagement,
                'timeframe_hours': hours
            }
        except Exception as e:
            logger.error(f"Error calculating aggregated sentiment for {symbol}: {e}")
            return {
                'symbol': symbol,
                'avg_sentiment_score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_posts': 0,
                'avg_engagement_score': 0.0,
                'timeframe_hours': hours
            }
        finally:
            db.close()


# Global instance
social_media_service = SocialMediaService()