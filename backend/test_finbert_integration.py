"""
Verification script for FinBERT Financial NLP & Sentiment Engine Integration
"""

import sys
import os
import asyncio
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.engines.finbert_engine import finbert_engine
from app.services.social_media_service import social_media_service
from app.engines.ai_filter_engine import ai_filter_engine

def test_finbert_core():
    print("=== Testing FinBERT Core Sequence Classification ===")
    
    # Financial PhraseBank style examples
    examples = [
        "Operating profit rose 15% to $45.2 million due to strong demand and cost reductions.",
        "The company reported a severe quarterly loss of $12M and downgraded its revenue forecast.",
        "The board of directors scheduled the annual shareholder meeting for October 14th."
    ]
    
    for ex in examples:
        res = finbert_engine.predict_text(ex)
        print(f"Sentence: {ex}")
        for r in res:
            print(f" -> Prediction: {r['prediction'].upper()} | Score: {r['sentiment_score']:.4f} | Probabilities: {r['probabilities']}")
        print()
        
    assert len(res) > 0, "Failed to get FinBERT prediction"
    print("[PASS] Core FinBERT prediction passed.\n")

def test_document_analysis():
    print("=== Testing FinBERT Document & Headline Analysis ===")
    headline = "Apple shares surge 5% following record earnings beat and dividend increase"
    body = "Apple posted record revenue for Q3, driven by iPhone 16 sales in Asian markets. However, the company noted slight supply chain headwinds going into the holiday quarter. Overall cash flow expanded substantially."
    
    doc_res = finbert_engine.analyze_document(headline, body)
    print(f"Headline: {doc_res['headline']}")
    print(f"Overall Label: {doc_res['overall_label'].upper()} ({doc_res['overall_sentiment_score']:.4f})")
    print(f"Top Positive Catalyst: {doc_res['top_positive_sentence']}")
    print(f"Top Negative Catalyst: {doc_res['top_negative_sentence']}")
    assert doc_res['overall_label'] == 'positive', "Document should be classified as positive overall"
    print("[PASS] Document analysis passed.\n")

async def test_social_and_filter_engines():
    print("=== Testing Social Media Post Processing with FinBERT ===")
    mock_post = {
        "id": "100123",
        "text": "$NVDA Bullish breakout happening now! Massive volume and target raised to $160.",
        "author": "alphatrader",
        "engagement": {"likes": 45, "retweets": 12, "replies": 5}
    }
    
    processed = await social_media_service.process_social_media_post(mock_post, "stocktwits")
    print("Processed Post Summary:")
    print(f"ID: {processed['message_id']} | Author: {processed['author']}")
    print(f"Sentiment Label: {processed['sentiment_label'].upper()} ({processed['sentiment_score']:.4f})")
    print(f"Engagement Score: {processed['engagement_score']}")
    print(f"Model Engine: {processed['additional_data'].get('model_engine')}")
    assert processed['sentiment_label'] == 'positive', "Social post should be positive"
    print("[PASS] SocialMediaService FinBERT integration passed.\n")
    
    print("=== Testing AIFilterEngine Market Corpus Analysis ===")
    news_items = [
        {"title": "Fed signals potential interest rate cuts as inflation moderates to target levels."},
        {"title": "Tech sector leads market rally; semiconductor stocks jump on strong AI demand."}
    ]
    social_items = [
        {"text": "$SPY strong buyers entering at support level, looking for new all-time highs."},
        {"text": "$AAPL slight consolidation after earnings run, holding steady."}
    ]
    
    market_sentiment = await ai_filter_engine.analyze_market_sentiment(news_items, social_items)
    analysis = market_sentiment['sentiment_analysis']
    print(f"Overall Market Sentiment: {analysis['overall_sentiment']:.4f}")
    print(f"Market Regime: {analysis['market_regime']}")
    print(f"News Sentiment: {analysis['news_sentiment']:.4f} | Social Sentiment: {analysis['social_sentiment']:.4f}")
    print(f"Bullish Ratio: {analysis['distribution']['bullish_ratio']}%")
    assert market_sentiment['success'], "AIFilterEngine analysis failed"
    print("[PASS] AIFilterEngine FinBERT integration passed.\n")

if __name__ == "__main__":
    test_finbert_core()
    test_document_analysis()
    asyncio.run(test_social_and_filter_engines())
    print("All FinBERT integration verification tests passed successfully!")
