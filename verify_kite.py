import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from kiteconnect import KiteConnect
    from app.core.config import settings
    print("✅ Libraries imported successfully.")
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

def test_kite_connection():
    api_key = os.getenv("ZERODHA_API_KEY")
    api_secret = os.getenv("ZERODHA_API_SECRET")
    access_token = os.getenv("ZERODHA_ACCESS_TOKEN")

    print(f"Testing with API Key: {api_key}")
    
    if not api_key:
        print("❌ ZERODHA_API_KEY not found in .env")
        return

    kite = KiteConnect(api_key=api_key)
    
    if access_token:
        print("Using provided Access Token...")
        kite.set_access_token(access_token)
        try:
            profile = kite.profile()
            print(f"✅ Connection successful! Logged in as: {profile['user_name']}")
            
            # Fetch margins as a quick check
            margins = kite.margins()
            print(f"💰 Available Cash: {margins['equity']['net']}")
            
        except Exception as e:
            print(f"❌ Connection failed with Access Token: {e}")
            print("💡 You might need to generate a new Access Token using a Request Token.")
    else:
        print("⚠️ ZERODHA_ACCESS_TOKEN not set in .env.")
        print(f"🔗 Login URL: {kite.login_url()}")
        print("💡 Visit the URL above, login, and it will redirect to your redirect_url with a 'request_token'.")
        print("💡 Use that token to generate an access_token.")

if __name__ == "__main__":
    test_kite_connection()
