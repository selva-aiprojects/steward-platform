"""
Comprehensive End-to-End Smoke Testing & Workflow Confirmation for StockSteward AI
Validates:
1. FinBERT Core NLP Engine (Sequence classification, softmax probabilities, and domain calibration)
2. SocialMediaService & AIFilterEngine integration
3. FastAPI HTTP REST endpoints via TestClient (/api/v1/ai/finbert/* and /api/v1/social-media/finbert/*)
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.rbac import get_current_user
from app.api.deps import get_current_active_user
from app.models.user import User
from app.engines.finbert_engine import finbert_engine
from app.services.social_media_service import social_media_service
from app.engines.ai_filter_engine import ai_filter_engine

# Mock User for HTTP dependency overrides during smoke testing
mock_user = User(
    id=1,
    email="smoke_tester@stocksteward.ai",
    full_name="Smoke Tester",
    is_active=True,
    is_superuser=True,
    role="admin"
)

app.dependency_overrides[get_current_user] = lambda: mock_user
app.dependency_overrides[get_current_active_user] = lambda: mock_user

client = TestClient(app)

def print_section(title: str):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def smoke_test_engines_and_services():
    print_section("STAGE 1: ENGINE & SERVICE WORKFLOW CONFIRMATION")
    
    # 1. FinBERT Core Text Prediction
    print("1.1 Testing FinBERT Core Text Prediction...")
    text_sample = "Operating margin expanded by 340 basis points to 22.4% following strong cost control and revenue growth."
    predictions = finbert_engine.predict_text(text_sample)
    assert len(predictions) > 0, "FinBERT engine returned empty prediction list"
    first_pred = predictions[0]
    print(f"   [PASS] Input: '{text_sample[:60]}...'")
    print(f"          Prediction: {first_pred['prediction'].upper()} (Score: {first_pred['sentiment_score']:.4f}, Confidence: {first_pred['confidence']:.4f})")
    assert first_pred['prediction'] == 'positive', "Expected positive sentiment for margin expansion"
    
    # 2. FinBERT Batched Prediction
    print("1.2 Testing FinBERT Batched Prediction...")
    batch_samples = [
        "Apple reports quarterly earnings beat with record service revenue.",
        "Severe regulatory penalties and ongoing lawsuit risks drag down shares of regional bank.",
        "The company announced a routine management presentation scheduled for next Tuesday."
    ]
    batch_res = finbert_engine.predict_batch(batch_samples)
    assert len(batch_res) == 3, f"Expected 3 batch outputs, got {len(batch_res)}"
    print(f"   [PASS] Batch of {len(batch_samples)} items processed successfully.")
    print(f"          Item 1: {batch_res[0][0]['prediction'].upper()} | Item 2: {batch_res[1][0]['prediction'].upper()} | Item 3: {batch_res[2][0]['prediction'].upper()}")
    
    # 3. FinBERT Document Analysis
    print("1.3 Testing FinBERT Document & Headline Analysis...")
    doc_res = finbert_engine.analyze_document(
        title="NVIDIA announces new AI supercomputing architecture with massive pre-order backlog",
        body="NVIDIA unveiled its next-generation Blackwell platform today. Early pre-orders from hyperscalers have already exceeded initial capacity forecasts, signaling multi-year revenue visibility."
    )
    assert doc_res['overall_label'] == 'positive', "Expected positive label for NVIDIA announcement"
    print(f"   [PASS] Document Analysis -> Overall: {doc_res['overall_label'].upper()} ({doc_res['overall_sentiment_score']:.4f})")
    print(f"          Top Bullish Catalyst: '{doc_res['top_positive_sentence'][:70]}...'")

def smoke_test_async_workflow():
    print_section("STAGE 2: ASYNC SOCIAL & MARKET SENTIMENT PIPELINE")
    
    async def _run():
        # 2.1 Social Media Post Processing
        print("2.1 Processing Social Media Post through FinBERT...")
        post_data = {
            "id": "smoke_post_001",
            "text": "$NVDA Strong institutional buying and breakout momentum at open! Target raised to $165.",
            "author": "quant_trader_ai",
            "engagement": {"likes": 120, "retweets": 45, "replies": 14}
        }
        processed_post = await social_media_service.process_social_media_post(post_data, "stocktwits")
        assert processed_post is not None, "Failed to process social post"
        assert processed_post['sentiment_label'] == 'positive', "Expected positive social post sentiment"
        print(f"   [PASS] Social Post ID: {processed_post['message_id']} by @{processed_post['author']}")
        print(f"          Sentiment: {processed_post['sentiment_label'].upper()} ({processed_post['sentiment_score']:.4f}) | Engagement Score: {processed_post['engagement_score']}")
        
        # 2.2 AIFilterEngine Market Corpus Aggregation
        print("2.2 Running AIFilterEngine Market Corpus Analysis...")
        news_items = [
            {"title": "Global tech rally continues as semiconductor demand outstrips supply."},
            {"title": "Central bank holds rates steady while expressing confidence in inflation trajectory."}
        ]
        social_items = [
            {"text": "$MSFT Azure growth accelerates, bullish accumulation spotted."},
            {"text": "$SPY holding key support level above 550 on heavy volume."}
        ]
        market_sentiment = await ai_filter_engine.analyze_market_sentiment(news_items, social_items)
        assert market_sentiment['success'] is True, "Market sentiment analysis failed"
        analysis = market_sentiment['sentiment_analysis']
        print(f"   [PASS] Market Regime: {analysis['market_regime']} | Overall Sentiment: {analysis['overall_sentiment']:.4f}")
        print(f"          News Score: {analysis['news_sentiment']:.4f} | Social Score: {analysis['social_sentiment']:.4f}")
        print(f"          Bullish Ratio: {analysis['distribution']['bullish_ratio']}% | Bearish Ratio: {analysis['distribution']['bearish_ratio']}%")
        
    asyncio.run(_run())

def smoke_test_http_endpoints():
    print_section("STAGE 3: LIVE HTTP API ENDPOINT CONFIRMATION (FastAPI TestClient)")
    
    # 3.1 Root & Health
    print("3.1 Verifying / and /health endpoints...")
    res_root = client.get("/")
    assert res_root.status_code == 200, f"Root returned {res_root.status_code}"
    print(f"   [PASS] GET / -> {res_root.json()['message']}")
    
    res_health = client.get("/health")
    assert res_health.status_code == 200, f"Health returned {res_health.status_code}"
    print(f"   [PASS] GET /health -> status: {res_health.json()['status']}")
    
    # 3.2 POST /api/v1/ai/finbert/analyze-text
    print("3.2 Verifying POST /api/v1/ai/finbert/analyze-text...")
    payload_text = {
        "text": "Tesla reports unexpected surge in vehicle deliveries, beating Wall Street consensus estimates by 12%."
    }
    res_text = client.post("/api/v1/ai/finbert/analyze-text", json=payload_text)
    assert res_text.status_code == 200, f"analyze-text returned {res_text.status_code}: {res_text.text}"
    data_text = res_text.json()
    assert data_text['overall_label'] == 'positive', f"Expected positive label, got {data_text['overall_label']}"
    print(f"   [PASS] POST /api/v1/ai/finbert/analyze-text -> Overall Label: {data_text['overall_label'].upper()} (Score: {data_text['overall_score']:.4f})")
    
    # 3.3 POST /api/v1/ai/finbert/batch-sentiment
    print("3.3 Verifying POST /api/v1/ai/finbert/batch-sentiment...")
    payload_batch = {
        "texts": [
            "Operating cash flow reached a new record high of $4.8 billion.",
            "The company warned of declining margins due to rising input costs."
        ]
    }
    res_batch = client.post("/api/v1/ai/finbert/batch-sentiment", json=payload_batch)
    assert res_batch.status_code == 200, f"batch-sentiment returned {res_batch.status_code}: {res_batch.text}"
    data_batch = res_batch.json()
    assert data_batch['total_items'] == 2, f"Expected 2 items, got {data_batch['total_items']}"
    print(f"   [PASS] POST /api/v1/ai/finbert/batch-sentiment -> Processed {data_batch['total_items']} items cleanly.")
    
    # 3.4 POST /api/v1/ai/finbert/document
    print("3.4 Verifying POST /api/v1/ai/finbert/document...")
    payload_doc = {
        "title": "Reliance Industries expands green energy investment with $10B commitment",
        "body": "The conglomerate confirmed major acquisitions across solar and hydrogen supply chains today, positioning itself as a global clean energy leader."
    }
    res_doc = client.post("/api/v1/ai/finbert/document", json=payload_doc)
    assert res_doc.status_code == 200, f"document returned {res_doc.status_code}: {res_doc.text}"
    data_doc = res_doc.json()
    assert data_doc['overall_label'] == 'positive', "Expected positive label for Reliance green investment"
    print(f"   [PASS] POST /api/v1/ai/finbert/document -> Overall: {data_doc['overall_label'].upper()} ({data_doc['overall_sentiment_score']:.4f})")
    
    # 3.5 GET /api/v1/social-media/finbert/summary/{symbol}
    print("3.5 Verifying GET /api/v1/social-media/finbert/summary/RELIANCE...")
    res_summary = client.get("/api/v1/social-media/finbert/summary/RELIANCE?hours=24")
    assert res_summary.status_code == 200, f"summary returned {res_summary.status_code}: {res_summary.text}"
    data_summary = res_summary.json()
    assert data_summary['symbol'] == 'RELIANCE', f"Expected RELIANCE, got {data_summary['symbol']}"
    print(f"   [PASS] GET /api/v1/social-media/finbert/summary/RELIANCE -> Regime: {data_summary['sentiment_regime']} | Posts Analyzed: {data_summary['total_analyzed_posts']}")

def main():
    print("\n" + "#"*70)
    print(" STARTING STOCKSTEWARD AI END-TO-END SMOKE TESTING & WORKFLOW VERIFICATION")
    print("#"*70)
    
    try:
        smoke_test_engines_and_services()
        smoke_test_async_workflow()
        smoke_test_http_endpoints()
        
        print("\n" + "#"*70)
        print(" [SUCCESS] ALL SMOKE TESTS AND WORKFLOWS CONFIRMED OPERATIONAL!")
        print("#"*70 + "\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] Smoke test encountered an error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
