# Troubleshooting Guide

## 🔧 Common Issues and Solutions

This guide provides solutions to common issues encountered when developing, deploying, or using FinanceBot.

## 🚀 Setup and Installation Issues

### Python Environment Issues

#### Issue: Python Version Compatibility
**Error**: `Python 3.9+ is required but found 3.8.x`

**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.9+ using pyenv
curl https://pyenv.run | bash
pyenv install 3.9.16
pyenv global 3.9.16

# Or using conda
conda create -n financebot python=3.9
conda activate financebot
```

#### Issue: Virtual Environment Problems
**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Ensure you're in the project root
cd /path/to/FinanceBot-Hust

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import app; print('App module imported successfully')"
```

#### Issue: Package Installation Failures
**Error**: `ERROR: Could not find a version that satisfies the requirement`

**Solution**:
```bash
# Update pip
pip install --upgrade pip

# Install packages individually to identify problematic ones
pip install fastapi
pip install uvicorn
pip install pydantic

# For problematic packages, try alternative versions
pip install "pydantic>=2.0,<3.0"

# Clear pip cache
pip cache purge
```

### Environment Configuration Issues

#### Issue: Environment Variables Not Loading
**Error**: `KeyError: 'OPENAI_API_KEY'`

**Solution**:
```bash
# Check if .env file exists
ls -la .env

# Create .env file from template
cp env.example .env

# Edit .env file with your values
nano .env

# Verify environment variables are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

#### Issue: API Key Validation Errors
**Error**: `Invalid API key format`

**Solution**:
```bash
# Verify OpenAI API key format
# Should start with 'sk-' and be 51 characters long
echo $OPENAI_API_KEY | wc -c  # Should be 52 (including newline)

# Test API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

## 🤖 Agent and Model Issues

### OpenAI API Issues

#### Issue: Rate Limiting
**Error**: `Rate limit exceeded. Try again in X seconds.`

**Solution**:
```python
import asyncio
import time
from openai import OpenAI

class RateLimitedClient:
    def __init__(self, api_key, max_requests_per_minute=60):
        self.client = OpenAI(api_key=api_key)
        self.max_requests = max_requests_per_minute
        self.requests = []
    
    async def make_request(self, *args, **kwargs):
        # Implement rate limiting
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = 60 - (now - self.requests[0])
            await asyncio.sleep(sleep_time)
        
        self.requests.append(now)
        return await self.client.chat.completions.create(*args, **kwargs)
```

#### Issue: Model Not Found
**Error**: `The model 'gpt-4' does not exist or you don't have access to it`

**Solution**:
```python
# Check available models
import openai
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
models = client.models.list()
available_models = [model.id for model in models.data]
print(f"Available models: {available_models}")

# Use alternative model
# In your configuration, change to available model
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4-turbo-preview
```

#### Issue: Context Length Exceeded
**Error**: `This model's maximum context length is 4096 tokens`

**Solution**:
```python
# Implement context management
class ContextManager:
    def __init__(self, max_tokens=4000):
        self.max_tokens = max_tokens
        self.messages = []
    
    def add_message(self, message):
        # Estimate token count (rough approximation)
        token_count = len(message.split()) * 1.3
        
        if self.get_total_tokens() + token_count > self.max_tokens:
            # Remove oldest messages to make room
            while self.get_total_tokens() + token_count > self.max_tokens:
                if self.messages:
                    self.messages.pop(0)
        
        self.messages.append(message)
    
    def get_total_tokens(self):
        return sum(len(msg.split()) * 1.3 for msg in self.messages)
```

### Agent Execution Issues

#### Issue: Agent Selection Failures
**Error**: `No suitable agent found for query`

**Solution**:
```python
# Debug agent selection
def debug_agent_selection(query, available_agents):
    """Debug agent selection process."""
    print(f"Query: {query}")
    print(f"Available agents: {[agent.name for agent in available_agents]}")
    
    # Check query type detection
    query_type = detect_query_type(query)
    print(f"Detected query type: {query_type}")
    
    # Check agent capabilities
    for agent in available_agents:
        confidence = calculate_confidence(query, query_type, agent.capabilities)
        print(f"Agent {agent.name}: confidence = {confidence}")
    
    # Select agent with highest confidence
    best_agent = max(available_agents, key=lambda a: calculate_confidence(query, query_type, a.capabilities))
    print(f"Selected agent: {best_agent.name}")
    
    return best_agent
```

#### Issue: Agent Execution Timeout
**Error**: `Agent execution timeout`

**Solution**:
```python
import asyncio
from asyncio import TimeoutError

async def execute_with_timeout(agent, query, timeout=30):
    """Execute agent with timeout."""
    try:
        result = await asyncio.wait_for(
            agent.execute(query),
            timeout=timeout
        )
        return result
    except TimeoutError:
        print(f"Agent {agent.name} execution timed out after {timeout} seconds")
        # Implement fallback logic
        return await fallback_agent.execute(query)
```

#### Issue: Agent Output Validation Errors
**Error**: `Pydantic validation error`

**Solution**:
```python
# Debug Pydantic validation
def debug_validation_error(model_class, data):
    """Debug Pydantic validation errors."""
    try:
        instance = model_class(**data)
        return instance
    except ValidationError as e:
        print(f"Validation errors: {e.errors()}")
        
        # Try to fix common issues
        fixed_data = fix_validation_issues(data, e.errors())
        
        try:
            return model_class(**fixed_data)
        except ValidationError as e2:
            print(f"Still has errors after fixes: {e2.errors()}")
            raise

def fix_validation_issues(data, errors):
    """Fix common validation issues."""
    fixed_data = data.copy()
    
    for error in errors:
        field = error['loc'][0] if error['loc'] else None
        error_type = error['type']
        
        if error_type == 'missing':
            # Add missing required fields with defaults
            if field == 'confidence_score':
                fixed_data['confidence_score'] = 0.0
        elif error_type == 'value_error':
            # Fix value errors
            if 'Input should be a valid number' in str(error['msg']):
                fixed_data[field] = 0.0
    
    return fixed_data
```

## 🔧 Tool and External API Issues

### Market Data API Issues

#### Issue: Yahoo Finance API Failures
**Error**: `yfinance.exceptions.YFinanceException: No data found`

**Solution**:
```python
import yfinance as yf
from typing import Optional

def safe_get_stock_data(symbol: str, period: str = "1y") -> Optional[dict]:
    """Safely get stock data with error handling."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            print(f"No data found for symbol: {symbol}")
            return None
        
        return {
            "symbol": symbol,
            "data": data,
            "current_price": data['Close'].iloc[-1],
            "volume": data['Volume'].iloc[-1]
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# Alternative data sources
def get_alternative_data(symbol: str):
    """Get data from alternative sources."""
    # Try Alpha Vantage
    try:
        return get_alpha_vantage_data(symbol)
    except:
        pass
    
    # Try IEX Cloud
    try:
        return get_iex_data(symbol)
    except:
        pass
    
    # Return cached data if available
    return get_cached_data(symbol)
```

#### Issue: API Rate Limiting
**Error**: `Too Many Requests`

**Solution**:
```python
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    """Rate limiting decorator."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_second=0.5)  # 2 seconds between calls
def call_market_api(symbol):
    """Call market API with rate limiting."""
    # API call implementation
    pass
```

### Technical Analysis Calculation Issues

#### Issue: Insufficient Data for Indicators
**Error**: `ValueError: Not enough data to calculate RSI`

**Solution**:
```python
def safe_calculate_indicators(prices, min_periods=14):
    """Safely calculate technical indicators."""
    if len(prices) < min_periods:
        print(f"Insufficient data: {len(prices)} prices, need {min_periods}")
        return None
    
    try:
        # Calculate indicators
        rsi = calculate_rsi(prices)
        macd = calculate_macd(prices)
        
        return {
            "rsi": rsi,
            "macd": macd,
            "data_points": len(prices)
        }
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return None

def get_more_historical_data(symbol, period="2y"):
    """Get more historical data for better indicator calculation."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data['Close'].tolist()
    except Exception as e:
        print(f"Error getting historical data: {e}")
        return []
```

## 🚀 Deployment Issues

### Docker Issues

#### Issue: Docker Build Failures
**Error**: `Step X/10 : RUN pip install -r requirements.txt ---> [Warning]`

**Solution**:
```dockerfile
# Optimize Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 financebot && \
    chown -R financebot:financebot /app
USER financebot

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Issue: Container Memory Issues
**Error**: `Container killed due to memory limit`

**Solution**:
```yaml
# docker-compose.yml
version: '3.8'
services:
  financebot:
    build: .
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    environment:
      - PYTHONUNBUFFERED=1
      - MALLOC_ARENA_MAX=2  # Reduce memory fragmentation
```

### FastAPI Issues

#### Issue: Application Won't Start
**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run with explicit path
PYTHONPATH=/path/to/FinanceBot-Hust uvicorn app.app:app --host 0.0.0.0 --port 8000

# Check import paths in app/app.py
# Ensure relative imports are correct
from .api.routes import router  # Not from app.api.routes
```

#### Issue: CORS Errors
**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
```python
# In app/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue: Request Timeout
**Error**: `Request timeout`

**Solution**:
```python
# Configure timeout in uvicorn
uvicorn app.app:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 60

# Or in application
import asyncio
from fastapi import Request

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=60.0)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"detail": "Request timeout"}
        )
```

## 📊 Monitoring and Logging Issues

### Langfuse Issues

#### Issue: Langfuse Connection Failures
**Error**: `Failed to connect to Langfuse`

**Solution**:
```python
# Test Langfuse connection
from langfuse import Langfuse

def test_langfuse_connection():
    """Test Langfuse connection."""
    try:
        langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        
        # Test connection
        langfuse.trace(name="test_connection")
        langfuse.flush()
        print("Langfuse connection successful")
        return True
    except Exception as e:
        print(f"Langfuse connection failed: {e}")
        return False

# Implement fallback monitoring
class FallbackMonitor:
    def __init__(self):
        self.langfuse_available = test_langfuse_connection()
    
    def trace(self, name, **kwargs):
        if self.langfuse_available:
            return self.langfuse.trace(name, **kwargs)
        else:
            return self.mock_trace(name, **kwargs)
    
    def mock_trace(self, name, **kwargs):
        """Mock trace for when Langfuse is unavailable."""
        print(f"Mock trace: {name}")
        return self
```

#### Issue: Langfuse Flush Failures
**Error**: `Failed to flush traces to Langfuse`

**Solution**:
```python
import asyncio
from typing import Optional

class RobustLangfuse:
    def __init__(self, *args, **kwargs):
        self.langfuse = Langfuse(*args, **kwargs)
        self.failed_flushes = []
    
    async def flush_with_retry(self, max_retries=3, timeout=10):
        """Flush with retry logic."""
        for attempt in range(max_retries):
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(self.langfuse.flush),
                    timeout=timeout
                )
                return True
            except Exception as e:
                print(f"Flush attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.failed_flushes.append({
                        "timestamp": time.time(),
                        "error": str(e)
                    })
        return False
    
    async def flush_periodically(self, interval=30):
        """Periodically flush traces."""
        while True:
            await self.flush_with_retry()
            await asyncio.sleep(interval)
```

### Logging Issues

#### Issue: Log Files Not Created
**Error**: `Permission denied when creating log file`

**Solution**:
```bash
# Check directory permissions
ls -la logs/
mkdir -p logs
chmod 755 logs
chown financebot:financebot logs

# Or configure logging to use different location
export LOG_DIR=/tmp/financebot-logs
mkdir -p $LOG_DIR
```

#### Issue: Log Rotation Problems
**Error**: `Log file too large`

**Solution**:
```python
import logging
import logging.handlers
import os

def setup_rotating_logger(name, log_file, max_bytes=10*1024*1024, backup_count=5):
    """Setup rotating file logger."""
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    # Create rotating file handler
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

# Usage
logger = setup_rotating_logger('financebot', 'logs/app.log')
```

## 🔍 Performance Issues

### Memory Issues

#### Issue: High Memory Usage
**Error**: `Out of memory`

**Solution**:
```python
import psutil
import gc

class MemoryMonitor:
    def __init__(self, threshold_mb=1000):
        self.threshold_mb = threshold_mb
    
    def check_memory(self):
        """Check current memory usage."""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > self.threshold_mb:
            print(f"High memory usage: {memory_mb:.2f} MB")
            self.cleanup_memory()
    
    def cleanup_memory(self):
        """Clean up memory."""
        gc.collect()  # Force garbage collection
        
        # Clear any cached data
        if hasattr(self, 'cache'):
            self.cache.clear()

# Use in application
memory_monitor = MemoryMonitor()

@app.middleware("http")
async def memory_middleware(request: Request, call_next):
    memory_monitor.check_memory()
    response = await call_next(request)
    return response
```

### Performance Optimization

#### Issue: Slow Agent Execution
**Error**: `Agent execution taking too long`

**Solution**:
```python
import time
from functools import wraps

def performance_monitor(func):
    """Monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 10:  # Log slow executions
            print(f"Slow execution: {func.__name__} took {execution_time:.2f}s")
        
        return result
    return wrapper

# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(symbol: str, period: str):
    """Cache expensive calculations."""
    # Expensive calculation here
    return result

# Use async for I/O operations
async def fetch_data_async(symbols):
    """Fetch multiple symbols concurrently."""
    tasks = [fetch_single_symbol(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## 🆘 Getting Help

### Debugging Tools

```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
def debug_agent_execution(agent, query):
    print(f"Debug: Executing {agent.name} with query: {query}")
    print(f"Debug: Agent tools: {[tool.name for tool in agent.tools]}")
    
    result = agent.execute(query)
    
    print(f"Debug: Execution result: {result}")
    print(f"Debug: Execution time: {result.execution_time}")
    
    return result
```

### Support Resources

1. **Check Logs**: Always check application logs first
2. **Environment Variables**: Verify all required environment variables are set
3. **Dependencies**: Ensure all dependencies are correctly installed
4. **API Keys**: Verify API keys are valid and have proper permissions
5. **Network Connectivity**: Check internet connection for external API calls

### Reporting Issues

When reporting issues, include:

1. **Error Message**: Complete error message and stack trace
2. **Environment**: Python version, OS, dependencies
3. **Configuration**: Relevant configuration files (without sensitive data)
4. **Steps to Reproduce**: Clear steps to reproduce the issue
5. **Expected vs Actual**: What you expected vs what actually happened
6. **Logs**: Relevant log entries around the time of the error

This troubleshooting guide covers the most common issues and provides practical solutions to resolve them quickly and effectively.
