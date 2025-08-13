#!/bin/bash

# VibeIntelligence Remote Deployment Script
# Target: vizi@borgtools.ddns.net

set -e

REMOTE_HOST="vizi@borgtools.ddns.net"
REMOTE_DIR="~/vibeintelligence"
LOCAL_DIR="$(pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 VibeIntelligence Deployment to $REMOTE_HOST"
echo "================================================"

# Step 1: Create deployment package
echo "📦 Creating deployment package..."
tar -czf vibeintelligence_deploy_${TIMESTAMP}.tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='.env.local' \
    --exclude='test_*.png' \
    --exclude='demo_*.png' \
    --exclude='*.js' \
    backend/ frontend/ docker-compose.prod.yml docker-compose.yml install.sh CLAUDE.md README.md

echo "✅ Package created: vibeintelligence_deploy_${TIMESTAMP}.tar.gz"

# Step 2: Upload to server
echo "📤 Uploading to server..."
scp vibeintelligence_deploy_${TIMESTAMP}.tar.gz ${REMOTE_HOST}:${REMOTE_DIR}/

# Step 3: Deploy on server
echo "🔧 Deploying on server..."
ssh ${REMOTE_HOST} << 'ENDSSH'
cd ~/vibeintelligence

# Extract the latest deployment package
LATEST_PACKAGE=$(ls -t vibeintelligence_deploy_*.tar.gz | head -1)
echo "Extracting $LATEST_PACKAGE..."
tar -xzf $LATEST_PACKAGE

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# VibeIntelligence Production Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
POSTGRES_USER=vi_user
POSTGRES_PASSWORD=vi_secure_$(openssl rand -hex 12)
POSTGRES_DB=vi_db
DATABASE_URL=postgresql://vi_user:${POSTGRES_PASSWORD}@postgres:5432/vi_db

# Redis
REDIS_PASSWORD=redis_secure_$(openssl rand -hex 12)
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=["https://borgtools.ddns.net","https://borg.tools"]

# AI Services (UPDATE THESE)
OPENROUTER_API_KEY=
HUGGINGFACE_API_TOKEN=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Application
API_PORT=8000
FRONTEND_PORT=80
PROJECT_SCAN_PATH=/ai_projects
AI_PROJECTS_PATH=/home/vizi/projects

# Domain
DOMAIN=borgtools.ddns.net
LETSENCRYPT_EMAIL=admin@borg.tools
EOF
    echo "⚠️  Please update AI API keys in .env file"
fi

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Build and start production containers
echo "Building and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be ready
echo "Waiting for services to be healthy..."
sleep 15

# Run database migrations
echo "Running database migrations..."
docker exec vi_backend_prod python -m alembic upgrade head 2>/dev/null || echo "Migrations will run on first request"

# Show status
echo "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ Deployment complete!"
echo "Access the application at:"
echo "  - https://borgtools.ddns.net"
echo "  - https://borg.tools"
echo ""
echo "Traefik dashboard: http://borgtools.ddns.net:8080"
ENDSSH

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Checking deployment status..."
ssh ${REMOTE_HOST} "cd ~/vibeintelligence && docker-compose -f docker-compose.prod.yml ps"

# Cleanup local package
rm -f vibeintelligence_deploy_${TIMESTAMP}.tar.gz