#!/usr/bin/env python3
"""
Debug script to check what's happening in the LLM service
"""

import os
from dotenv import load_dotenv
load_dotenv()

from app.services.llm_service import llm_service

print("Testing LLM service directly...")

# Test the get_chat_response method directly
try:
    response = llm_service.get_chat_response("Hello, how are you?")
    print(f"Response: {response}")
    print(f"Is offline response?: {'Offline Intelligence' in response}")
except Exception as e:
    print(f"Exception occurred: {e}")
    import traceback
    traceback.print_exc()