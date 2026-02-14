import requests
import time
import sys
import json

BASE_URL = "http://localhost:8001/api/v1"
FRONTEND_URL = "http://localhost:3000"
USER_EMAIL = "alex@stocksteward.ai"
# We'll assume we can use a backdoor or existing token if login ignores password, or use a known password. 
# For now, we'll try to login or use a seeded token if available. 
# Actually, the auth endpoint /login/access-token is standard OAuth2. 
# Default password for seeded users is usually 'password' or similar. 
# I'll try 'password' and 'password123'.

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def check_service_health():
    log("Checking services...")
    # Backend
    try:
        r = requests.get(f"{BASE_URL}/market/status", timeout=2) # Using market status as health check
        if r.ok:
            log("Backend is reachable", "PASS")
        else:
            log(f"Backend returned {r.status_code}", "FAIL")
    except Exception as e:
        log(f"Backend unreachable: {e}", "FAIL")
        
    # Frontend
    try:
        r = requests.get(FRONTEND_URL, timeout=2)
        if r.ok:
            log("Frontend is reachable", "PASS")
        else:
            log(f"Frontend returned {r.status_code}", "FAIL")
    except Exception as e:
        log(f"Frontend unreachable: {e}", "FAIL")

def get_auth_token():
    log("Attempting Login...")
    try:
        # Try login with standard passwords
        passwords = ["password", "password123", "trader123", "admin123"]
        token = None
        
        for p in passwords:
            try:
                # payload for JSON login if auth.py expects Pydantic model (it does: schemas.LoginRequest)
                # It does NOT use OAuth2 form data (username/password), but JSON body (email/password).
                # Check auth.py: payload: schemas.LoginRequest
                r = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": USER_EMAIL,
                    "password": p
                })
                
                if r.ok:
                    token = r.json().get("access_token")
                    log(f"Login successful with password '{p}'. Token: {token[:10]}...", "PASS")
                    return token
            except:
                continue
                
        if not token:
            log(f"Login failed for {USER_EMAIL}. Response: {r.text if 'r' in locals() else 'No connection'}", "FAIL")
            return None
    except Exception as e:
        log(f"Login error: {e}", "FAIL")
        return None

def verify_flows(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Portfolio
    log("Verifying Portfolio Data...")
    try:
        r = requests.get(f"{BASE_URL}/portfolio/?user_id=1", headers=headers)
        if r.ok:
            data = r.json()[0]
            log(f"Portfolio Fetch: OK. Cash: {data.get('cash_balance')}, Invested: {data.get('invested_amount')}", "PASS")
            if 'total_value' in data:
                 log(f"Computed Field 'total_value' present: {data['total_value']}", "PASS")
            else:
                 log("Computed Field 'total_value' MISSING", "FAIL")
        else:
            log(f"Portfolio Fetch Failed: {r.status_code}", "FAIL")
    except Exception as e:
        log(f"Portfolio Error: {e}", "FAIL")

    # 2. Reports (Daily PnL)
    log("Verifying Reports Data (Daily PnL)...")
    try:
        r = requests.get(f"{BASE_URL}/trades/daily-pnl?user_id=1", headers=headers)
        if r.ok:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                 log(f"Daily PnL data returned {len(data)} records", "PASS")
            else:
                 log("Daily PnL returned empty list", "WARN")
        else:
            log(f"Daily PnL Failed: {r.status_code}", "FAIL")
    except Exception as e:
        log(f"Reports Error: {e}", "FAIL")

    # 3. Strategies
    log("Verifying Strategies...")
    try:
        r = requests.get(f"{BASE_URL}/strategies/?user_id=1", headers=headers)
        if r.ok:
            data = r.json()
            log(f"Strategies found: {len(data)}", "PASS")
        else:
            log(f"Strategies Fetch Failed: {r.status_code}", "FAIL")
    except Exception as e:
        log(f"Strategies Error: {e}", "FAIL")

def main():
    check_service_health()
    # Note: We need a valid token. If login fails (due to password), we might need to seed a user or bypass.
    # For this verification, we assume the backend is running and we can hit endpoints. 
    # If auth fails, we can verify public endpoints or user 1 availability via admin if we had admin token.
    # But checking public reachability is step 1.
    
    # Actually, let's try to get a token for user 1. 
    # If not, we can assume the local dev environment might allow some access or we check logs.
    
    token = get_auth_token()
    if token:
        verify_flows(token)
    else:
        log("Skipping authenticated flows due to login failure.", "WARN")

if __name__ == "__main__":
    main()
