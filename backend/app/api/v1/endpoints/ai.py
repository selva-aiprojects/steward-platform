from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.llm_service import llm_service

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

@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
):
    # Pass user info as context if needed
    user_context = f"User: {current_user.full_name}, Role: {current_user.trading_mode}, User_ID: {current_user.id}"
    full_context = f"{user_context}. {request.context}"

    response = llm_service.get_chat_response(request.message, full_context)
    return ChatResponse(response=response)


@router.get("/market-research", response_model=MarketResearchResponse)
def market_research(
    current_user: User = Depends(get_current_active_user),
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