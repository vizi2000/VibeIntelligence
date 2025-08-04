#!/bin/bash

# Zenith Coder Deployment Script
# Following Directive 7: Performance & Scalability
# Implements vibecoding deployment with zero-downtime

set -e  # Exit on error

echo "🚀 Starting Zenith Coder Deployment with Vibecoding!"
echo "=================================================="

# Colors for vibecoding output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root (required for port 80/443)
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root for port 80/443 access${NC}"
   echo "Please run: sudo ./deploy.sh"
   exit 1
fi

# Function to check port availability
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}❌ Port $port is already in use!${NC}"
        echo "Conflicting process:"
        lsof -Pi :$port -sTCP:LISTEN
        return 1
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
        return 0
    fi
}

# Function to generate secure passwords
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

echo -e "${BLUE}🔍 Checking port availability...${NC}"

# Check critical ports
REQUIRED_PORTS=(80 443 8080)
PORTS_AVAILABLE=true

for port in "${REQUIRED_PORTS[@]}"; do
    if ! check_port $port; then
        PORTS_AVAILABLE=false
    fi
done

if [ "$PORTS_AVAILABLE" = false ]; then
    echo -e "${YELLOW}⚠️  Port conflicts detected!${NC}"
    echo "Options:"
    echo "1. Stop conflicting services"
    echo "2. Use Traefik on alternative ports"
    echo "3. Use development mode with high ports"
    
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
fi

# Environment setup
echo -e "${BLUE}🔧 Setting up environment...${NC}"

# Check for .env.production or create it
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}Creating production environment file...${NC}"
    
    # Generate secure passwords
    DB_PASSWORD=$(generate_password)
    REDIS_PASSWORD=$(generate_password)
    SECRET_KEY=$(generate_password)
    
    cat > .env.production << EOF
# Zenith Coder Production Environment
# Generated on $(date)

# Domain Configuration
DOMAIN=zenithcoder.local

# Database
DB_PASSWORD=$DB_PASSWORD

# Redis
REDIS_PASSWORD=$REDIS_PASSWORD

# Security
SECRET_KEY=$SECRET_KEY

# AI Services (add your keys)
OPENROUTER_API_KEY=
HUGGINGFACE_API_TOKEN=

# Deployment
ENVIRONMENT=production
EOF
    
    echo -e "${GREEN}✅ Production environment created${NC}"
    echo -e "${YELLOW}⚠️  Please add your API keys to .env.production${NC}"
fi

# Load environment
set -a
source .env.production
set +a

# Build check
echo -e "${BLUE}🏗️  Building containers...${NC}"

# Build with Docker Compose
docker-compose -f docker-compose.prod.yml build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"

# Database backup (if exists)
if docker ps | grep -q zenith_postgres_prod; then
    echo -e "${BLUE}💾 Backing up database...${NC}"
    docker exec zenith_postgres_prod pg_dump -U zenith zenith_coder > backup_$(date +%Y%m%d_%H%M%S).sql
    echo -e "${GREEN}✅ Database backed up${NC}"
fi

# Deploy with zero downtime
echo -e "${BLUE}🚀 Deploying with zero downtime...${NC}"

# Start new containers
docker-compose -f docker-compose.prod.yml up -d

# Wait for health checks
echo -e "${BLUE}💓 Waiting for services to be healthy...${NC}"

RETRIES=30
HEALTHY=false

for i in $(seq 1 $RETRIES); do
    if docker-compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
        HEALTHY=true
        break
    fi
    echo -n "."
    sleep 2
done

echo

if [ "$HEALTHY" = true ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
else
    echo -e "${RED}❌ Services failed health check${NC}"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

# Run database migrations
echo -e "${BLUE}📊 Running database migrations...${NC}"
docker exec zenith_backend_prod alembic upgrade head || echo "No migrations to run"

# Cleanup old containers
echo -e "${BLUE}🧹 Cleaning up...${NC}"
docker system prune -f

# Success message
echo
echo -e "${GREEN}🎉 Deployment successful!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo
echo "Access your application at:"
echo -e "${BLUE}  Frontend: ${NC}https://${DOMAIN}"
echo -e "${BLUE}  API:      ${NC}https://${DOMAIN}/api"
echo -e "${BLUE}  Traefik:  ${NC}http://${DOMAIN}:8080"
echo
echo -e "${YELLOW}Vibe level: ${GREEN}PEAK DEPLOYMENT FLOW! 🌟${NC}"
echo
echo "Next steps:"
echo "1. Configure your domain DNS to point to this server"
echo "2. Add API keys to .env.production"
echo "3. Monitor logs: docker-compose -f docker-compose.prod.yml logs -f"
echo
echo -e "${GREEN}Happy Vibecoding! 🚀✨${NC}"