import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def test_live_feed_logic():
    print("🚀 Starting Thorough Verification of Live Market Feed...")
    from app.services.kite_service import kite_service
    from app.core.config import settings
    from groq import Groq
    
    # 1. Check Configuration
    print(f"Checking Mode: {settings.EXECUTION_MODE}")
    
    # 2. Test Kite Connectivity & Symbols
    print("\n[1/3] Testing Kite Connectivity for Tickers...")
    watchlist = ['RELIANCE', 'TCS', 'INFY']
    for symbol in watchlist:
        try:
            quote = kite_service.get_quote(symbol)
            if quote:
                print(f"✅ Successfully fetched {symbol}: Price={quote['last_price']}, Change={quote['change']}%")
            else:
                print(f"❌ Failed to fetch {symbol}")
        except Exception as e:
            print(f"❌ Kite Exception for {symbol}: {e}")

    # 3. Test Groq Integration (Projection Logic)
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("\n❌ GROQ_API_KEY is missing from .env.")
    else:
        print("\n[2/3] Testing Groq AI Projection (Llama 3.1 8B)...")
        try:
            client = Groq(api_key=groq_key)
            prompt = "Provide a 1-sentence projection for RELIANCE at 2500."
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=60
            )
            print(f"✅ Groq 8B Response: {completion.choices[0].message.content.strip()}")
        except Exception as e:
            print(f"❌ Groq 8B failure: {e}")

        print("\n[3/3] Testing Global Steward Intelligence (Llama 3.3 70B)...")
        try:
            client = Groq(api_key=groq_key)
            summary = "RELIANCE: 1.5%, TCS: -0.5%, INFY: 0.2%"
            prompt = f"Summarize Nifty trend in one punchy expert sentence based on: {summary}."
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=100
            )
            print(f"✅ Groq 70B Response: {completion.choices[0].message.content.strip()}")
        except Exception as e:
            print(f"❌ Groq 70B failure: {e}")

    print("\n✨ Verification Script Complete.")

if __name__ == "__main__":
    asyncio.run(test_live_feed_logic())
