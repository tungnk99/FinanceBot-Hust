# FinanceBot Multi-Agent System

**AI-Powered Financial Analysis với Multi-Agent System**

Hệ thống đa agent tài chính được xây dựng bằng FastAPI, tích hợp Master Agent để tự động điều phối các specialist agents cho phân tích tài chính toàn diện.

## 🏗️ Cấu trúc Project

```
FinanceBot-Hust/
├── app/                   # FastAPI Service
│   ├── api/              # API Layer
│   ├── core/             # Core Configuration
│   ├── schemas/          # Data Schemas
│   ├── services/         # Business Logic
│   ├── utils/            # Utilities
│   ├── monitors/         # Monitoring
│   ├── app.py           # FastAPI main app
│   ├── start_server.py  # Server startup
│   ├── client_example.py # API client
│   └── test_api.py      # API tests
├── src/                  # Core Agents & Tools
│   ├── agents/          # AI Agents
│   ├── tools/           # Tools & Functions
│   ├── schemas/         # Core Schemas
│   └── utils/           # Core Utilities
├── tests/               # Test Suite
├── docs/                # Documentation
├── requirements.txt     # Dependencies
├── Makefile            # Commands
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Cài đặt Dependencies

```bash
# Clone repository
git clone <repository-url>
cd FinanceBot-Hust

# Cài đặt dependencies
make install
# hoặc
pip install -r requirements.txt
```

### 2. Cấu hình Environment

```bash
# Setup development environment
make setup
# hoặc
cp app/env.example app/.env
```

**Chỉnh sửa `app/.env` với API keys của bạn:**

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Monitoring Configuration
MONITORING_PROVIDER=langfuse  # Options: langfuse, logfire, wandb, none
ENABLE_MONITORING=true

# Langfuse Configuration (Optional)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

### 3. Chạy Service

```bash
# Development mode với auto-reload
make dev

# Production mode  
make run

# Docker deployment
make docker-build
```

**Hoặc chạy trực tiếp:**

```bash
# Development
cd app && uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload

# Production
cd app && python start_server.py
```

**Service sẽ chạy tại:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🛠️ Commands

```bash
make help          # Show all available commands
make setup         # Setup development environment
make install       # Install dependencies
make dev           # Run FastAPI service in development mode
make run           # Run FastAPI service in production mode
make test          # Run tests
make test-api      # Run API tests only
make test-agents   # Run agent tests
make agents-test   # Test individual agents
make docker-build  # Build and run with Docker
make client-demo   # Run client demo
make client-chat   # Run interactive chat
make clean         # Clean up temporary files
make health        # Check service health
make quickstart    # Complete setup for new users
```

## 📚 API Endpoints

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Phân tích cổ phiếu VIC",
    "query_type": "stock_research",
    "priority": "HIGH"
  }'
```

### Stock Analysis
```bash
curl -X POST "http://localhost:8000/analyze/stock" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "VIC",
    "analysis_type": "comprehensive"
  }'
```

### Quantitative Analysis
```bash
curl -X POST "http://localhost:8000/analyze/quantitative" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "indicators": ["RSI", "MACD", "Moving Averages"]
  }'
```

### Chart Generation
```bash
curl -X POST "http://localhost:8000/generate/chart" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "VIC",
    "chart_type": "price with Bollinger Bands"
  }'
```

## 🤖 Available Agents

### Specialist Agents
- **Research Agent**: Nghiên cứu cổ phiếu toàn diện
- **Quant Agent**: Phân tích định lượng và kỹ thuật
- **Fin Doc Agent**: Phân tích tài liệu tài chính
- **Risk Agent**: Đánh giá rủi ro

### Task Agents
- **Search Agent**: Tìm kiếm thông tin tài chính
- **Chart Generator Agent**: Tạo biểu đồ chuyên nghiệp
- **Writer Agent**: Viết báo cáo tài chính

### Query Types
- `stock_research`: Nghiên cứu cổ phiếu toàn diện
- `quantitative_analysis`: Phân tích định lượng
- `financial_document`: Phân tích tài liệu
- `risk_assessment`: Đánh giá rủi ro
- `market_search`: Tìm kiếm thông tin thị trường
- `chart_generation`: Tạo biểu đồ
- `report_writing`: Viết báo cáo

## 📊 Monitoring & Observability

### Supported Providers
- **Langfuse**: Tracing và monitoring với OpenTelemetry
- **Logfire**: Logging và tracing
- **Weights & Biases**: Experiment tracking
- **None**: Disable monitoring

### Features
- Multi-provider support
- Tự động tích hợp monitoring
- Tracing tất cả agent calls
- Auto-flush traces
- Performance monitoring
- Error tracking

## 🐳 Docker Deployment

```bash
# Build and run
make docker-build

# Run in background
cd app && docker-compose up -d

# View logs
cd app && docker-compose logs -f
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run API tests
make test-api

# Run agent tests
make test-agents

# Test individual agents
make agents-test

# Interactive testing
make client-demo
make client-chat
```

## 🔧 Development

### Project Structure
- **`app/`**: FastAPI service với clean architecture
- **`src/`**: Core agents và tools
- **`tests/`**: Comprehensive test suite
- **`docs/`**: Documentation

### Architecture Pattern
- **API Layer**: FastAPI endpoints
- **Business Logic**: Services layer
- **Data Schemas**: Pydantic models
- **Utilities**: Helper functions
- **Monitoring**: Integrated observability

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Đảm bảo đã cài đặt dependencies với `make install`
2. **API Key Issues**: Kiểm tra OPENAI_API_KEY trong `app/.env`
3. **Port Conflicts**: Thay đổi API_PORT trong `app/.env`
4. **Monitoring Errors**: Có thể disable bằng MONITORING_PROVIDER=none

### Health Check

```bash
# Check service health
make health

# View service logs
cd app && docker-compose logs -f
```

## 🆘 Support

- **API Documentation**: http://localhost:8000/docs (when running)
- **Health Check**: http://localhost:8000/health
- **Issues**: Create GitHub issue

## 📄 License

This project is licensed under the MIT License.

---

**FinanceBot Multi-Agent System** - Powered by Master Agent 🚀