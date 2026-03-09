import os
import sys
import requests

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000/api/v1")
FRONTEND_URL = os.getenv("E2E_FRONTEND_URL", "http://127.0.0.1:3000")
USER_EMAIL = os.getenv("E2E_EMAIL", "admin@stocksteward.ai")
USER_PASSWORD = os.getenv("E2E_PASSWORD", "admin123")
REQUIRE_FRONTEND = os.getenv("E2E_REQUIRE_FRONTEND", "0") == "1"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def check_service_health():
    backend_ok = True
    frontend_ok = True
    log("Checking services...")
    # Backend
    try:
        r = requests.get(f"{BASE_URL}/market/status", timeout=4)
        if r.ok:
            log("Backend is reachable", "PASS")
        else:
            log(f"Backend returned {r.status_code}", "FAIL")
            backend_ok = False
    except Exception as e:
        log(f"Backend unreachable: {e}", "FAIL")
        backend_ok = False
        
    # Frontend
    try:
        r = requests.get(FRONTEND_URL, timeout=4)
        if r.ok:
            log("Frontend is reachable", "PASS")
        else:
            log(f"Frontend returned {r.status_code}", "FAIL")
            frontend_ok = False
    except Exception as e:
        log(f"Frontend unreachable: {e}", "FAIL")
        frontend_ok = False
    if REQUIRE_FRONTEND:
        return backend_ok and frontend_ok
    return backend_ok

def get_auth_token():
    log("Attempting Login...")
    try:
        r = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": USER_EMAIL, "password": USER_PASSWORD},
            timeout=10,
        )
        if not r.ok:
            log(f"Login failed for {USER_EMAIL}. Response: {r.text}", "FAIL")
            return None, None
        payload = r.json()
        token = payload.get("access_token")
        user_id = payload.get("id")
        if token:
            log("Login successful", "PASS")
            return token, user_id
        log("Login response missing access_token", "FAIL")
        return None, None
    except Exception as e:
        log(f"Login error: {e}", "FAIL")
        return None, None

def verify_flows(token, user_id):
    headers = {"Authorization": f"Bearer {token}"}
    passed = True
    
    # 1. Portfolio
    log("Verifying Portfolio Data...")
    try:
        r = requests.get(f"{BASE_URL}/portfolio/?user_id={user_id}", headers=headers, timeout=10)
        if r.ok:
            payload = r.json()
            data = payload[0] if isinstance(payload, list) and payload else {}
            log(f"Portfolio Fetch: OK. Cash: {data.get('cash_balance')}, Invested: {data.get('invested_amount')}", "PASS")
            if 'total_value' in data or isinstance(payload, list):
                 log("Portfolio payload structure OK", "PASS")
            else:
                 log("Portfolio payload structure unexpected", "FAIL")
                 passed = False
        else:
            log(f"Portfolio Fetch Failed: {r.status_code}", "FAIL")
            passed = False
    except Exception as e:
        log(f"Portfolio Error: {e}", "FAIL")
        passed = False

    # 2. Reports (Daily PnL)
    log("Verifying Reports Data (Daily PnL)...")
    try:
        r = requests.get(f"{BASE_URL}/trades/daily-pnl?user_id={user_id}", headers=headers, timeout=10)
        if r.ok:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                 log(f"Daily PnL data returned {len(data)} records", "PASS")
            else:
                 log("Daily PnL returned empty list", "WARN")
        else:
            log(f"Daily PnL Failed: {r.status_code}", "FAIL")
            passed = False
    except Exception as e:
        log(f"Reports Error: {e}", "FAIL")
        passed = False

    # 3. Strategies
    log("Verifying Strategies...")
    try:
        r = requests.get(f"{BASE_URL}/strategies/?user_id={user_id}", headers=headers, timeout=10)
        if r.ok:
            data = r.json()
            log(f"Strategies found: {len(data)}", "PASS")
        else:
            log(f"Strategies Fetch Failed: {r.status_code}", "FAIL")
            passed = False
    except Exception as e:
        log(f"Strategies Error: {e}", "FAIL")
        passed = False

    # 4. Paper Order + Idempotency
    log("Verifying Trade Submit + Idempotency...")
    try:
        trade_payload = {
            "symbol": "RELIANCE",
            "action": "BUY",
            "quantity": 1,
            "price": 2500.0,
            "user_id": user_id,
        }
        idem_headers = {**headers, "Idempotency-Key": "e2e-idem-001"}
        r1 = requests.post(f"{BASE_URL}/trades/paper/order", headers=idem_headers, json=trade_payload, timeout=20)
        r2 = requests.post(f"{BASE_URL}/trades/paper/order", headers=idem_headers, json=trade_payload, timeout=20)
        if r1.ok and r2.ok and r1.json() == r2.json():
            log("Trade idempotency check passed", "PASS")
        else:
            log("Trade idempotency check failed", "FAIL")
            passed = False
    except Exception as e:
        log(f"Trade flow error: {e}", "FAIL")
        passed = False

    return passed

def main():
    healthy = check_service_health()
    token, user_id = get_auth_token()
    if token:
        flows_ok = verify_flows(token, user_id)
    else:
        log("Skipping authenticated flows due to login failure.", "WARN")
        flows_ok = False

    if healthy and flows_ok:
        log("E2E script completed successfully", "PASS")
        sys.exit(0)
    log("E2E script completed with failures", "FAIL")
    sys.exit(1)

if __name__ == "__main__":
    main()
