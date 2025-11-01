"""
FinanceBot FastAPI Service - Chatbot API với Master Agent
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import sys
from pathlib import Path

# Ensure project root is on sys.path so `src` and `app` are importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api.routes import router
from app.core.config import get_settings
from app.monitors import create_monitor
from agents import enable_verbose_stdout_logging

enable_verbose_stdout_logging()


# Load environment variables
load_dotenv(".env", override=True)

# Initialize FastAPI app
app = FastAPI(
    title="FinanceBot API",
    description="AI-Powered Financial Analysis Chatbot with Multi-Agent System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
monitor = None
is_initialized = False


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global monitor, is_initialized
    
    try:
        print("🚀 Starting FinanceBot FastAPI Service...")
        
        # Get settings
        settings = get_settings()
        
        # Initialize monitoring
        monitor = create_monitor(settings, settings.monitoring_provider)
        if monitor.initialize():
            print("✅ Monitoring initialized")
        else:
            print("⚠️  Monitoring initialization failed, continuing without monitoring")
        
        is_initialized = True
        print("✅ FinanceBot FastAPI Service started successfully!")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        is_initialized = False


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global monitor
    
    print("🔄 Shutting down FinanceBot FastAPI Service...")
    
    if monitor:
        monitor.shutdown()
    
    print("✅ Shutdown completed")


# Include API routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
