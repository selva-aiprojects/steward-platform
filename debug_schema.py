
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.schemas.trade import TradeProposal, TradeResult
from pydantic import ValidationError

print("--- Debugging TradeProposal ---")
payload = {
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 10,
    "request_id": "test-regression-001"
}
try:
    p = TradeProposal(**payload)
    print("✅ TradeProposal Request Valid")
except ValidationError as e:
    print(f"❌ TradeProposal Failed: {e}")

print("\n--- Debugging TradeResult ---")
# Simulate what TradeService returns
response_data = {
    "status": "EXECUTED",
    "reason": "Trade executed successfully",
    "trace_id": "12345",
    "execution_result": {"order_id": "999"},
    "trace": [],
    "risk_score": None # or 10
}

try:
    r = TradeResult(**response_data)
    print("✅ TradeResult Response Valid")
except ValidationError as e:
    print(f"❌ TradeResult Failed: {e}")
