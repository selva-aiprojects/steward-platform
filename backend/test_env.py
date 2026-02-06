#!/usr/bin/env python3
"""
Test script to verify environment variables are loaded properly
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("Environment variables from .env file:")
print(f"GROQ_API_KEY: {'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET'}")
print(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print(f"ANTHROPIC_API_KEY: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
print(f"HUGGINGFACE_API_KEY: {'SET' if os.getenv('HUGGINGFACE_API_KEY') else 'NOT SET'}")
print(f"ZERODHA_API_KEY: {'SET' if os.getenv('ZERODHA_API_KEY') else 'NOT SET'}")

# Also test the settings from the app
from app.core.config import settings
print("\nSettings from app config:")
print(f"settings.GROQ_API_KEY: {'SET' if settings.GROQ_API_KEY else 'NOT SET'}")
print(f"settings.OPENAI_API_KEY: {'SET' if settings.OPENAI_API_KEY else 'NOT SET'}")
print(f"settings.ANTHROPIC_API_KEY: {'SET' if settings.ANTHROPIC_API_KEY else 'NOT SET'}")
print(f"settings.HUGGINGFACE_API_KEY: {'SET' if settings.HUGGINGFACE_API_KEY else 'NOT SET'}")
print(f"settings.ZERODHA_API_KEY: {'SET' if settings.ZERODHA_API_KEY else 'NOT SET'}")

# Test the LLM service initialization
from app.services.llm_service import llm_service
print(f"\nLLM Service client initialized: {llm_service.client is not None}")

# Test the enhanced LLM service
from app.services.enhanced_llm_service import enhanced_llm_service
print(f"Enhanced LLM available providers: {enhanced_llm_service.get_available_providers()}")