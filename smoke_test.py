import asyncio
import sys
import os
import traceback

# Ensure backend path is in sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.trade_service import TradeService

async def smoke_test():
    print("starting smoke test...")
    try:
        service = TradeService()
        
        proposal = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 10,
            "price": 150.0
        }
        
        print(f"Executing trade proposal: {proposal}")
        result = await service.execute_trade(proposal)
        
        print("\n--- Execution Result ---")
        print(f"Status: {result['status']}")
        print(f"Trace ID: {result['trace_id']}")
        
        # Validation
        if result['status'] in ["COMPLETED", "REJECTED_RISK", "EXECUTED"]:
            print("\n✅ Smoke Test PASSED: Workflow completed successfully.")
        else:
            print(f"\n❌ Smoke Test FAILED: Unexpected status '{result['status']}'")
            
        # Check trace
        print("\n--- Trace Summary ---")
        for step in result.get('trace', []):
            print(f"[{step['agent']}] -> Keys updated: {list(step['output'].keys())}")
            
    except Exception as e:
        traceback.print_exc()
        print(f"\n❌ Smoke Test FAILED with Exception: {e}")

if __name__ == "__main__":
    asyncio.run(smoke_test())
