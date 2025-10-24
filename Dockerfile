FROM python:3.11-slim

# Set working directory
WORKDIR /financebot

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash financebot \
    && chown -R financebot:financebot /financebot
USER financebot

# Set working directory to project root
WORKDIR /financebot

# Add the project root to Python path
ENV PYTHONPATH=/financebot

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "app/start_server.py"]
