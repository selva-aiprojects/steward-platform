"""
Test script to verify the complete deposit workflow
"""
import requests
import time
import subprocess
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_deposit_workflow():
    """Test the complete deposit workflow"""
    print("Testing deposit workflow...")
    
    # Wait a moment for the server to start if it's not already running
    time.sleep(2)
    
    # Test deposit endpoint
    base_url = "http://localhost:8000"
    
    # Test deposit functionality
    deposit_data = {
        "user_id": 1,
        "amount": 5000.0
    }
    
    print(f"Testing deposit with user_id: {deposit_data['user_id']}")
    try:
        deposit_response = requests.post(f"{base_url}/api/v1/portfolio/deposit", json=deposit_data)
        print(f"Deposit response status: {deposit_response.status_code}")
        print(f"Deposit response: {deposit_response.text}")
        
        if deposit_response.status_code in [200, 201]:
            print("SUCCESS: Deposit endpoint is working correctly!")
            deposit_result = deposit_response.json()
            print(f"Deposit result: {deposit_result}")
            return True
        else:
            print(f"FAILURE: Deposit failed with status {deposit_response.status_code}")
            return False
    except Exception as e:
        print(f"Error during deposit test: {e}")
        return False

def run_cypress_tests():
    """Run Cypress tests for the deposit workflow"""
    print("\nRunning Cypress tests for deposit workflow...")
    
    try:
        # Change to frontend directory
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
        os.chdir(frontend_dir)
        
        # Run Cypress tests
        result = subprocess.run([
            "npx", "cypress", "run", 
            "--spec", "cypress/e2e/features.cy.js"
        ], capture_output=True, text=True, timeout=300)
        
        print("Cypress test stdout:")
        print(result.stdout)
        print("\nCypress test stderr:")
        print(result.stderr)
        print(f"\nCypress test exit code: {result.returncode}")
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Cypress tests timed out")
        return False
    except Exception as e:
        print(f"Error running Cypress tests: {e}")
        return False

if __name__ == "__main__":
    print("Starting comprehensive deposit workflow test...")
    
    # Test the deposit API endpoint
    api_success = test_deposit_workflow()
    
    if api_success:
        print("\nSUCCESS: API deposit workflow is functioning correctly")
    else:
        print("\nFAILURE: API deposit workflow has issues")
    
    # Run Cypress tests
    os.chdir(os.path.dirname(__file__))  # Go back to backend directory first
    cypress_success = run_cypress_tests()
    
    if cypress_success:
        print("\nSUCCESS: Cypress tests passed")
    else:
        print("\nFAILURE: Cypress tests failed")
    
    overall_success = api_success and cypress_success
    
    if overall_success:
        print("\nSUCCESS: All deposit workflow tests passed!")
    else:
        print("\nFAILURE: Some deposit workflow tests failed")
    
    sys.exit(0 if overall_success else 1)