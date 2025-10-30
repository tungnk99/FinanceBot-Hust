#!/usr/bin/env python3
"""
FinanceBot FastAPI Server Startup Script
"""
import os
import sys
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env", override=True)

# Ensure project root is on sys.path so `app` is importable when running by path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import FastAPI app directly to avoid module string import issues
from app.main import app as fastapi_app

def main():
    """Start the FastAPI server"""
    print("🚀 Starting FinanceBot FastAPI Server...")
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = False
    
    uvicorn.run(
            fastapi_app,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )

if __name__ == "__main__":
    main()
