#!/usr/bin/env python3
"""
Test script to mimic the exact API endpoint behavior
"""

import os
from dotenv import load_dotenv
load_dotenv()

from app.services.llm_service import llm_service
from app.api.deps import get_current_active_user
from app.core.database import SessionLocal
from app.models.user import User

# Simulate the API endpoint behavior
async def simulate_api_call():
    print("Simulating API endpoint behavior...")

    # Get the current user (this mimics the dependency injection)
    db = SessionLocal()
    try:
        current_user = await get_current_active_user(db)
        print(f"Current user: {current_user.email if current_user.email else current_user.id}")

        # Call the LLM service with user context (similar to how the API endpoint does it)
        user_context = f"User: {current_user.full_name}, Role: {getattr(current_user, 'trading_mode', 'MANUAL')}"
        full_context = f"{user_context}. "

        response = llm_service.get_chat_response("Hello, how are you?", full_context)
        print(f"Response: {response}")
        print(f"Is offline response?: {'Offline Intelligence' in response}")

    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(simulate_api_call())