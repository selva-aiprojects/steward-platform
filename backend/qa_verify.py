import requests
import json
import time

BASE_URL = "http://localhost:9006/api/v1"

def log(msg):
    print(f"[QA LOG] {msg}")

def perform_qa():
    # 1. Create or Fetch 2 Users
    users = []
    for i, name in enumerate(["QA Trader Beta", "QA Trader Gamma"]):
        email = f"trader{i+1}@qa.com"
        log(f"Creating/Fetching user: {name} ({email})")
        resp = requests.post(f"{BASE_URL}/users/", json={
            "email": email,
            "full_name": name,
            "password": "password123",
            "risk_tolerance": "AGGRESSIVE" if i == 0 else "MODERATE"
        })
        
        if resp.status_code == 200:
            user = resp.json()
            users.append(user)
            log(f"User ready with ID: {user['id']}")
        elif resp.status_code == 400 and "already exists" in resp.text:
            log("User already exists, fetching existing user...")
            all_users_resp = requests.get(f"{BASE_URL}/users/")
            if all_users_resp.status_code == 200:
                found = False
                for u in all_users_resp.json():
                    if u['email'] == email:
                        users.append(u)
                        log(f"Fetched existing user with ID: {u['id']}")
                        found = True
                        break
                if not found:
                    log(f"Could not find user with email {email} in users list")
            else:
                log(f"Failed to fetch users: {all_users_resp.text}")
        else:
            log(f"Failed to process user: {resp.status_code} - {resp.text}")

    if len(users) < 2:
        log("Error: Could not prepare 2 users for QA.")
        return

    # 2. Add Funds ($50,000 for each)
    for user in users:
        log(f"Depositing $50,000 for user: {user.get('full_name', 'Unknown')}")
        resp = requests.post(f"{BASE_URL}/portfolio/deposit", json={
            "user_id": user['id'],
            "amount": 50000.0
        })
        if resp.status_code == 200:
            log("Deposit successful.")
        else:
            log(f"Deposit failed: {resp.text}")

    # 3. Buy 2 Scripts for User 1 (RELIANCE, TCS)
    user1 = users[0]
    trades = [
        {"symbol": "RELIANCE", "quantity": 50, "price": 2850.0, "action": "BUY"},
        {"symbol": "TCS", "quantity": 20, "price": 3900.0, "action": "BUY"}
    ]

    for trade_data in trades:
        log(f"User 1 ({user1.get('full_name', 'Unknown')}) buying {trade_data['quantity']} {trade_data['symbol']} @ ${trade_data['price']}")
        resp = requests.post(f"{BASE_URL}/trades/paper/order", json={ # Updated to hit the paper order endpoint which triggers agents
            "user_id": user1['id'],
            "symbol": trade_data['symbol'],
            "action": trade_data['action'],
            "quantity": trade_data['quantity'],
            "price": trade_data['price']
        })
        if resp.status_code == 200:
            res = resp.json()
            log(f"Trade Result: {res.get('status')} - Reason: {res.get('reason')}")
            # Print Trace
            for step in res.get("trace", []):
                log(f"   [AGENT] {step['step']}: {json.dumps(step['output'], indent=2)}")
        else:
            log(f"Trade failed: {resp.text}")

    # 4. Sell 1 Script for User 1 (RELIANCE)
    log(f"User 1 ({user1.get('full_name', 'Unknown')}) selling 20 RELIANCE @ $2900.0")
    resp = requests.post(f"{BASE_URL}/trades/paper/order", json={
        "user_id": user1['id'],
        "symbol": "RELIANCE",
        "action": "SELL",
        "quantity": 20,
        "price": 2900.0
    })
    if resp.status_code == 200:
        res = resp.json()
        log(f"Sell Result: {res.get('status')} - Reason: {res.get('reason')}")
    else:
        log(f"Sell failed: {resp.text}")

    # 5. Check Final Status for User 1
    log("Verifying final status for User 1...")
    
    # Check Portfolio
    port_resp = requests.get(f"{BASE_URL}/portfolio/?user_id={user1['id']}")
    if port_resp.status_code == 200:
        port_data = port_resp.json()
        port = port_data[0] if isinstance(port_data, list) and len(port_data) > 0 else port_data
        if port:
            log(f"User 1 Cash Balance: ${port.get('cash_balance')}")
            log(f"User 1 Invested Amount: ${port.get('invested_amount')}")
        else:
            log("No portfolio found for User 1")
    
    # Check Holdings
    hold_resp = requests.get(f"{BASE_URL}/portfolio/holdings?user_id={user1['id']}")
    if hold_resp.status_code == 200:
        holdings = hold_resp.json()
        log(f"User 1 Holdings: {json.dumps(holdings, indent=2)}")

if __name__ == "__main__":
    perform_qa()
