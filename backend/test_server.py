import os
import sys
sys.path.insert(0, '.')

# Set environment to paper trading to avoid API issues
os.environ['EXECUTION_MODE'] = 'PAPER_TRADING'

from app.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")