"""
Social Media Sentiment Data Model for StockSteward AI
Stores sentiment data from various social media sources including StockTwits
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from app.core.database import Base


class SocialSentiment(Base):
    """
    Model to store social media sentiment data
    """
    __tablename__ = "social_sentiment"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)  # Stock symbol
    source = Column(String, index=True, nullable=False)  # Source: 'stocktwits', 'twitter', 'reddit', etc.
    message_id = Column(String, unique=True, nullable=False)  # Unique ID from the source
    message_text = Column(Text, nullable=False)  # The actual social media post
    author = Column(String, nullable=True)  # Author of the post
    sentiment_score = Column(Float, nullable=True)  # Calculated sentiment score (-1 to 1)
    sentiment_label = Column(String, nullable=True)  # Sentiment label: 'positive', 'negative', 'neutral'
    engagement_score = Column(Float, nullable=True)  # Engagement metric (likes, retweets, etc.)
    timestamp = Column(DateTime, nullable=False)  # Timestamp of the post
    processed_at = Column(DateTime, default=datetime.utcnow)  # When it was processed
    additional_data = Column(JSON, nullable=True)  # Additional metadata from the source
    
    # Relationship to user who might have analyzed this
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="social_sentiments")

    def __repr__(self):
        return f"<SocialSentiment(symbol='{self.symbol}', source='{self.source}', sentiment={self.sentiment_score})>"


# Add relationship to User model
def extend_user_model(User):
    """Extend the existing User model with social sentiment relationship"""
    User.social_sentiments = relationship("SocialSentiment", back_populates="user", lazy="dynamic")