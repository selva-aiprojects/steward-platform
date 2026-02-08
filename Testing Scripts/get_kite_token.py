import os
import sys
from dotenv import load_dotenv
from kiteconnect import KiteConnect

# Load environment variables from .env
load_dotenv()

def generate_access_token(request_token):
    api_key = os.getenv("ZERODHA_API_KEY")
    api_secret = os.getenv("ZERODHA_API_SECRET")

    if not api_key or not api_secret:
        print("❌ Error: ZERODHA_API_KEY or ZERODHA_API_SECRET missing in .env")
        return

    kite = KiteConnect(api_key=api_key)
    
    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        print(f"\n✅ Access Token generated successfully!")
        print(f"User ID: {data['user_id']}")
        print(f"Access Token: {access_token}")
        print("\n--- ACTION REQUIRED ---")
        print(f"Please add the following line to your .env file:")
        print(f"ZERODHA_ACCESS_TOKEN={access_token}")
    except Exception as e:
        print(f"❌ Failed to generate session: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_kite_token.py <request_token>")
    else:
        generate_access_token(sys.argv[1])
