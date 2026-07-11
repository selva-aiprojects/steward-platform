from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.core.rbac import get_current_user
from app.models.user import User
from app.services.llm_service import llm_service
from app.engines.finbert_engine import finbert_engine
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: str = ""

class ChatResponse(BaseModel):
    response: str

class MarketResearchResponse(BaseModel):
    headlines: list[str]
    sentiment: dict
    watchlist: list[dict]

async def get_live_market_data():
    """Fetch live market data to enrich AI responses"""
    try:
        # Fetch market movers (top gainers and losers)
        from app.core.state import last_market_movers
        return last_market_movers
    except Exception as e:
        logger.error(f"Error fetching live market data: {e}")
        return {"gainers": [], "losers": []}


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    # Pass user info as context if needed
    user_context = f"User: {current_user.full_name}, Role: {current_user.trading_mode}, User_ID: {current_user.id}"

    # Fetch live market data to enrich the context
    market_data = await get_live_market_data()

    # Format market data for context
    market_context_parts = []

    # Add top gainers
    if market_data.get("gainers"):
        top_gainers = market_data["gainers"][:3]  # Top 3 gainers
        gainers_str = ", ".join([f"{g['symbol']}: {g['change']}%" for g in top_gainers])
        market_context_parts.append(f"Top Gainers: {gainers_str}")

    # Add top losers
    if market_data.get("losers"):
        top_losers = market_data["losers"][:3]  # Top 3 losers
        losers_str = ", ".join([f"{l['symbol']}: {l['change']}%" for l in top_losers])
        market_context_parts.append(f"Top Losers: {losers_str}")

    # Combine all context
    market_context = " | ".join(market_context_parts) if market_context_parts else "No live market data available"

    full_context = f"{user_context}. Live Market Data: {market_context}. {request.context}"

    response = llm_service.get_chat_response(request.message, full_context)
    return ChatResponse(response=response)


@router.get("/market-research", response_model=MarketResearchResponse)
def market_research(
    current_user: User = Depends(get_current_user),
):
    """
    Lightweight market research feed for dashboards.
    Falls back to deterministic mock insights if LLM is unavailable.
    """
    try:
        prompt = (
            "Provide 4 short market research headlines and sentiment scores for India equities. "
            "Return JSON with keys: headlines (array of strings), sentiment "
            "(object with market, risk, momentum 0-100), "
            "watchlist (array of {symbol, bias, note})."
        )
        response = llm_service.get_chat_response(prompt, context="")
        import json
        data = json.loads(response)
        return data
    except Exception:
        return {
            "headlines": [
                "Nifty consolidates after strong weekly inflows",
                "Banking index shows early momentum rotation",
                "IT majors steady ahead of earnings commentary",
                "Commodities: gold stabilizes, crude softens"
            ],
            "sentiment": {"market": 62, "risk": 41, "momentum": 57},
            "watchlist": [
                {"symbol": "RELIANCE", "bias": "BUY", "note": "Institutional accumulation signal"},
                {"symbol": "TCS", "bias": "HOLD", "note": "Range-bound with stable volumes"},
                {"symbol": "HDFCBANK", "bias": "BUY", "note": "Breakout watch above 1,680"}
            ]
        }


class FinBERTAnalyzeRequest(BaseModel):
    text: str

class FinBERTBatchRequest(BaseModel):
    texts: List[str]

class FinBERTDocumentRequest(BaseModel):
    title: str
    body: Optional[str] = ""

@router.post("/finbert/analyze-text", summary="Analyze financial text using FinBERT sequence classification")
async def analyze_text_finbert(
    request: FinBERTAnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Sentence-level financial sentiment analysis exact to ProsusAI/finBERT sequence classification.
    Returns softmax probability distribution (positive, negative, neutral) and score (prob_pos - prob_neg).
    """
    try:
        results = finbert_engine.predict_text(request.text)
        avg_score = sum(r['sentiment_score'] for r in results) / len(results) if results else 0.0
        label = 'positive' if avg_score > 0.06 else 'negative' if avg_score < -0.06 else 'neutral'
        return {
            "overall_score": round(avg_score, 4),
            "overall_label": label,
            "sentence_count": len(results),
            "sentence_breakdown": results,
            "model": "ProsusAI/finbert (Financial PhraseBank sequence classification)"
        }
    except Exception as e:
        logger.error(f"Error in FinBERT text analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"FinBERT analysis failed: {str(e)}")


@router.post("/finbert/batch-sentiment", summary="Batched FinBERT sequence classification across multiple texts")
async def batch_sentiment_finbert(
    request: FinBERTBatchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run batched sequence classification over multiple tweets, headlines, or documents.
    """
    try:
        batch_results = finbert_engine.predict_batch(request.texts)
        summary = []
        for i, text in enumerate(request.texts):
            res = batch_results[i]
            score = sum(r['sentiment_score'] for r in res) / len(res) if res else 0.0
            label = 'positive' if score > 0.06 else 'negative' if score < -0.06 else 'neutral'
            summary.append({
                "index": i,
                "text_preview": text[:80] + ("..." if len(text) > 80 else ""),
                "sentiment_score": round(score, 4),
                "prediction": label,
                "sentence_count": len(res),
                "details": res
            })
        return {
            "total_items": len(request.texts),
            "batch_summary": summary,
            "model": "ProsusAI/finbert"
        }
    except Exception as e:
        logger.error(f"Error in FinBERT batch analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"FinBERT batch analysis failed: {str(e)}")


@router.post("/finbert/document", summary="Comprehensive document sentiment analysis using FinBERT")
async def analyze_document_finbert(
    request: FinBERTDocumentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates headline vs body, computes weighted sentiment score, and isolates top bullish/bearish catalysts.
    """
    try:
        doc_res = finbert_engine.analyze_document(request.title, request.body)
        return doc_res
    except Exception as e:
        logger.error(f"Error in FinBERT document analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"FinBERT document analysis failed: {str(e)}")