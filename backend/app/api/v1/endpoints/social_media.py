from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.social_media_service import social_media_service
from app.core.database import SessionLocal

router = APIRouter()

class SocialSentimentResponse(BaseModel):
    id: int
    message_id: str
    message_text: str
    author: str
    sentiment_score: float
    sentiment_label: str
    engagement_score: float
    timestamp: str
    source: str

class AggregatedSentimentResponse(BaseModel):
    symbol: str
    avg_sentiment_score: float
    positive_count: int
    negative_count: int
    neutral_count: int
    total_posts: int
    avg_engagement_score: float
    timeframe_hours: int

class IngestionRequest(BaseModel):
    symbol: str
    sources: List[str] = ["stocktwits", "twitter", "reddit"]

@router.post("/ingest", summary="Ingest social media data for a symbol")
async def ingest_social_media_data(
    request: IngestionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Ingest social media data from specified sources for a given symbol
    """
    try:
        await social_media_service.ingest_social_media_data(
            symbol=request.symbol,
            sources=request.sources
        )
        return {
            "message": f"Successfully initiated ingestion for {request.symbol}",
            "symbol": request.symbol,
            "sources": request.sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting social media data: {str(e)}")


@router.get("/recent/{symbol}", response_model=List[SocialSentimentResponse], summary="Get recent social sentiment for a symbol")
async def get_recent_sentiment(
    symbol: str,
    hours: int = Query(24, description="Number of hours to look back"),
    source: Optional[str] = Query(None, description="Filter by source (stocktwits, twitter, reddit)"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get recent social media sentiment for a given symbol
    """
    try:
        sentiment_data = await social_media_service.get_recent_sentiment(
            symbol=symbol,
            hours=hours,
            source=source
        )
        return sentiment_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sentiment data: {str(e)}")


@router.get("/aggregate/{symbol}", response_model=AggregatedSentimentResponse, summary="Get aggregated sentiment for a symbol")
async def get_aggregated_sentiment(
    symbol: str,
    hours: int = Query(24, description="Number of hours to look back"),
    source: Optional[str] = Query(None, description="Filter by source (stocktwits, twitter, reddit)"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get aggregated social media sentiment metrics for a given symbol
    """
    try:
        aggregated_data = await social_media_service.get_aggregated_sentiment(
            symbol=symbol,
            hours=hours,
            source=source
        )
        return aggregated_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving aggregated sentiment: {str(e)}")


@router.get("/trending", response_model=List[dict], summary="Get trending symbols based on social media activity")
async def get_trending_symbols(
    hours: int = Query(24, description="Number of hours to look back"),
    limit: int = Query(10, description="Number of trending symbols to return"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get trending symbols based on social media activity and sentiment
    """
    try:
        # This would typically query the database for most discussed symbols
        # For now, we'll return a simulated response
        db = SessionLocal()
        try:
            from sqlalchemy import func
            from app.models.social_sentiment import SocialSentiment
            
            # Get symbols with most posts in the last N hours
            trending_query = db.query(
                SocialSentiment.symbol,
                func.count(SocialSentiment.id).label('post_count'),
                func.avg(SocialSentiment.sentiment_score).label('avg_sentiment')
            ).filter(
                SocialSentiment.timestamp >= datetime.utcnow() - timedelta(hours=hours)
            ).group_by(SocialSentiment.symbol).order_by(
                func.count(SocialSentiment.id).desc()
            ).limit(limit)
            
            results = trending_query.all()
            
            trending_symbols = [
                {
                    'symbol': r.symbol,
                    'post_count': r.post_count,
                    'avg_sentiment': float(r.avg_sentiment) if r.avg_sentiment else 0.0,
                    'sentiment_label': 'positive' if r.avg_sentiment and r.avg_sentiment > 0.1 else 'negative' if r.avg_sentiment and r.avg_sentiment < -0.1 else 'neutral'
                }
                for r in results
            ]
            
            return trending_symbols
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trending symbols: {str(e)}")