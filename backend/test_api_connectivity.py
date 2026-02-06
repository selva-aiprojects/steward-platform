#!/usr/bin/env python3
"""
Test script to verify API connectivity
"""

import os
from dotenv import load_dotenv
load_dotenv()

from app.services.llm_service import llm_service
from app.services.enhanced_llm_service import enhanced_llm_service
import asyncio

async def test_api_connectivity():
    print("Testing API connectivity...")
    
    # Test basic LLM service
    print(f"\nBasic LLM Service:")
    print(f"Client initialized: {llm_service.client is not None}")
    
    if llm_service.client:
        try:
            # Test a simple API call
            from groq import InternalServerError
            response = llm_service.client.chat.completions.create(
                messages=[{"role": "user", "content": "Test"}],
                model="llama-3.3-70b-versatile",
                max_tokens=5
            )
            print(f"Groq API call successful: {response is not None}")
        except Exception as e:
            print(f"Groq API call failed: {e}")
    
    # Test enhanced LLM service
    print(f"\nEnhanced LLM Service:")
    available_providers = enhanced_llm_service.get_available_providers()
    print(f"Available providers: {available_providers}")
    
    for provider in available_providers:
        try:
            test_result = await enhanced_llm_service.test_connection(provider)
            print(f"{provider} connection test: {test_result}")
        except Exception as e:
            print(f"{provider} connection test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_connectivity())