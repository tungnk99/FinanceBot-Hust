#!/usr/bin/env python3
"""
FinanceBot FastAPI Server Startup Script
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env", override=True)

def main():
    """Start the FastAPI server"""
    print("🚀 Starting FinanceBot FastAPI Server...")
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    print(f"📡 Server will start on: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {'Enabled' if reload else 'Disabled'}")
    print("=" * 50)
    
    # Start server
    uvicorn.run(
        "app.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
