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
    print("[SUCCESS] Libraries imported successfully.")
except ImportError as e:
    print(f"[ERROR] Error: {e}")
    sys.exit(1)

def test_kite_connection():
    api_key = os.getenv("ZERODHA_API_KEY")
    api_secret = os.getenv("ZERODHA_API_SECRET")
    access_token = os.getenv("ZERODHA_ACCESS_TOKEN")

    print(f"Testing with API Key: {api_key}")

    if not api_key:
        print("[ERROR] ZERODHA_API_KEY not found in .env")
        return

    kite = KiteConnect(api_key=api_key)

    if access_token:
        print("Using provided Access Token...")
        kite.set_access_token(access_token)
        try:
            profile = kite.profile()
            print(f"[SUCCESS] Connection successful! Logged in as: {profile['user_name']}")

            # Fetch margins as a quick check
            margins = kite.margins()
            print(f"[INFO] Available Cash: {margins['equity']['net']}")

        except Exception as e:
            print(f"[ERROR] Connection failed with Access Token: {e}")
            print("[INFO] You might need to generate a new Access Token using a Request Token.")
    else:
        print("[WARNING] ZERODHA_ACCESS_TOKEN not set in .env.")
        print(f"[INFO] Login URL: {kite.login_url()}")
        print("[INFO] Visit the URL above, login, and it will redirect to your redirect_url with a 'request_token'.")
        print("[INFO] Use that token to generate an access_token.")

if __name__ == "__main__":
    test_kite_connection()
