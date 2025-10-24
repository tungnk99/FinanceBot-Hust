# FinanceBot Multi-Agent System Makefile

.PHONY: help install dev test build run docker-build docker-run clean setup

# Default target
help:
	@echo "FinanceBot Multi-Agent System Commands:"
	@echo "====================================="
	@echo "setup         - Setup development environment"
	@echo "install       - Install dependencies"
	@echo "dev           - Run FastAPI service in development mode"
	@echo "run           - Run FastAPI service in production mode"
	@echo "test          - Run tests"
	@echo "test-api      - Run API tests only"
	@echo "test-agents   - Run agent tests"
	@echo "build         - Build Docker image"
	@echo "docker-run    - Run with Docker Compose"
	@echo "docker-build  - Build and run with Docker"
	@echo "client-demo   - Run client demo"
	@echo "client-chat   - Run interactive chat client"
	@echo "clean         - Clean up temporary files"
	@echo "health        - Check service health"
	@echo "agents-test   - Test individual agents"

# Setup development environment
setup: install
	@echo "Setting up FinanceBot development environment..."
	@if [ ! -f app/.env ]; then cp app/env.example app/.env; echo "Created app/.env file from app/env.example"; fi
	@echo "Please edit app/.env file with your API keys"
	@echo "Setup complete! Run 'make dev' to start development server"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Development mode with auto-reload
dev:
	@echo "Starting FinanceBot FastAPI service in development mode..."
	PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
run:
	@echo "Starting FinanceBot FastAPI service in production mode..."
	PYTHONPATH=. python app/start_server.py

# Run all tests
test:
	@echo "Running all tests..."
	pytest test_api.py -v

# Run API tests only
test-api:
	@echo "Running API tests..."
	python test_api.py

# Run agent tests
test-agents:
	@echo "Running agent tests..."
	python -m pytest tests/agents/ -v

# Test individual agents
agents-test:
	@echo "Testing individual agents..."
	@echo "Testing search agent..."
	python tests/agents/test_search_agent.py
	@echo "Testing quant agent..."
	python tests/agents/test_quant_agent.py
	@echo "Testing writer agent..."
	python tests/agents/test_writer_agent.py

# Build Docker image
build:
	@echo "Building Docker image..."
	docker build -t financebot-api .

# Run with Docker Compose
docker-run:
	@echo "Starting with Docker Compose..."
	docker-compose up

# Build and run with Docker
docker-build:
	@echo "Building and running with Docker..."
	docker-compose up --build

# Run client demo
client-demo:
	@echo "Running client demo..."
	python client_example.py

# Run interactive chat client
client-chat:
	@echo "Starting interactive chat client..."
	python client_example.py chat

# Check service health
health:
	@echo "Checking service health..."
	curl -f http://localhost:8000/health || echo "Service not running"

# Clean up
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf app/__pycache__
	rm -rf app/*/__pycache__

# Development helpers
lint:
	@echo "Running linter..."
	cd app && python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Quick start for new users
quickstart: setup
	@echo "FinanceBot Quick Start Complete!"
	@echo "================================"
	@echo "1. Edit app/.env with your OpenAI API key"
	@echo "2. Run 'make dev' to start development server"
	@echo "3. Visit http://localhost:8000/docs for API documentation"
	@echo "4. Run 'make client-demo' to test the service"

# Show project structure
structure:
	@echo "FinanceBot Project Structure:"
	@echo "============================"
	@tree -I '__pycache__|*.pyc|.git|.pytest_cache' || find . -type f -name "*.py" | head -20
