"""
Langfuse integration for FinanceBot
Provides centralized logging and tracing for agents and tools
"""
import os
import asyncio
from typing import Optional

# Try to import Langfuse dependencies
try:
    import nest_asyncio
    import logfire
    from langfuse import get_client
    LANGFUSE_AVAILABLE = True
    print("✅ Langfuse dependencies imported successfully")
except ImportError as e:
    LANGFUSE_AVAILABLE = False
    print(f"⚠️ Langfuse dependencies not available: {e}")
    print("   Install with: pip install langfuse logfire nest-asyncio")

from src.setting import settings


class LangfuseManager:
    """Manager class for Langfuse integration"""
    
    def __init__(self):
        self.client = None
        self.is_configured = False
        
    def setup(self) -> bool:
        """Setup Langfuse integration"""
        if not LANGFUSE_AVAILABLE:
            print("❌ Langfuse not available - skipping setup")
            return False
            
        try:
            # Apply nest_asyncio for Jupyter compatibility
            nest_asyncio.apply()
            print("✅ Applied nest_asyncio")
            
            # Configure logfire
            logfire.configure(
                service_name='finance_bot_service',
                send_to_logfire=False,  # Send to Langfuse instead
            )
            print("✅ Configured logfire")
            
            # Instrument OpenAI Agents SDK
            logfire.instrument_openai_agents()
            print("✅ Instrumented OpenAI Agents SDK")
            
            # Initialize Langfuse client
            self.client = get_client()
            print("✅ Initialized Langfuse client")
            
            # Try to verify connection (skip if no credentials)
            try:
                if self.client.auth_check():
                    print("✅ Langfuse client is authenticated and ready!")
                    self.is_configured = True
                    return True
                else:
                    print("⚠️ Langfuse authentication failed, but continuing in demo mode")
                    self.is_configured = True  # Continue anyway for demo
                    return True
            except Exception as auth_e:
                print(f"⚠️ Auth check failed: {auth_e}, continuing in demo mode")
                self.is_configured = True  # Continue anyway for demo
                return True
                
        except Exception as e:
            print(f"❌ Failed to setup Langfuse: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if Langfuse is ready to use"""
        return self.is_configured and self.client is not None
    
    def get_client(self):
        """Get Langfuse client"""
        return self.client if self.is_ready() else None
    
    def flush(self):
        """Flush pending traces"""
        if self.is_ready():
            try:
                self.client.flush()
            except Exception as e:
                print(f"⚠️ Failed to flush Langfuse traces: {e}")


# Global Langfuse manager instance
langfuse_manager = LangfuseManager()


def setup_langfuse() -> bool:
    """
    Setup Langfuse integration
    Returns True if successful, False otherwise
    """
    print("🔧 Setting up Langfuse integration...")
    
    if not LANGFUSE_AVAILABLE:
        print("❌ Langfuse dependencies not available")
        return False
    
    # Check if Langfuse credentials are available
    if not settings.LANGFUSE_SECRET_KEY or not settings.LANGFUSE_PUBLIC_KEY:
        print("⚠️ Langfuse credentials not found in environment variables")
        print("   Set LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY in .env file")
        print("   For demo purposes, will setup without authentication")
        # For demo, try to setup anyway
        return langfuse_manager.setup()
    
    return langfuse_manager.setup()


def get_langfuse_client():
    """Get Langfuse client if available"""
    return langfuse_manager.get_client()


def is_langfuse_ready() -> bool:
    """Check if Langfuse is ready"""
    return langfuse_manager.is_ready()


def flush_langfuse():
    """Flush Langfuse traces"""
    langfuse_manager.flush()


# Auto-setup on import (if credentials are available)
if LANGFUSE_AVAILABLE:
    setup_langfuse()
