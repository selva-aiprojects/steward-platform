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

@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
):
    # Pass user info as context if needed
    user_context = f"User: {current_user.full_name}, Role: {current_user.trading_mode}"
    full_context = f"{user_context}. {request.context}"
    
    response = llm_service.get_chat_response(request.message, full_context)
    return ChatResponse(response=response)
