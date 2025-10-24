"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
import sys
import os
from unittest.mock import MagicMock

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_run_context():
    """Create a mock RunContextWrapper for testing"""
    return MagicMock()


@pytest.fixture
def sample_crypto_data():
    """Sample cryptocurrency data for testing"""
    return {
        "symbol": "BTC",
        "price": 45000.0,
        "change": 1000.0,
        "percent_change": 2.27,
        "volume": 1000000,
        "market_cap": 850000000000,
        "high": 46000.0,
        "low": 44000.0,
        "source": "CoinGecko"
    }


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing"""
    return {
        "symbol": "VIC",
        "price": 85000,
        "change": 2000,
        "percent_change": 2.41,
        "volume": 5000000,
        "market_cap": 85000000000000,
        "high": 87000,
        "low": 83000,
        "source": "TCBS"
    }


@pytest.fixture
def sample_retrieval_data():
    """Sample retrieval data for testing"""
    return {
        "title": "VIC Stock Analysis",
        "content": "Vingroup Corporation stock information",
        "source": "documents",
        "timestamp": "2024-01-15T10:00:00Z",
        "confidence": 0.95,
        "snippet": "VIC shows strong performance...",
        "score": 0.9
    }
