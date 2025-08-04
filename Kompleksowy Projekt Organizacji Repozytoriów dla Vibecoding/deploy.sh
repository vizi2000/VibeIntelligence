#!/bin/bash

# Zenith Coder Deployment Script
# This script handles the complete deployment of Zenith Coder to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="zenith-coder"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning "Please edit .env file with your configuration before continuing."
            read -p "Press Enter to continue after editing .env file..."
        else
            log_error ".env.example file not found. Cannot create .env file."
            exit 1
        fi
    fi
    
    log_success "Prerequisites check completed"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build backend image
    log_info "Building backend image..."
    docker-compose build backend
    
    # Build frontend image
    log_info "Building frontend image..."
    docker-compose build frontend
    
    log_success "Docker images built successfully"
}

start_services() {
    log_info "Starting services..."
    
    # Start infrastructure services first
    log_info "Starting infrastructure services (PostgreSQL, Redis, ChromaDB)..."
    docker-compose up -d postgres redis chromadb
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Start Traefik
    log_info "Starting Traefik reverse proxy..."
    docker-compose up -d traefik
    
    # Start backend
    log_info "Starting backend service..."
    docker-compose up -d backend
    
    # Wait for backend to be ready
    log_info "Waiting for backend to be ready..."
    sleep 15
    
    # Start frontend
    log_info "Starting frontend service..."
    docker-compose up -d frontend
    
    log_success "All services started successfully"
}

run_health_checks() {
    log_info "Running health checks..."
    
    # Check if services are running
    services=("postgres" "redis" "chromadb" "traefik" "backend" "frontend")
    
    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "$service.*Up"; then
            log_success "$service is running"
        else
            log_error "$service is not running"
            return 1
        fi
    done
    
    # Check backend health endpoint
    log_info "Checking backend health..."
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost/api/v1/health &> /dev/null; then
            log_success "Backend health check passed"
            break
        else
            log_info "Attempt $attempt/$max_attempts: Backend not ready yet..."
            sleep 2
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Backend health check failed after $max_attempts attempts"
        return 1
    fi
    
    # Check frontend
    log_info "Checking frontend..."
    if curl -f http://localhost &> /dev/null; then
        log_success "Frontend is accessible"
    else
        log_error "Frontend is not accessible"
        return 1
    fi
    
    log_success "All health checks passed"
}

show_deployment_info() {
    log_success "🚀 Zenith Coder deployed successfully!"
    echo
    echo "📊 Access URLs:"
    echo "  • Dashboard: http://localhost"
    echo "  • API Documentation: http://localhost/api/v1/docs"
    echo "  • Traefik Dashboard: http://localhost:8080"
    echo
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart services: docker-compose restart"
    echo "  • Update services: docker-compose pull && docker-compose up -d"
    echo
    echo "📁 Important Files:"
    echo "  • Configuration: .env"
    echo "  • Logs: docker-compose logs"
    echo "  • Data: Docker volumes (postgres_data, redis_data, chromadb_data)"
    echo
}

cleanup_on_error() {
    log_error "Deployment failed. Cleaning up..."
    docker-compose down
    exit 1
}

# Main deployment process
main() {
    log_info "🚀 Starting Zenith Coder deployment..."
    echo
    
    # Set up error handling
    trap cleanup_on_error ERR
    
    # Run deployment steps
    check_prerequisites
    build_images
    start_services
    run_health_checks
    show_deployment_info
    
    log_success "✅ Deployment completed successfully!"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping Zenith Coder..."
        docker-compose down
        log_success "Zenith Coder stopped"
        ;;
    "restart")
        log_info "Restarting Zenith Coder..."
        docker-compose restart
        log_success "Zenith Coder restarted"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    "update")
        log_info "Updating Zenith Coder..."
        docker-compose pull
        docker-compose up -d
        log_success "Zenith Coder updated"
        ;;
    "clean")
        log_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            docker-compose down -v --rmi all
            log_success "Cleanup completed"
        else
            log_info "Cleanup cancelled"
        fi
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|update|clean}"
        echo
        echo "Commands:"
        echo "  deploy  - Deploy Zenith Coder (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Show logs from all services"
        echo "  status  - Show status of all services"
        echo "  update  - Update and restart services"
        echo "  clean   - Remove all containers, images, and volumes"
        exit 1
        ;;
esac

