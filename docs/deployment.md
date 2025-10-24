# Deployment Guide

## 🚀 Overview

This guide covers deploying FinanceBot in various environments, from local development to production. The application supports multiple deployment strategies including Docker, cloud platforms, and traditional server deployments.

## 📋 Prerequisites

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for external APIs

### Software Requirements

- **Python**: 3.9 or higher
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for multi-container deployment)
- **Git**: For version control and deployment

## 🐳 Docker Deployment

### Single Container Deployment

#### 1. Build Docker Image

```bash
# Build the image
docker build -t financebot:latest .

# Verify the image
docker images financebot:latest
```

#### 2. Run Container

```bash
# Run with environment variables
docker run -d \
  --name financebot \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key_here \
  -e LANGFUSE_PUBLIC_KEY=your_langfuse_key \
  -e LANGFUSE_SECRET_KEY=your_langfuse_secret \
  financebot:latest

# Check container status
docker ps
docker logs financebot
```

#### 3. Health Check

```bash
# Test the API
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-01-30T10:30:00Z",
  "version": "1.0.0",
  "monitoring_enabled": true
}
```

### Docker Compose Deployment

#### 1. Create docker-compose.yml

```yaml
version: '3.8'

services:
  financebot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=${OPENAI_MODEL:-gpt-4}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_HOST=${LANGFUSE_HOST:-https://cloud.langfuse.com}
      - LOGFIRE_TOKEN=${LOGFIRE_TOKEN}
      - WANDB_API_KEY=${WANDB_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./charts:/app/charts
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - financebot
    restart: unless-stopped

volumes:
  redis_data:
```

#### 2. Create .env file

```bash
# Copy example environment file
cp env.example .env

# Edit with your values
nano .env
```

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Monitoring Configuration
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

LOGFIRE_TOKEN=your_logfire_token
WANDB_API_KEY=your_wandb_api_key

# Application Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Database Configuration (optional)
DATABASE_URL=postgresql://user:password@postgres:5432/financebot

# Redis Configuration
REDIS_URL=redis://redis:6379
```

#### 3. Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f financebot

# Scale the application
docker-compose up -d --scale financebot=3
```

#### 4. Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream financebot {
        server financebot:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
        limit_req zone=api burst=20 nodelay;

        location / {
            proxy_pass http://financebot;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://financebot/health;
            access_log off;
        }

        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## ☁️ Cloud Deployment

### AWS Deployment

#### 1. AWS ECS with Fargate

Create `task-definition.json`:

```json
{
  "family": "financebot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "financebot",
      "image": "your-account.dkr.ecr.region.amazonaws.com/financebot:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "your_openai_api_key"
        }
      ],
      "secrets": [
        {
          "name": "LANGFUSE_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:financebot/langfuse"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/financebot",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### 2. Deploy to ECS

```bash
# Build and push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-west-2.amazonaws.com

docker build -t financebot .
docker tag financebot:latest your-account.dkr.ecr.us-west-2.amazonaws.com/financebot:latest
docker push your-account.dkr.ecr.us-west-2.amazonaws.com/financebot:latest

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster financebot-cluster \
  --service-name financebot-service \
  --task-definition financebot:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Platform

#### 1. Cloud Run Deployment

Create `cloudbuild.yaml`:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/financebot', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/financebot']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'financebot'
      - '--image'
      - 'gcr.io/$PROJECT_ID/financebot'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'OPENAI_API_KEY=$_OPENAI_API_KEY'
      - '--set-secrets'
      - 'LANGFUSE_SECRET_KEY=langfuse-secret:latest'

substitutions:
  _OPENAI_API_KEY: 'your_openai_api_key'
```

#### 2. Deploy to Cloud Run

```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml

# Or deploy directly
gcloud run deploy financebot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_api_key
```

### Azure Container Instances

#### 1. Create container group

```bash
# Create resource group
az group create --name financebot-rg --location eastus

# Deploy container
az container create \
  --resource-group financebot-rg \
  --name financebot \
  --image your-registry.azurecr.io/financebot:latest \
  --cpu 1 \
  --memory 2 \
  --ports 8000 \
  --dns-name-label financebot-unique \
  --environment-variables \
    OPENAI_API_KEY=your_api_key \
    LANGFUSE_PUBLIC_KEY=your_langfuse_key \
  --restart-policy Always
```

## 🖥️ Traditional Server Deployment

### Ubuntu/Debian Server

#### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.9 python3.9-venv python3-pip nginx certbot python3-certbot-nginx

# Install Node.js (for frontend if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 2. Application Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash financebot
sudo usermod -aG sudo financebot

# Switch to application user
sudo su - financebot

# Clone repository
git clone https://github.com/your-org/financebot.git
cd financebot

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/financebot.service
```

#### 3. Systemd Service Configuration

```ini
[Unit]
Description=FinanceBot FastAPI Application
After=network.target

[Service]
Type=exec
User=financebot
Group=financebot
WorkingDirectory=/home/financebot/financebot
Environment=PATH=/home/financebot/financebot/venv/bin
ExecStart=/home/financebot/financebot/venv/bin/uvicorn app.app:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4. Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable financebot
sudo systemctl start financebot

# Check status
sudo systemctl status financebot

# View logs
sudo journalctl -u financebot -f
```

#### 5. Nginx Configuration

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/financebot
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/financebot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring and Logging

### Application Monitoring

#### 1. Health Checks

```bash
# Basic health check
curl -f http://localhost:8000/health

# Detailed health check script
#!/bin/bash
HEALTH_URL="http://localhost:8000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed with status: $RESPONSE"
    exit 1
fi
```

#### 2. Log Management

```bash
# Log rotation configuration
sudo nano /etc/logrotate.d/financebot
```

```
/home/financebot/financebot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 financebot financebot
    postrotate
        systemctl reload financebot
    endscript
}
```

#### 3. Monitoring with Prometheus

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'financebot'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Performance Monitoring

#### 1. Resource Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor system resources
htop
iotop -a
nethogs

# Monitor application logs
tail -f /home/financebot/financebot/logs/app.log
```

#### 2. Database Monitoring (if using)

```bash
# PostgreSQL monitoring
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Redis monitoring
redis-cli info stats
redis-cli monitor
```

## 🔧 Maintenance and Updates

### Application Updates

#### 1. Rolling Updates with Docker

```bash
# Pull latest image
docker pull financebot:latest

# Update service with zero downtime
docker-compose up -d --no-deps --build financebot

# Verify update
curl http://localhost:8000/health
```

#### 2. Blue-Green Deployment

```bash
# Deploy new version to green environment
docker-compose -f docker-compose.green.yml up -d

# Test green environment
curl http://localhost:8001/health

# Switch traffic (update load balancer configuration)
# Update nginx.conf to point to green environment

# Shut down blue environment
docker-compose -f docker-compose.blue.yml down
```

### Backup and Recovery

#### 1. Application Data Backup

```bash
#!/bin/bash
# Backup script
BACKUP_DIR="/backup/financebot"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup application files
tar -czf $BACKUP_DIR/$DATE/application.tar.gz /home/financebot/financebot

# Backup logs
tar -czf $BACKUP_DIR/$DATE/logs.tar.gz /home/financebot/financebot/logs

# Backup charts
tar -czf $BACKUP_DIR/$DATE/charts.tar.gz /home/financebot/financebot/charts

# Clean old backups (keep 30 days)
find $BACKUP_DIR -type d -mtime +30 -exec rm -rf {} \;
```

#### 2. Configuration Backup

```bash
# Backup configuration files
sudo cp /etc/nginx/sites-available/financebot /backup/config/
sudo cp /etc/systemd/system/financebot.service /backup/config/
sudo cp /home/financebot/financebot/.env /backup/config/
```

### Troubleshooting

#### Common Issues

1. **Service Won't Start**
```bash
# Check service status
sudo systemctl status financebot

# Check logs
sudo journalctl -u financebot -n 50

# Check port availability
sudo netstat -tlnp | grep :8000
```

2. **High Memory Usage**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Restart service
sudo systemctl restart financebot
```

3. **API Timeouts**
```bash
# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Check application logs
sudo journalctl -u financebot -f

# Test API directly
curl -v http://localhost:8000/health
```

#### Performance Optimization

1. **Enable Gzip Compression**
```nginx
# Add to nginx.conf
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

2. **Configure Caching**
```nginx
# Add to nginx.conf
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

3. **Optimize Python Performance**
```python
# Add to requirements.txt
gunicorn[gevent]
uvloop
```

```bash
# Use gunicorn with gevent workers
gunicorn app.app:app -w 4 -k gevent -b 0.0.0.0:8000
```

This deployment guide provides comprehensive instructions for deploying FinanceBot in various environments with proper monitoring, security, and maintenance procedures.
