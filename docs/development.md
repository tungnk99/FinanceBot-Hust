# Development Guidelines

## 🛠️ Development Environment Setup

### Prerequisites

- Python 3.9+
- pip or poetry for package management
- Git for version control
- Docker (optional, for containerized development)

### Environment Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd FinanceBot-Hust
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Verify installation**
```bash
make test
```

## 📁 Project Structure

```
FinanceBot-Hust/
├── app/                    # FastAPI application
│   ├── api/               # API routes and endpoints
│   ├── core/              # Core configuration
│   ├── schemas/           # Pydantic models
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── app.py             # FastAPI app instance
├── src/                   # Core application logic
│   ├── agents/            # AI agents
│   │   ├── planner_agents/    # Master agent
│   │   ├── specialist_agents/ # Domain-specific agents
│   │   └── task_agents/       # Task-specific agents
│   ├── tools/             # Tools and utilities
│   ├── memory/            # Memory management
│   └── models/            # Data models
├── tests/                 # Test files
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── Makefile             # Development commands
└── README.md            # Project documentation
```

## 🎯 Coding Standards

### Python Style Guide

We follow PEP 8 with some project-specific modifications:

#### Code Formatting
- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **String quotes**: Double quotes for strings, single quotes for string literals in code
- **Imports**: Grouped and sorted (stdlib, third-party, local)

#### Import Organization
```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Local imports
from app.schemas.requests import ChatRequest
from app.services.chat_service import ChatService
```

#### Type Hints
Always use type hints for function parameters and return values:

```python
def process_request(
    message: str,
    query_type: Optional[str] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """Process user request and return formatted response."""
    # Implementation
    return {"success": True, "data": result}
```

#### Docstrings
Use Google-style docstrings:

```python
def analyze_stock_data(
    symbol: str,
    timeframe: str = "1Y",
    indicators: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyze stock data with technical indicators.
    
    Args:
        symbol: Stock symbol to analyze (e.g., 'AAPL')
        timeframe: Analysis timeframe ('1D', '1W', '1M', '1Y')
        indicators: List of technical indicators to calculate
        
    Returns:
        Dictionary containing analysis results with keys:
        - metrics: Technical indicators values
        - signals: Trading signals
        - recommendations: Investment recommendations
        
    Raises:
        ValueError: If symbol format is invalid
        DataError: If market data is unavailable
    """
    # Implementation
```

### Pydantic Models

#### Schema Design
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    message: str = Field(..., description="User message", min_length=1, max_length=1000)
    query_type: Optional[str] = Field(default=None, description="Query type for agent selection")
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is the current price of AAPL?",
                "query_type": "market_search",
                "priority": "normal"
            }
        }
```

#### Validation Rules
- Use `Field()` for all model fields with descriptions
- Use `Optional[]` for nullable fields
- Use `Field(default_factory=list)` for list defaults
- Use `pattern=` for regex validation (not `regex=` in Pydantic v2)
- Provide examples in `Config.json_schema_extra`

### Error Handling

#### Exception Hierarchy
```python
# Custom exceptions
class FinanceBotError(Exception):
    """Base exception for FinanceBot errors."""
    pass

class AgentError(FinanceBotError):
    """Raised when agent execution fails."""
    pass

class ToolError(FinanceBotError):
    """Raised when tool execution fails."""
    pass

class ValidationError(FinanceBotError):
    """Raised when input validation fails."""
    pass
```

#### Error Handling Pattern
```python
async def process_request(request: ChatRequest) -> ChatResponse:
    """Process chat request with proper error handling."""
    try:
        # Validate input
        if not request.message.strip():
            raise ValidationError("Message cannot be empty")
        
        # Process request
        result = await master_agent.process(request.message)
        
        # Format response
        return ChatResponse(
            success=True,
            message_id=generate_message_id(),
            response=result
        )
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except AgentError as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail="Agent execution failed")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 🤖 Agent Development

### Agent Structure

#### Base Agent Pattern
```python
from agents import Agent, AgentOutputSchema
from pydantic import BaseModel, Field
from typing import Dict, Any, List

class AgentResponse(BaseModel):
    """Response schema for agent."""
    
    result: Dict[str, Any] = Field(..., description="Analysis result")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "result": {"price": 150.25, "change": 2.15},
                "confidence_score": 0.85,
                "recommendations": ["Monitor for breakout", "Consider profit-taking"]
            }
        }

# Agent instructions
AGENT_PROMPT = """
You are a specialized financial analysis agent.

## Capabilities:
- Analyze financial data
- Provide investment insights
- Generate recommendations

## Guidelines:
- Always provide confidence scores
- Include risk assessments
- Use professional terminology
"""

# Create agent
my_agent = Agent(
    name="MyAgent",
    instructions=AGENT_PROMPT,
    output_type=AgentOutputSchema(AgentResponse, strict_json_schema=False),
    tools=[tool1, tool2, tool3],
    model="gpt-4"
)
```

#### Tool Integration
```python
from agents import function_tool

@function_tool
def analyze_technical_indicators(
    symbol: str,
    timeframe: str = "1Y",
    indicators: List[str] = ["RSI", "MACD", "SMA"]
) -> Dict[str, Any]:
    """
    Analyze technical indicators for a stock.
    
    Args:
        symbol: Stock symbol to analyze
        timeframe: Analysis timeframe
        indicators: List of indicators to calculate
        
    Returns:
        Dictionary with indicator values and signals
    """
    # Implementation
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "indicators": indicator_data,
        "signals": trading_signals
    }

# Add tool to agent
my_agent = Agent(
    name="TechnicalAgent",
    instructions=AGENT_PROMPT,
    tools=[analyze_technical_indicators],
    # ... other parameters
)
```

### Agent Testing

#### Unit Tests
```python
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.specialist_agents.quant_agent import quant_agent

@pytest.mark.asyncio
async def test_quant_agent_technical_analysis():
    """Test quantitative agent technical analysis."""
    
    # Mock external dependencies
    with patch('src.tools.stock_market.get_realtime_market_data') as mock_data:
        mock_data.return_value = {
            "symbol": "AAPL",
            "price": 150.25,
            "volume": 1000000
        }
        
        # Test agent execution
        result = await quant_agent.run("Analyze AAPL technical indicators")
        
        # Assertions
        assert result.final_output.symbol == "AAPL"
        assert result.final_output.confidence_score > 0
        assert len(result.final_output.metrics) > 0
```

#### Integration Tests
```python
@pytest.mark.asyncio
async def test_master_agent_workflow():
    """Test complete master agent workflow."""
    
    # Test request
    request = "What is the technical analysis for AAPL?"
    
    # Execute through master agent
    result = await master_agent.process_request(request)
    
    # Verify agent selection
    assert result.selected_agent.agent_name == "quant_agent"
    assert result.selected_agent.confidence_score > 0.7
    
    # Verify execution result
    assert result.execution_result is not None
    assert result.success is True
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/                  # Unit tests
│   ├── agents/           # Agent unit tests
│   ├── tools/            # Tool unit tests
│   └── services/         # Service unit tests
├── integration/          # Integration tests
│   ├── api/              # API integration tests
│   └── workflows/        # End-to-end workflow tests
├── fixtures/             # Test fixtures and data
└── conftest.py          # Pytest configuration
```

### Test Categories

#### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Fast execution (< 1 second per test)
- High coverage (> 90%)

#### Integration Tests
- Test component interactions
- Use real external services (with test data)
- Moderate execution time (< 10 seconds per test)
- Focus on critical paths

#### End-to-End Tests
- Test complete user workflows
- Use production-like environment
- Longer execution time acceptable
- Focus on user scenarios

### Test Data Management

#### Fixtures
```python
# conftest.py
import pytest
from app.schemas.requests import ChatRequest

@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return ChatRequest(
        message="Analyze AAPL stock",
        query_type="stock_research",
        session_id="test_session_123"
    )

@pytest.fixture
def mock_market_data():
    """Mock market data for testing."""
    return {
        "symbol": "AAPL",
        "price": 150.25,
        "change": 2.15,
        "percent_change": 1.45,
        "volume": 1000000
    }
```

#### Test Database
```python
@pytest.fixture(scope="session")
def test_db():
    """Create test database for integration tests."""
    # Setup test database
    yield test_db
    # Cleanup after tests
```

### Mocking Guidelines

#### External API Calls
```python
from unittest.mock import patch, AsyncMock

@patch('src.tools.stock_market.requests.get')
def test_market_data_fetch(mock_get):
    """Test market data fetching with mocked API."""
    
    # Configure mock response
    mock_response = Mock()
    mock_response.json.return_value = {"price": 150.25}
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    # Test function
    result = get_market_data("AAPL")
    
    # Assertions
    assert result["price"] == 150.25
    mock_get.assert_called_once()
```

#### Async Functions
```python
@pytest.mark.asyncio
async def test_async_agent_execution():
    """Test async agent execution."""
    
    # Mock async function
    with patch('src.agents.master_agent.process_request', new_callable=AsyncMock) as mock_process:
        mock_process.return_value = {"success": True, "data": "test"}
        
        # Test async execution
        result = await test_function()
        
        # Verify async call
        mock_process.assert_awaited_once()
```

## 📊 Performance Guidelines

### Async Programming

#### Use Async/Await
```python
# Good: Async function
async def fetch_market_data(symbol: str) -> Dict[str, Any]:
    """Fetch market data asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/stock/{symbol}") as response:
            return await response.json()

# Bad: Synchronous blocking call
def fetch_market_data(symbol: str) -> Dict[str, Any]:
    """Fetch market data synchronously (blocking)."""
    response = requests.get(f"https://api.example.com/stock/{symbol}")
    return response.json()
```

#### Concurrent Execution
```python
import asyncio

async def analyze_multiple_stocks(symbols: List[str]) -> List[Dict[str, Any]]:
    """Analyze multiple stocks concurrently."""
    
    # Create tasks for concurrent execution
    tasks = [analyze_single_stock(symbol) for symbol in symbols]
    
    # Execute concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

### Caching Strategy

#### Response Caching
```python
from functools import lru_cache
import asyncio

# Synchronous caching
@lru_cache(maxsize=128)
def get_stock_info(symbol: str) -> Dict[str, Any]:
    """Get stock information with caching."""
    # Expensive computation or API call
    return stock_data

# Async caching (manual implementation)
_cache = {}

async def get_market_data_cached(symbol: str) -> Dict[str, Any]:
    """Get market data with async caching."""
    
    if symbol in _cache:
        return _cache[symbol]
    
    # Fetch data
    data = await fetch_market_data(symbol)
    
    # Cache for 5 minutes
    _cache[symbol] = data
    asyncio.create_task(expire_cache_entry(symbol, 300))
    
    return data
```

### Memory Management

#### Resource Cleanup
```python
class DataProcessor:
    """Data processor with proper resource cleanup."""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def process_data(self, data: List[str]) -> List[str]:
        """Process data with session."""
        # Use self.session for processing
        pass

# Usage
async def main():
    async with DataProcessor() as processor:
        result = await processor.process_data(data)
    # Session automatically closed
```

## 🔍 Logging and Monitoring

### Logging Configuration

#### Structured Logging
```python
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
    format='%(message)s'
)

logger = logging.getLogger(__name__)
logger.handlers[0].setFormatter(StructuredFormatter())
```

#### Logging Best Practices
```python
# Good: Structured logging with context
logger.info(
    "Agent execution completed",
    extra={
        "agent_name": "quant_agent",
        "symbol": "AAPL",
        "execution_time": 1.5,
        "confidence_score": 0.85
    }
)

# Good: Error logging with context
try:
    result = await agent.execute(task)
except Exception as e:
    logger.error(
        "Agent execution failed",
        extra={
            "agent_name": agent.name,
            "task": task,
            "error_type": type(e).__name__
        },
        exc_info=True
    )
    raise

# Bad: Unstructured logging
logger.info(f"Agent {agent_name} completed for {symbol}")
```

### Performance Monitoring

#### Execution Time Tracking
```python
import time
from functools import wraps

def track_execution_time(func):
    """Decorator to track function execution time."""
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed",
                extra={
                    "execution_time": execution_time,
                    "status": "success"
                }
            )
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(
                f"Function {func.__name__} failed",
                extra={
                    "execution_time": execution_time,
                    "status": "error",
                    "error": str(e)
                }
            )
            raise
    
    return async_wrapper

# Usage
@track_execution_time
async def analyze_stock(symbol: str) -> Dict[str, Any]:
    """Analyze stock with execution time tracking."""
    # Implementation
    pass
```

## 🚀 Deployment Guidelines

### Environment Configuration

#### Environment Variables
```python
# app/core/config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # Monitoring
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: Optional[str] = None
    
    # Database
    database_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

#### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Best Practices

#### Input Validation
```python
from pydantic import validator
import re

class ChatRequest(BaseModel):
    """Chat request with input validation."""
    
    message: str = Field(..., min_length=1, max_length=1000)
    
    @validator('message')
    def validate_message(cls, v):
        """Validate message content."""
        # Remove potentially harmful content
        v = re.sub(r'<script.*?</script>', '', v, flags=re.DOTALL)
        v = v.strip()
        
        if not v:
            raise ValueError('Message cannot be empty after sanitization')
        
        return v
```

#### API Key Management
```python
import os
from cryptography.fernet import Fernet

class APIKeyManager:
    """Secure API key management."""
    
    def __init__(self):
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        self.cipher = Fernet(self.encryption_key.encode())
    
    def encrypt_key(self, api_key: str) -> str:
        """Encrypt API key."""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt API key."""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

## 📝 Code Review Guidelines

### Review Checklist

#### Functionality
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance is acceptable

#### Code Quality
- [ ] Code follows style guidelines
- [ ] Functions are well-documented
- [ ] Type hints are present
- [ ] No code duplication

#### Testing
- [ ] Unit tests are present
- [ ] Tests cover edge cases
- [ ] Integration tests if needed
- [ ] Test coverage is adequate

#### Security
- [ ] Input validation is present
- [ ] No sensitive data exposure
- [ ] Authentication/authorization if needed
- [ ] No security vulnerabilities

### Review Process

1. **Self Review**: Author reviews own code before submission
2. **Peer Review**: At least one team member reviews the code
3. **Automated Checks**: CI/CD pipeline runs automated tests and linting
4. **Approval**: Code is approved by reviewer before merge

This comprehensive development guide ensures consistent, high-quality code across the FinanceBot project.
