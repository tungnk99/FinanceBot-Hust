# FinanceBot API Documentation

## 🌐 Overview

FinanceBot provides a comprehensive REST API for financial analysis and AI-powered insights. The API is built with FastAPI and offers both general chat functionality and specialized financial analysis endpoints.

## 🚀 Base URL

```
http://localhost:8000
```

## 📋 Authentication

Currently, the API does not require authentication. Authentication and authorization features are planned for future releases.

## 📊 API Endpoints

### Health Check

#### `GET /health`

Check the service health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-30T10:30:00Z",
  "version": "1.0.0",
  "monitoring_enabled": true
}
```

**Response Model:**
- `status` (string): Service status
- `timestamp` (datetime): Response timestamp
- `version` (string): API version
- `monitoring_enabled` (boolean): Whether monitoring is enabled

---

### Chat Endpoint

#### `POST /chat`

Main chat endpoint that processes user messages through the Master Agent system.

**Request Body:**
```json
{
  "message": "What is the current price of AAPL?",
  "query_type": "market_search",
  "priority": "normal",
  "session_id": "session_123",
  "user_id": "user_456",
  "context": {
    "preferred_language": "en",
    "timezone": "UTC"
  }
}
```

**Request Model:**
- `message` (string, required): User's message or query
- `query_type` (string, optional): Type of query (see Query Types below)
- `priority` (string, optional): Request priority ("low", "normal", "high")
- `session_id` (string, optional): Session identifier
- `user_id` (string, optional): User identifier
- `context` (object, optional): Additional context information

**Response:**
```json
{
  "success": true,
  "message_id": "MSG-20250130-001",
  "response": {
    "request_id": "req_202501300001",
    "query": "What is the current price of AAPL?",
    "query_type": "market_search",
    "selected_agent": {
      "agent_name": "get_realtime_market_data",
      "agent_type": "direct_tool",
      "confidence_score": 0.85,
      "reasoning": "Direct market data request for specific stock symbol"
    },
    "execution_result": {
      "symbol": "AAPL",
      "price": 150.25,
      "change": 2.15,
      "percent_change": 1.45
    },
    "execution_time": 0.8,
    "timestamp": "2025-01-30T10:30:00Z",
    "success": true,
    "follow_up_suggestions": [
      "Would you like to see AAPL's price chart?",
      "Do you want technical analysis for AAPL?"
    ]
  },
  "selected_agent": {
    "name": "search_agent",
    "type": "task",
    "confidence": 0.85
  },
  "execution_time": 0.8,
  "timestamp": "2025-01-30T10:30:00Z",
  "session_id": "session_123",
  "error": null
}
```

**Response Model:**
- `success` (boolean): Whether the request was successful
- `message_id` (string): Unique message identifier
- `response` (object|string): Bot response (can be structured object or string)
- `selected_agent` (object, optional): Information about the selected agent
- `execution_time` (float, optional): Execution time in seconds
- `timestamp` (datetime): Response timestamp
- `session_id` (string, optional): Session identifier
- `error` (string, optional): Error message if any

---

### Stock Analysis

#### `POST /analyze/stock`

Perform comprehensive stock analysis using the Research Agent.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "analysis_type": "comprehensive",
  "timeframe": "1Y",
  "indicators": ["RSI", "MACD", "Bollinger_Bands"]
}
```

**Request Model:**
- `symbol` (string, required): Stock symbol (e.g., "AAPL", "MSFT")
- `analysis_type` (string, optional): Type of analysis ("technical", "fundamental", "comprehensive")
- `timeframe` (string, optional): Analysis timeframe ("1D", "1W", "1M", "3M", "1Y")
- `indicators` (array, optional): Technical indicators to include

**Response:**
```json
{
  "success": true,
  "message_id": "MSG-20250130-002",
  "response": {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "current_price": 150.25,
    "market_cap": 2400000000000,
    "analysis_type": "comprehensive",
    "fundamental_metrics": {
      "pe_ratio": 28.5,
      "pb_ratio": 6.8,
      "roe": 0.147
    },
    "technical_indicators": {
      "rsi": 65.2,
      "macd": 1.25,
      "bollinger_bands": {
        "upper": 155.8,
        "middle": 148.2,
        "lower": 140.6
      }
    },
    "investment_recommendation": "BUY",
    "confidence_score": 0.87
  },
  "selected_agent": {
    "name": "research_agent",
    "type": "specialist",
    "confidence": 0.87
  },
  "execution_time": 2.3,
  "timestamp": "2025-01-30T10:32:00Z"
}
```

---

### Quantitative Analysis

#### `POST /analyze/quantitative`

Perform technical and quantitative analysis using the Quantitative Agent.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "indicators": ["RSI", "MACD", "SMA"],
  "timeframe": "6M"
}
```

**Response:**
```json
{
  "success": true,
  "message_id": "MSG-20250130-003",
  "response": {
    "symbol": "AAPL",
    "analysis_type": "technical",
    "timeframe": "6M",
    "metrics": {
      "rsi_14": 65.2,
      "macd": 1.25,
      "sma_20": 148.5,
      "sma_50": 145.8
    },
    "signals": [
      "RSI indicates overbought conditions",
      "MACD shows bullish momentum",
      "Price above 20-day SMA"
    ],
    "recommendations": [
      "Consider profit-taking if RSI exceeds 70",
      "Monitor for MACD divergence"
    ],
    "confidence_score": 0.82
  },
  "selected_agent": {
    "name": "quant_agent",
    "type": "specialist",
    "confidence": 0.82
  },
  "execution_time": 1.8,
  "timestamp": "2025-01-30T10:34:00Z"
}
```

---

### Chart Generation

#### `POST /generate/chart`

Generate financial charts and visualizations using the Chart Generator Agent.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "chart_type": "candlestick",
  "timeframe": "3M"
}
```

**Request Model:**
- `symbol` (string, required): Stock symbol
- `chart_type` (string, required): Type of chart ("line", "candlestick", "volume", "technical_indicators")
- `timeframe` (string, optional): Chart timeframe

**Response:**
```json
{
  "success": true,
  "message_id": "MSG-20250130-004",
  "response": {
    "chart_type": "candlestick",
    "title": "AAPL - 3 Month Candlestick Chart",
    "data": {
      "symbol": "AAPL",
      "timeframe": "3M",
      "price_data": [...]
    },
    "chart_config": {
      "width": 800,
      "height": 600,
      "style": "professional"
    },
    "file_path": "/charts/aapl_3m_candlestick.png",
    "description": "3-month candlestick chart for AAPL with volume overlay",
    "insights": [
      "Strong uptrend over the period",
      "High volume on breakout days",
      "Support at $145 level"
    ]
  },
  "selected_agent": {
    "name": "chart_generator_agent",
    "type": "task",
    "confidence": 0.89
  },
  "execution_time": 3.2,
  "timestamp": "2025-01-30T10:36:00Z"
}
```

---

### Agents Information

#### `GET /agents`

Get information about available agents and their capabilities.

**Response:**
```json
{
  "specialist_agents": [
    {
      "name": "research_agent",
      "description": "Nghiên cứu cổ phiếu toàn diện với phân tích cơ bản, kỹ thuật và thị trường",
      "capabilities": ["stock_research", "fundamental_analysis", "market_analysis"],
      "agent_type": "specialist"
    },
    {
      "name": "quant_agent",
      "description": "Phân tích định lượng, kỹ thuật và tính toán các metrics tài chính",
      "capabilities": ["technical_analysis", "quantitative_metrics", "risk_calculation"],
      "agent_type": "specialist"
    }
  ],
  "task_agents": [
    {
      "name": "search_agent",
      "description": "Tìm kiếm thông tin tài chính từ nhiều nguồn dữ liệu",
      "capabilities": ["information_retrieval", "market_data", "news_search"],
      "agent_type": "task"
    },
    {
      "name": "chart_generator_agent",
      "description": "Tạo biểu đồ tài chính chuyên nghiệp và visualizations",
      "capabilities": ["chart_generation", "data_visualization", "technical_charts"],
      "agent_type": "task"
    }
  ],
  "query_types": [
    {
      "value": "stock_research",
      "description": "Nghiên cứu cổ phiếu toàn diện"
    },
    {
      "value": "quantitative_analysis",
      "description": "Phân tích định lượng và kỹ thuật"
    },
    {
      "value": "market_search",
      "description": "Tìm kiếm thông tin thị trường"
    }
  ]
}
```

## 🔍 Query Types

The API supports various query types that help the Master Agent select the most appropriate specialist agent:

| Query Type | Description | Recommended Agent |
|------------|-------------|-------------------|
| `stock_research` | Comprehensive stock research | research_agent |
| `quantitative_analysis` | Technical and quantitative analysis | quant_agent |
| `financial_document` | Financial document analysis | fin_doc_agent |
| `risk_assessment` | Risk evaluation and assessment | risk_agent |
| `market_search` | Market data search | search_agent |
| `chart_generation` | Chart and visualization creation | chart_generator_agent |
| `report_writing` | Professional report generation | writer_agent |
| `comprehensive_analysis` | Multi-faceted analysis | Multiple agents |
| `general_finance` | General financial queries | search_agent |

## 📈 Chart Types

Available chart types for the chart generation endpoint:

| Chart Type | Description |
|------------|-------------|
| `line_chart` | Price line charts |
| `candlestick` | OHLC candlestick charts |
| `volume` | Volume analysis charts |
| `technical_indicators` | Technical indicator overlays |
| `comparison` | Multi-asset comparison charts |
| `sector_comparison` | Sector analysis charts |

## ⚠️ Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

### Error Response Format
```json
{
  "detail": "Error description"
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| `400` | Bad Request - Invalid input parameters |
| `404` | Not Found - Endpoint or resource not found |
| `422` | Validation Error - Request validation failed |
| `500` | Internal Server Error - Server-side error |

### Example Error Responses

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "symbol"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Processing Error:**
```json
{
  "detail": "Chat processing failed: Agent execution timeout"
}
```

## 🔧 Rate Limiting

Currently, there are no rate limits implemented. Rate limiting and throttling features are planned for production deployment.

## 📝 Request Examples

### Python Client Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Chat request
chat_response = requests.post(f"{BASE_URL}/chat", json={
    "message": "Analyze AAPL stock",
    "query_type": "stock_research"
})

print(json.dumps(chat_response.json(), indent=2))

# Stock analysis request
stock_response = requests.post(f"{BASE_URL}/analyze/stock", json={
    "symbol": "AAPL",
    "analysis_type": "comprehensive",
    "timeframe": "1Y"
})

print(json.dumps(stock_response.json(), indent=2))
```

### cURL Examples

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Chat request
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the price of AAPL?"}'

# Stock analysis
curl -X POST "http://localhost:8000/analyze/stock" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "analysis_type": "comprehensive",
    "timeframe": "1Y"
  }'

# Generate chart
curl -X POST "http://localhost:8000/generate/chart" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "chart_type": "candlestick",
    "timeframe": "3M"
  }'
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Chat request
async function sendChatMessage(message) {
  try {
    const response = await axios.post(`${BASE_URL}/chat`, {
      message: message,
      query_type: 'general_finance'
    });
    
    console.log('Response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Usage
sendChatMessage('Analyze Tesla stock performance');
```

## 🔄 WebSocket Support

WebSocket support for real-time streaming responses is planned for future releases.

## 📚 Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🚀 Performance Considerations

### Response Times
- **Simple queries**: < 1 second
- **Complex analysis**: 2-5 seconds
- **Chart generation**: 3-10 seconds

### Best Practices
1. **Use appropriate query types** to help with agent selection
2. **Provide session_id** for context continuity
3. **Use specific timeframes** for better performance
4. **Handle errors gracefully** in your client applications

This API provides a powerful and flexible interface for accessing FinanceBot's AI-powered financial analysis capabilities.
