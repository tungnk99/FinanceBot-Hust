#!/bin/bash

# Docker Hub configuration
DOCKER_USERNAME="tungnk1999"  # Thay đổi thành username Docker Hub của bạn
IMAGE_NAME="financebot-hust"
TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Building and pushing FinanceBot Docker image to Docker Hub${NC}"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if user is logged in to Docker Hub
if ! docker info | grep -q "Username:"; then
    echo -e "${YELLOW}⚠️  You need to login to Docker Hub first:${NC}"
    echo "Run: docker login"
    echo "Then run this script again."
    exit 1
fi

# Build the Docker image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
else
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi

# Tag the image for Docker Hub
echo -e "${BLUE}🏷️  Tagging image for Docker Hub...${NC}"
docker tag ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG} ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}

# Push to Docker Hub
echo -e "${BLUE}📤 Pushing image to Docker Hub...${NC}"
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Image pushed successfully to Docker Hub!${NC}"
    echo -e "${GREEN}🔗 Your image is available at: https://hub.docker.com/r/${DOCKER_USERNAME}/${IMAGE_NAME}${NC}"
else
    echo -e "${RED}❌ Failed to push image to Docker Hub!${NC}"
    exit 1
fi

# Show image info
echo -e "${BLUE}📋 Image Information:${NC}"
echo "Repository: ${DOCKER_USERNAME}/${IMAGE_NAME}"
echo "Tag: ${TAG}"
echo "Full name: ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"

echo -e "${GREEN}🎉 Build and push completed successfully!${NC}"
