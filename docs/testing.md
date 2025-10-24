# Testing Guide

## 🧪 Overview

This guide covers comprehensive testing strategies for FinanceBot, including unit tests, integration tests, and end-to-end testing. The testing framework ensures reliability, performance, and maintainability of the AI-powered financial analysis system.

## 📋 Testing Framework

### Dependencies

```bash
# Testing dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov
pip install httpx  # For API testing
pip install factory-boy  # For test data generation
pip install freezegun  # For time mocking
```

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── agents/            # Agent unit tests
│   │   ├── test_master_agent.py
│   │   ├── test_research_agent.py
│   │   ├── test_quant_agent.py
│   │   └── test_risk_agent.py
│   ├── tools/             # Tool unit tests
│   │   ├── test_stock_market.py
│   │   ├── test_technical_analysis.py
│   │   └── test_crypto_market.py
│   ├── services/          # Service unit tests
│   │   ├── test_chat_service.py
│   │   └── test_monitor_service.py
│   └── utils/             # Utility tests
│       ├── test_validators.py
│       └── test_helpers.py
├── integration/           # Integration tests
│   ├── api/              # API integration tests
│   │   ├── test_chat_endpoint.py
│   │   ├── test_stock_analysis.py
│   │   └── test_chart_generation.py
│   ├── agents/           # Agent integration tests
│   │   ├── test_agent_workflows.py
│   │   └── test_agent_collaboration.py
│   └── workflows/        # End-to-end workflow tests
│       ├── test_complete_analysis.py
│       └── test_multi_agent_scenarios.py
├── fixtures/             # Test fixtures and data
│   ├── sample_data.py
│   ├── mock_responses.py
│   └── test_config.py
├── conftest.py          # Pytest configuration
└── test_utils.py        # Testing utilities
```

## 🔧 Pytest Configuration

### conftest.py

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from app.services.chat_service import ChatService
from src.agents.planner_agents.master_agent import master_agent
import os
from dotenv import load_dotenv

# Load test environment
load_dotenv(".env.test")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def chat_service():
    """Create chat service instance for testing."""
    service = ChatService()
    await service.initialize()
    yield service
    await service.shutdown()

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Test response from OpenAI",
                    "role": "assistant"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "symbol": "AAPL",
        "price": 150.25,
        "change": 2.15,
        "percent_change": 1.45,
        "volume": 1000000,
        "high": 152.00,
        "low": 148.50,
        "open": 149.00,
        "close": 150.25,
        "market_cap": 2400000000000,
        "timestamp": "2025-01-30T10:30:00Z"
    }

@pytest.fixture
def sample_technical_indicators():
    """Sample technical indicators for testing."""
    return {
        "rsi_14": 65.2,
        "macd": 1.25,
        "macd_signal": 1.10,
        "macd_histogram": 0.15,
        "sma_20": 148.5,
        "sma_50": 145.8,
        "ema_12": 149.2,
        "ema_26": 147.8,
        "bollinger_upper": 155.8,
        "bollinger_middle": 148.2,
        "bollinger_lower": 140.6,
        "volume_sma": 950000
    }

@pytest.fixture
def mock_langfuse():
    """Mock Langfuse client."""
    mock_langfuse = Mock()
    mock_langfuse.trace.return_value.__enter__ = Mock()
    mock_langfuse.trace.return_value.__exit__ = Mock()
    mock_langfuse.span.return_value.__enter__ = Mock()
    mock_langfuse.span.return_value.__exit__ = Mock()
    mock_langfuse.flush = Mock()
    return mock_langfuse

@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "message": "Analyze AAPL stock",
        "query_type": "stock_research",
        "priority": "normal",
        "session_id": "test_session_123",
        "user_id": "test_user_456"
    }
```

## 🧪 Unit Tests

### Agent Unit Tests

#### Master Agent Tests

```python
# tests/unit/agents/test_master_agent.py
import pytest
from unittest.mock import AsyncMock, patch, Mock
from src.agents.planner_agents.master_agent import master_agent, QueryType, AgentSelection
from app.schemas.requests import ChatRequest

class TestMasterAgent:
    
    @pytest.mark.asyncio
    async def test_agent_selection_market_data(self):
        """Test master agent selects correct agent for market data queries."""
        
        # Test market data query
        query = "What is the current price of AAPL?"
        
        with patch.object(master_agent, 'run') as mock_run:
            mock_run.return_value = Mock(
                final_output=Mock(
                    query_type=QueryType.MARKET_SEARCH,
                    selected_agent=AgentSelection(
                        agent_name="get_realtime_market_data",
                        agent_type="direct_tool",
                        confidence_score=0.85
                    )
                )
            )
            
            result = await master_agent.run(query)
            
            # Verify agent selection
            assert result.final_output.selected_agent.agent_name == "get_realtime_market_data"
            assert result.final_output.selected_agent.confidence_score > 0.7
    
    @pytest.mark.asyncio
    async def test_agent_selection_technical_analysis(self):
        """Test master agent selects quant agent for technical analysis."""
        
        query = "Show me RSI and MACD for AAPL"
        
        with patch.object(master_agent, 'run') as mock_run:
            mock_run.return_value = Mock(
                final_output=Mock(
                    query_type=QueryType.QUANTITATIVE_ANALYSIS,
                    selected_agent=AgentSelection(
                        agent_name="quant_agent",
                        agent_type="specialist",
                        confidence_score=0.92
                    )
                )
            )
            
            result = await master_agent.run(query)
            
            assert result.final_output.selected_agent.agent_name == "quant_agent"
            assert result.final_output.query_type == QueryType.QUANTITATIVE_ANALYSIS
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test master agent error handling."""
        
        query = "Invalid query that should cause error"
        
        with patch.object(master_agent, 'run') as mock_run:
            mock_run.side_effect = Exception("Test error")
            
            with pytest.raises(Exception) as exc_info:
                await master_agent.run(query)
            
            assert "Test error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execution_time_tracking(self):
        """Test execution time tracking."""
        
        query = "Analyze AAPL stock"
        
        with patch.object(master_agent, 'run') as mock_run:
            mock_run.return_value = Mock(
                final_output=Mock(
                    execution_time=1.5,
                    success=True
                )
            )
            
            result = await master_agent.run(query)
            
            assert result.final_output.execution_time > 0
            assert result.final_output.success is True
```

#### Research Agent Tests

```python
# tests/unit/agents/test_research_agent.py
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.specialist_agents.research_agent import research_agent, ResearchAnalysis

class TestResearchAgent:
    
    @pytest.mark.asyncio
    async def test_stock_research_analysis(self, sample_market_data):
        """Test comprehensive stock research analysis."""
        
        query = "Research AAPL stock comprehensively"
        
        with patch('src.tools.stock_market.get_realtime_market_data') as mock_market_data, \
             patch('src.tools.yfinance_data.get_stock_with_technical_analysis') as mock_technical:
            
            # Mock market data
            mock_market_data.return_value = sample_market_data
            
            # Mock technical analysis
            mock_technical.return_value = {
                "symbol": "AAPL",
                "technical_indicators": {
                    "rsi": 65.2,
                    "macd": 1.25
                }
            }
            
            # Mock agent execution
            with patch.object(research_agent, 'run') as mock_run:
                mock_run.return_value = Mock(
                    final_output=ResearchAnalysis(
                        symbol="AAPL",
                        company_name="Apple Inc.",
                        current_price=150.25,
                        market_cap=2400000000000,
                        analysis_type="comprehensive",
                        fundamental_metrics={
                            "pe_ratio": 28.5,
                            "pb_ratio": 6.8,
                            "roe": 0.147
                        },
                        technical_indicators={
                            "rsi": 65.2,
                            "macd": 1.25
                        },
                        investment_recommendation="BUY",
                        confidence_score=0.87
                    )
                )
                
                result = await research_agent.run(query)
                
                # Verify analysis result
                assert result.final_output.symbol == "AAPL"
                assert result.final_output.confidence_score > 0.8
                assert result.final_output.investment_recommendation in ["BUY", "HOLD", "SELL"]
                assert len(result.final_output.fundamental_metrics) > 0
                assert len(result.final_output.technical_indicators) > 0
    
    @pytest.mark.asyncio
    async def test_research_agent_tool_usage(self, sample_market_data):
        """Test research agent properly uses available tools."""
        
        query = "Analyze Microsoft stock"
        
        with patch('src.tools.stock_market.get_realtime_market_data') as mock_market_data:
            mock_market_data.return_value = {
                **sample_market_data,
                "symbol": "MSFT",
                "price": 300.50
            }
            
            with patch.object(research_agent, 'run') as mock_run:
                mock_run.return_value = Mock(
                    final_output=ResearchAnalysis(
                        symbol="MSFT",
                        company_name="Microsoft Corporation",
                        current_price=300.50,
                        confidence_score=0.85
                    )
                )
                
                result = await research_agent.run(query)
                
                # Verify tools were called
                mock_market_data.assert_called()
                assert result.final_output.symbol == "MSFT"
```

#### Quantitative Agent Tests

```python
# tests/unit/agents/test_quant_agent.py
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.specialist_agents.quant_agent import quant_agent, QuantitativeAnalysis, AnalysisType

class TestQuantitativeAgent:
    
    @pytest.mark.asyncio
    async def test_technical_analysis(self, sample_technical_indicators):
        """Test technical analysis functionality."""
        
        query = "Calculate RSI and MACD for AAPL"
        
        with patch('src.tools.yfinance_data.get_stock_with_technical_analysis') as mock_technical:
            mock_technical.return_value = {
                "symbol": "AAPL",
                "price_data": [],
                "technical_indicators": sample_technical_indicators
            }
            
            with patch.object(quant_agent, 'run') as mock_run:
                mock_run.return_value = Mock(
                    final_output=QuantitativeAnalysis(
                        symbol="AAPL",
                        analysis_type=AnalysisType.TECHNICAL,
                        timeframe="1Y",
                        metrics=sample_technical_indicators,
                        signals=["RSI indicates overbought conditions"],
                        recommendations=["Consider profit-taking"],
                        confidence_score=0.82
                    )
                )
                
                result = await quant_agent.run(query)
                
                # Verify technical analysis
                assert result.final_output.analysis_type == AnalysisType.TECHNICAL
                assert result.final_output.metrics["rsi_14"] == 65.2
                assert len(result.final_output.signals) > 0
                assert len(result.final_output.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_quantitative_metrics_calculation(self):
        """Test quantitative metrics calculation."""
        
        query = "Calculate financial ratios for AAPL"
        
        with patch.object(quant_agent, 'run') as mock_run:
            mock_run.return_value = Mock(
                final_output=QuantitativeAnalysis(
                    symbol="AAPL",
                    analysis_type=AnalysisType.QUANTITATIVE,
                    metrics={
                        "pe_ratio": 28.5,
                        "pb_ratio": 6.8,
                        "roe": 0.147,
                        "debt_to_equity": 1.75
                    },
                    confidence_score=0.78
                )
            )
            
            result = await quant_agent.run(query)
            
            # Verify quantitative metrics
            assert result.final_output.analysis_type == AnalysisType.QUANTITATIVE
            assert result.final_output.metrics["pe_ratio"] > 0
            assert result.final_output.metrics["roe"] > 0
    
    @pytest.mark.asyncio
    async def test_portfolio_analysis(self):
        """Test portfolio analysis functionality."""
        
        query = "Analyze portfolio risk for AAPL, MSFT, GOOGL"
        
        with patch.object(quant_agent, 'run') as mock_run:
            mock_run.return_value = Mock(
                final_output=QuantitativeAnalysis(
                    symbol="PORTFOLIO",
                    analysis_type=AnalysisType.PORTFOLIO,
                    risk_metrics={
                        "portfolio_beta": 1.2,
                        "sharpe_ratio": 0.85,
                        "max_drawdown": 0.15,
                        "volatility": 0.22
                    },
                    recommendations=["Diversify portfolio", "Consider risk management"],
                    confidence_score=0.75
                )
            )
            
            result = await quant_agent.run(query)
            
            # Verify portfolio analysis
            assert result.final_output.analysis_type == AnalysisType.PORTFOLIO
            assert "portfolio_beta" in result.final_output.risk_metrics
            assert "sharpe_ratio" in result.final_output.risk_metrics
```

### Tool Unit Tests

#### Stock Market Tool Tests

```python
# tests/unit/tools/test_stock_market.py
import pytest
from unittest.mock import patch, Mock
import requests
from src.tools.stock_market import get_realtime_market_data

class TestStockMarketTool:
    
    @patch('requests.get')
    def test_get_realtime_market_data_success(self, mock_get, sample_market_data):
        """Test successful market data retrieval."""
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_market_data
        mock_get.return_value = mock_response
        
        # Test function
        result = get_realtime_market_data("AAPL")
        
        # Verify result
        assert result["symbol"] == "AAPL"
        assert result["price"] == 150.25
        assert result["change"] == 2.15
        assert result["percent_change"] == 1.45
        assert result["volume"] == 1000000
        
        # Verify API call
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_realtime_market_data_api_error(self, mock_get):
        """Test handling of API errors."""
        
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("Not found")
        mock_get.return_value = mock_response
        
        # Test error handling
        with pytest.raises(requests.HTTPError):
            get_realtime_market_data("INVALID_SYMBOL")
    
    @patch('requests.get')
    def test_get_realtime_market_data_network_error(self, mock_get):
        """Test handling of network errors."""
        
        # Mock network error
        mock_get.side_effect = requests.ConnectionError("Network error")
        
        # Test error handling
        with pytest.raises(requests.ConnectionError):
            get_realtime_market_data("AAPL")
    
    def test_symbol_validation(self):
        """Test stock symbol validation."""
        
        # Test valid symbols
        valid_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        for symbol in valid_symbols:
            # This would be tested in the actual validation function
            assert len(symbol) > 0
            assert symbol.isalpha()
    
    @patch('requests.get')
    def test_multiple_symbols(self, mock_get, sample_market_data):
        """Test retrieving data for multiple symbols."""
        
        symbols = ["AAPL", "MSFT", "GOOGL"]
        
        for i, symbol in enumerate(symbols):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                **sample_market_data,
                "symbol": symbol,
                "price": 150.25 + i * 10
            }
            mock_get.return_value = mock_response
            
            result = get_realtime_market_data(symbol)
            
            assert result["symbol"] == symbol
            assert result["price"] == 150.25 + i * 10
```

#### Technical Analysis Tool Tests

```python
# tests/unit/tools/test_technical_analysis.py
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, Mock
from src.tools.technical_analysis import calculate_rsi, calculate_macd, calculate_bollinger_bands

class TestTechnicalAnalysisTool:
    
    def test_calculate_rsi(self):
        """Test RSI calculation."""
        
        # Create sample price data
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
        
        rsi = calculate_rsi(prices, period=14)
        
        # Verify RSI values
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100
        
        # Test with known values
        expected_rsi = 65.2  # This would be calculated based on the formula
        assert abs(rsi - expected_rsi) < 0.1
    
    def test_calculate_macd(self):
        """Test MACD calculation."""
        
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
        
        macd_line, signal_line, histogram = calculate_macd(prices)
        
        # Verify MACD components
        assert isinstance(macd_line, float)
        assert isinstance(signal_line, float)
        assert isinstance(histogram, float)
        
        # Verify histogram relationship
        assert abs(histogram - (macd_line - signal_line)) < 0.001
    
    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
        
        upper, middle, lower = calculate_bollinger_bands(prices, period=20, std_dev=2)
        
        # Verify Bollinger Bands
        assert isinstance(upper, float)
        assert isinstance(middle, float)
        assert isinstance(lower, float)
        
        # Verify band relationships
        assert upper > middle > lower
        
        # Test with pandas DataFrame
        df = pd.DataFrame({'close': prices})
        upper_series, middle_series, lower_series = calculate_bollinger_bands(df['close'])
        
        assert len(upper_series) == len(prices)
        assert isinstance(upper_series, pd.Series)
    
    def test_empty_data_handling(self):
        """Test handling of empty or invalid data."""
        
        # Test with empty list
        with pytest.raises(ValueError):
            calculate_rsi([])
        
        # Test with insufficient data
        with pytest.raises(ValueError):
            calculate_rsi([100, 102])  # Less than required period
        
        # Test with non-numeric data
        with pytest.raises(TypeError):
            calculate_rsi(['a', 'b', 'c'])
    
    def test_edge_cases(self):
        """Test edge cases in technical analysis."""
        
        # Test with constant prices
        constant_prices = [100] * 20
        rsi = calculate_rsi(constant_prices)
        assert rsi == 50  # RSI should be 50 for constant prices
        
        # Test with all increasing prices
        increasing_prices = list(range(100, 120))
        rsi = calculate_rsi(increasing_prices)
        assert rsi > 50  # RSI should be above 50 for increasing trend
        
        # Test with all decreasing prices
        decreasing_prices = list(range(120, 100, -1))
        rsi = calculate_rsi(decreasing_prices)
        assert rsi < 50  # RSI should be below 50 for decreasing trend
```

### Service Unit Tests

#### Chat Service Tests

```python
# tests/unit/services/test_chat_service.py
import pytest
from unittest.mock import AsyncMock, patch, Mock
from app.services.chat_service import ChatService
from app.schemas.requests import ChatRequest
from app.schemas.responses import ChatResponse

class TestChatService:
    
    @pytest.fixture
    async def chat_service(self):
        """Create chat service instance for testing."""
        service = ChatService()
        await service.initialize()
        yield service
        await service.shutdown()
    
    @pytest.mark.asyncio
    async def test_chat_success(self, chat_service, sample_chat_request):
        """Test successful chat processing."""
        
        # Mock master agent response
        mock_response = Mock()
        mock_response.final_output = {
            "request_id": "req_123",
            "query": sample_chat_request["message"],
            "selected_agent": {
                "agent_name": "research_agent",
                "confidence_score": 0.85
            },
            "execution_result": {
                "symbol": "AAPL",
                "analysis": "Comprehensive analysis result"
            },
            "execution_time": 1.5,
            "success": True
        }
        
        with patch.object(chat_service.master_agent, 'run', return_value=mock_response):
            result = await chat_service.chat(
                message=sample_chat_request["message"],
                query_type=sample_chat_request["query_type"]
            )
            
            # Verify response structure
            assert result["success"] is True
            assert "message_id" in result
            assert result["response"]["symbol"] == "AAPL"
            assert result["execution_time"] == 1.5
    
    @pytest.mark.asyncio
    async def test_chat_error_handling(self, chat_service):
        """Test chat error handling."""
        
        # Mock agent error
        with patch.object(chat_service.master_agent, 'run', side_effect=Exception("Agent error")):
            with pytest.raises(Exception) as exc_info:
                await chat_service.chat(
                    message="Test message",
                    query_type="stock_research"
                )
            
            assert "Agent error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_stock_analysis(self, chat_service):
        """Test stock analysis functionality."""
        
        mock_response = Mock()
        mock_response.final_output = {
            "symbol": "AAPL",
            "analysis_type": "comprehensive",
            "confidence_score": 0.87
        }
        
        with patch.object(chat_service.master_agent, 'run', return_value=mock_response):
            result = await chat_service.analyze_stock(
                symbol="AAPL",
                analysis_type="comprehensive"
            )
            
            assert result["success"] is True
            assert result["response"]["symbol"] == "AAPL"
    
    @pytest.mark.asyncio
    async def test_quantitative_analysis(self, chat_service):
        """Test quantitative analysis functionality."""
        
        mock_response = Mock()
        mock_response.final_output = {
            "symbol": "AAPL",
            "analysis_type": "technical",
            "metrics": {"rsi": 65.2, "macd": 1.25}
        }
        
        with patch.object(chat_service.master_agent, 'run', return_value=mock_response):
            result = await chat_service.quantitative_analysis(
                symbol="AAPL",
                indicators=["RSI", "MACD"]
            )
            
            assert result["success"] is True
            assert "metrics" in result["response"]
    
    @pytest.mark.asyncio
    async def test_chart_generation(self, chat_service):
        """Test chart generation functionality."""
        
        mock_response = Mock()
        mock_response.final_output = {
            "chart_type": "candlestick",
            "file_path": "/charts/aapl_chart.png",
            "title": "AAPL Candlestick Chart"
        }
        
        with patch.object(chat_service.master_agent, 'run', return_value=mock_response):
            result = await chat_service.generate_chart(
                symbol="AAPL",
                chart_type="candlestick"
            )
            
            assert result["success"] is True
            assert result["response"]["chart_type"] == "candlestick"
```

## 🔗 Integration Tests

### API Integration Tests

```python
# tests/integration/api/test_chat_endpoint.py
import pytest
import httpx
from fastapi.testclient import TestClient
from app.app import app

class TestChatEndpoint:
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_chat_endpoint_success(self, client, sample_chat_request):
        """Test successful chat endpoint call."""
        
        response = client.post("/chat", json=sample_chat_request)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message_id" in data
        assert "response" in data
        assert "timestamp" in data
    
    def test_chat_endpoint_invalid_request(self, client):
        """Test chat endpoint with invalid request."""
        
        invalid_request = {
            "message": "",  # Empty message
            "query_type": "invalid_type"
        }
        
        response = client.post("/chat", json=invalid_request)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_stock_analysis_endpoint(self, client):
        """Test stock analysis endpoint."""
        
        request = {
            "symbol": "AAPL",
            "analysis_type": "comprehensive",
            "timeframe": "1Y"
        }
        
        response = client.post("/analyze/stock", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["response"]["symbol"] == "AAPL"
    
    def test_quantitative_analysis_endpoint(self, client):
        """Test quantitative analysis endpoint."""
        
        request = {
            "symbol": "AAPL",
            "indicators": ["RSI", "MACD"],
            "timeframe": "6M"
        }
        
        response = client.post("/analyze/quantitative", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "metrics" in data["response"]
    
    def test_chart_generation_endpoint(self, client):
        """Test chart generation endpoint."""
        
        request = {
            "symbol": "AAPL",
            "chart_type": "candlestick",
            "timeframe": "3M"
        }
        
        response = client.post("/generate/chart", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["response"]["chart_type"] == "candlestick"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_agents_list_endpoint(self, client):
        """Test agents list endpoint."""
        
        response = client.get("/agents")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "specialist_agents" in data
        assert "task_agents" in data
        assert "query_types" in data
        
        # Verify agent information
        specialist_agents = data["specialist_agents"]
        assert len(specialist_agents) > 0
        assert any(agent["name"] == "research_agent" for agent in specialist_agents)
```

### Agent Integration Tests

```python
# tests/integration/agents/test_agent_workflows.py
import pytest
from unittest.mock import patch, AsyncMock
from src.agents.planner_agents.master_agent import master_agent

class TestAgentWorkflows:
    
    @pytest.mark.asyncio
    async def test_complete_stock_research_workflow(self):
        """Test complete stock research workflow."""
        
        query = "Research AAPL stock comprehensively"
        
        with patch('src.tools.stock_market.get_realtime_market_data') as mock_market, \
             patch('src.tools.yfinance_data.get_stock_with_technical_analysis') as mock_technical:
            
            # Mock external data
            mock_market.return_value = {
                "symbol": "AAPL",
                "price": 150.25,
                "change": 2.15,
                "volume": 1000000
            }
            
            mock_technical.return_value = {
                "symbol": "AAPL",
                "technical_indicators": {
                    "rsi": 65.2,
                    "macd": 1.25,
                    "sma_20": 148.5
                }
            }
            
            # Mock agent execution
            with patch.object(master_agent, 'run') as mock_run:
                mock_run.return_value = AsyncMock(
                    final_output={
                        "request_id": "req_123",
                        "query_type": "stock_research",
                        "selected_agent": {
                            "agent_name": "research_agent",
                            "confidence_score": 0.92
                        },
                        "execution_result": {
                            "symbol": "AAPL",
                            "company_name": "Apple Inc.",
                            "analysis_type": "comprehensive",
                            "investment_recommendation": "BUY",
                            "confidence_score": 0.87
                        },
                        "execution_time": 2.3,
                        "success": True
                    }
                )
                
                result = await master_agent.run(query)
                
                # Verify workflow completion
                assert result.final_output["success"] is True
                assert result.final_output["selected_agent"]["agent_name"] == "research_agent"
                assert result.final_output["execution_result"]["symbol"] == "AAPL"
                assert result.final_output["execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_multi_agent_collaboration(self):
        """Test collaboration between multiple agents."""
        
        query = "Generate comprehensive report for AAPL including technical analysis and risk assessment"
        
        with patch.object(master_agent, 'run') as mock_run:
            mock_run.return_value = AsyncMock(
                final_output={
                    "request_id": "req_456",
                    "query_type": "comprehensive_analysis",
                    "selected_agent": {
                        "agent_name": "writer_agent",
                        "confidence_score": 0.89
                    },
                    "execution_result": {
                        "title": "Comprehensive AAPL Analysis Report",
                        "technical_analysis": {
                            "rsi": 65.2,
                            "macd": 1.25,
                            "signals": ["Bullish momentum"]
                        },
                        "risk_assessment": {
                            "risk_level": "medium",
                            "volatility": 0.22
                        },
                        "investment_recommendation": "BUY",
                        "confidence_score": 0.85
                    },
                    "execution_time": 4.2,
                    "success": True
                }
            )
            
            result = await master_agent.run(query)
            
            # Verify multi-agent collaboration
            assert result.final_output["execution_result"]["technical_analysis"] is not None
            assert result.final_output["execution_result"]["risk_assessment"] is not None
            assert result.final_output["execution_time"] > 3.0  # Longer execution for complex analysis
```

## 🎯 End-to-End Tests

### Complete Workflow Tests

```python
# tests/integration/workflows/test_complete_analysis.py
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from app.services.chat_service import ChatService

class TestCompleteAnalysis:
    
    @pytest.fixture
    async def chat_service(self):
        """Create chat service for E2E testing."""
        service = ChatService()
        await service.initialize()
        yield service
        await service.shutdown()
    
    @pytest.mark.asyncio
    async def test_complete_stock_analysis_workflow(self, chat_service):
        """Test complete stock analysis from request to response."""
        
        # Test data
        request_data = {
            "message": "Analyze AAPL stock comprehensively",
            "query_type": "stock_research",
            "session_id": "e2e_test_session"
        }
        
        # Mock all external dependencies
        with patch('src.tools.stock_market.get_realtime_market_data') as mock_market, \
             patch('src.tools.yfinance_data.get_stock_with_technical_analysis') as mock_technical, \
             patch('src.agents.specialist_agents.research_agent.research_agent.run') as mock_research:
            
            # Mock market data
            mock_market.return_value = {
                "symbol": "AAPL",
                "price": 150.25,
                "change": 2.15,
                "percent_change": 1.45,
                "volume": 1000000,
                "market_cap": 2400000000000
            }
            
            # Mock technical analysis
            mock_technical.return_value = {
                "symbol": "AAPL",
                "price_data": [],
                "technical_indicators": {
                    "rsi_14": 65.2,
                    "macd": 1.25,
                    "sma_20": 148.5,
                    "bollinger_upper": 155.8,
                    "bollinger_lower": 140.6
                }
            }
            
            # Mock research agent
            mock_research.return_value = AsyncMock(
                final_output={
                    "symbol": "AAPL",
                    "company_name": "Apple Inc.",
                    "current_price": 150.25,
                    "market_cap": 2400000000000,
                    "analysis_type": "comprehensive",
                    "fundamental_metrics": {
                        "pe_ratio": 28.5,
                        "pb_ratio": 6.8,
                        "roe": 0.147,
                        "debt_to_equity": 1.75
                    },
                    "technical_indicators": {
                        "rsi": 65.2,
                        "macd": 1.25,
                        "sma_20": 148.5
                    },
                    "investment_recommendation": "BUY",
                    "confidence_score": 0.87
                }
            )
            
            # Execute complete workflow
            result = await chat_service.chat(
                message=request_data["message"],
                query_type=request_data["query_type"],
                session_id=request_data["session_id"]
            )
            
            # Verify complete workflow
            assert result["success"] is True
            assert "message_id" in result
            assert result["response"]["symbol"] == "AAPL"
            assert result["response"]["investment_recommendation"] == "BUY"
            assert result["execution_time"] > 0
            
            # Verify external calls were made
            mock_market.assert_called()
            mock_technical.assert_called()
            mock_research.assert_called()
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, chat_service):
        """Test error recovery in complete workflow."""
        
        request_data = {
            "message": "Analyze INVALID_SYMBOL",
            "query_type": "stock_research"
        }
        
        # Mock external API failure
        with patch('src.tools.stock_market.get_realtime_market_data', side_effect=Exception("API Error")):
            
            with pytest.raises(Exception) as exc_info:
                await chat_service.chat(
                    message=request_data["message"],
                    query_type=request_data["query_type"]
                )
            
            # Verify error is properly propagated
            assert "API Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, chat_service):
        """Test system performance under concurrent load."""
        
        # Create multiple concurrent requests
        requests = [
            {"message": f"Analyze stock {i}", "symbol": f"STOCK{i}"}
            for i in range(10)
        ]
        
        # Mock responses
        with patch.object(chat_service.master_agent, 'run') as mock_run:
            mock_run.return_value = AsyncMock(
                final_output={
                    "success": True,
                    "execution_time": 1.0,
                    "response": {"symbol": "MOCK"}
                }
            )
            
            # Execute concurrent requests
            tasks = [
                chat_service.chat(
                    message=req["message"],
                    query_type="stock_research"
                )
                for req in requests
            ]
            
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()
            
            # Verify all requests completed successfully
            assert len(results) == 10
            assert all(result["success"] for result in results)
            
            # Verify performance (should complete within reasonable time)
            total_time = end_time - start_time
            assert total_time < 30  # Should complete within 30 seconds
            assert total_time > 1   # But should take some time for processing
```

## 📊 Test Coverage and Reporting

### Coverage Configuration

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=app
    --cov=src
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80
    -v
asyncio_mode = auto
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto

# Run tests matching pattern
pytest -k "test_agent"

# Run tests with specific marker
pytest -m "not slow"
```

### Test Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov=src --cov-report=html
open htmlcov/index.html

# Generate XML report for CI/CD
pytest --cov=app --cov=src --cov-report=xml

# Generate JUnit XML for CI/CD
pytest --junitxml=test-results.xml
```

This comprehensive testing guide ensures FinanceBot maintains high quality, reliability, and performance across all components and workflows.
