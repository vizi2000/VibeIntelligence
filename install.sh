#!/bin/bash

# ════════════════════════════════════════════════════════════════════════════
# Zenith Coder Universal Installer
# Version: 2.0.0
# Description: Complete installation and deployment manager for Zenith Coder
# ════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                             COLOR DEFINITIONS                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                              CONFIGURATION                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
SCRIPT_VERSION="2.0.0"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$SCRIPT_DIR/install_$(date +%Y%m%d_%H%M%S).log"
REQUIRED_DOCKER_VERSION="20.10.0"
REQUIRED_COMPOSE_VERSION="2.0.0"

# Default values
INSTALL_MODE=""
ENVIRONMENT=""
SKIP_CHECKS=false
AUTO_CONFIRM=false
VERBOSE=false

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                             HELPER FUNCTIONS                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}[LOG]${NC} $1"
    fi
}

print_header() {
    echo
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║${WHITE}                        ZENITH CODER INSTALLER                        ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║${CYAN}                          Version $SCRIPT_VERSION                           ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_section() {
    echo
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR: $1"
}

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
    log "INFO: $1"
}

spinner() {
    local pid=$!
    local delay=0.1
    local spinstr='⣾⣽⣻⢿⡿⣟⣯⣷'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

confirm() {
    if [ "$AUTO_CONFIRM" = true ]; then
        return 0
    fi
    
    local prompt="$1 [y/N]: "
    read -p "$prompt" -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                          SYSTEM REQUIREMENTS CHECK                         ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

check_system_requirements() {
    print_section "System Requirements Check"
    
    local checks_passed=true
    
    # Check Docker
    info "Checking Docker installation..."
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if [ "$(printf '%s\n' "$REQUIRED_DOCKER_VERSION" "$docker_version" | sort -V | head -n1)" = "$REQUIRED_DOCKER_VERSION" ]; then
            success "Docker $docker_version found (minimum: $REQUIRED_DOCKER_VERSION)"
        else
            error "Docker version $docker_version is below minimum required version $REQUIRED_DOCKER_VERSION"
            checks_passed=false
        fi
    else
        error "Docker is not installed"
        checks_passed=false
    fi
    
    # Check Docker Compose
    info "Checking Docker Compose installation..."
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        success "Docker Compose found"
    else
        error "Docker Compose is not installed"
        checks_passed=false
    fi
    
    # Check available disk space
    info "Checking available disk space..."
    local available_space=$(df -BG "$SCRIPT_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -ge 5 ]; then
        success "Sufficient disk space available (${available_space}GB)"
    else
        warning "Low disk space: ${available_space}GB available (recommended: 5GB+)"
    fi
    
    # Check memory
    info "Checking system memory..."
    if [ "$(uname)" = "Darwin" ]; then
        local total_memory=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    else
        local total_memory=$(free -g | awk 'NR==2 {print $2}')
    fi
    
    if [ "$total_memory" -ge 4 ]; then
        success "Sufficient memory available (${total_memory}GB)"
    else
        warning "Low memory: ${total_memory}GB (recommended: 4GB+)"
    fi
    
    # Check network connectivity
    info "Checking network connectivity..."
    if ping -c 1 google.com &> /dev/null; then
        success "Network connectivity confirmed"
    else
        warning "No internet connectivity detected - some features may not work"
    fi
    
    if [ "$checks_passed" = false ] && [ "$SKIP_CHECKS" = false ]; then
        error "System requirements not met"
        echo
        echo "To skip checks, run with --skip-checks flag"
        exit 1
    fi
}

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                           PORT AVAILABILITY CHECK                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

check_ports() {
    print_section "Port Availability Check"
    
    local ports_to_check=()
    
    case "$ENVIRONMENT" in
        production)
            ports_to_check=(80 443 8080)
            ;;
        development)
            ports_to_check=(8101 3101 5434 6381)
            ;;
        *)
            ports_to_check=(8101 3101)
            ;;
    esac
    
    local port_conflicts=false
    
    for port in "${ports_to_check[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            error "Port $port is already in use"
            port_conflicts=true
            if command -v lsof &> /dev/null; then
                echo "  Process using port:"
                lsof -Pi :$port -sTCP:LISTEN | grep -v COMMAND | head -1
            fi
        else
            success "Port $port is available"
        fi
    done
    
    if [ "$port_conflicts" = true ]; then
        warning "Port conflicts detected"
        echo
        echo "Options:"
        echo "  1) Stop conflicting services"
        echo "  2) Modify port configuration in docker-compose files"
        echo "  3) Continue anyway (may cause issues)"
        
        if ! confirm "Continue despite port conflicts?"; then
            exit 1
        fi
    fi
}

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                          ENVIRONMENT SETUP                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

setup_environment() {
    print_section "Environment Configuration"
    
    local env_file=".env"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        env_file=".env.production"
    fi
    
    if [ -f "$env_file" ]; then
        warning "Environment file $env_file already exists"
        if confirm "Backup and regenerate environment file?"; then
            cp "$env_file" "${env_file}.backup.$(date +%Y%m%d_%H%M%S)"
            success "Existing environment backed up"
        else
            info "Using existing environment file"
            return
        fi
    fi
    
    info "Generating secure environment configuration..."
    
    # Generate secure passwords
    local db_password=$(generate_password)
    local redis_password=$(generate_password)
    local secret_key=$(generate_password)
    local jwt_secret=$(generate_password)
    
    cat > "$env_file" << EOF
# ═══════════════════════════════════════════════════════════════════════════
# Zenith Coder Environment Configuration
# Generated: $(date)
# Environment: $ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Core Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ENVIRONMENT=$ENVIRONMENT
DEBUG=$([ "$ENVIRONMENT" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$ENVIRONMENT" = "development" ] && echo "DEBUG" || echo "INFO")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Database Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POSTGRES_USER=zenith
POSTGRES_PASSWORD=$db_password
POSTGRES_DB=zenith_coder
DATABASE_URL=postgresql://zenith:$db_password@postgres:5432/zenith_coder

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Redis Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REDIS_PASSWORD=$redis_password
REDIS_URL=redis://:$redis_password@redis:6379

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Security
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECRET_KEY=$secret_key
JWT_SECRET_KEY=$jwt_secret
CORS_ORIGINS=["http://localhost:3000","http://localhost:3101","http://localhost:5173"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI Services (Add your API keys)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPENROUTER_API_KEY=
HUGGINGFACE_API_TOKEN=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Application Settings
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_PORT=8100
FRONTEND_PORT=3000
PROJECT_SCAN_PATH=/ai_projects

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Domain Configuration (Production)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOMAIN=localhost
LETSENCRYPT_EMAIL=admin@localhost
EOF
    
    success "Environment configuration generated"
    
    # Set restrictive permissions
    chmod 600 "$env_file"
    success "Environment file permissions set (600)"
    
    echo
    warning "IMPORTANT: Add your AI service API keys to $env_file"
    echo "  - OPENROUTER_API_KEY"
    echo "  - HUGGINGFACE_API_TOKEN"
    echo "  - ANTHROPIC_API_KEY (optional)"
    echo "  - OPENAI_API_KEY (optional)"
    echo
}

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                           INSTALLATION MODES                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

install_development() {
    print_section "Development Installation"
    
    info "Setting up development environment..."
    
    # Setup Python virtual environment
    if [ -d "backend/venv" ]; then
        info "Python virtual environment already exists"
    else
        info "Creating Python virtual environment..."
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
        cd ..
        success "Python environment setup complete"
    fi
    
    # Setup frontend dependencies
    if [ -d "frontend/node_modules" ]; then
        info "Frontend dependencies already installed"
    else
        info "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
        success "Frontend dependencies installed"
    fi
    
    # Start services
    info "Starting development services..."
    docker-compose -f docker-compose.yml up -d
    
    # Wait for services
    info "Waiting for services to be ready..."
    sleep 10
    
    # Run migrations
    info "Running database migrations..."
    docker exec zenith_backend python -m alembic upgrade head || true
    
    success "Development environment ready!"
    echo
    echo -e "${GREEN}Access your development environment:${NC}"
    echo "  Frontend: http://localhost:3101"
    echo "  Backend:  http://localhost:8101"
    echo "  Database: postgresql://localhost:5434/zenith_coder"
    echo "  Redis:    redis://localhost:6381"
}

install_production() {
    print_section "Production Installation"
    
    # Check if running as root (required for ports 80/443)
    if [[ $EUID -ne 0 ]] && [ "$SKIP_CHECKS" = false ]; then
        error "Production installation requires root privileges for ports 80/443"
        echo "Please run: sudo $0 --production"
        exit 1
    fi
    
    info "Building production containers..."
    docker-compose -f docker-compose.prod.yml build
    
    info "Starting production services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services
    info "Waiting for services to be healthy..."
    local retries=30
    local healthy=false
    
    for i in $(seq 1 $retries); do
        if docker-compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
            healthy=true
            break
        fi
        printf "."
        sleep 2
    done
    echo
    
    if [ "$healthy" = true ]; then
        success "All services are healthy"
    else
        error "Services failed health check"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi
    
    # Run migrations
    info "Running database migrations..."
    docker exec zenith_backend_prod python -m alembic upgrade head || true
    
    success "Production environment deployed!"
    echo
    echo -e "${GREEN}Access your production environment:${NC}"
    echo "  Application: https://${DOMAIN:-localhost}"
    echo "  API:         https://${DOMAIN:-localhost}/api"
    echo "  Traefik:     http://${DOMAIN:-localhost}:8080"
}

install_quick() {
    print_section "Quick Installation"
    
    info "Performing quick installation with defaults..."
    
    # Use development mode by default
    ENVIRONMENT="development"
    
    # Setup environment with defaults
    setup_environment
    
    # Start services
    info "Starting services..."
    docker-compose up -d
    
    success "Quick installation complete!"
    echo
    echo -e "${GREEN}Services are starting up...${NC}"
    echo "  Frontend: http://localhost:3101"
    echo "  Backend:  http://localhost:8101"
}

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                            MANAGEMENT FUNCTIONS                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

show_status() {
    print_section "System Status"
    
    echo -e "${CYAN}Docker Services:${NC}"
    docker-compose ps 2>/dev/null || docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo "No services running"
    
    echo
    echo -e "${CYAN}Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "No containers running"
    
    echo
    echo -e "${CYAN}Disk Usage:${NC}"
    docker system df
}

show_logs() {
    local service="${1:-}"
    
    if [ -z "$service" ]; then
        docker-compose logs -f --tail=100
    else
        docker-compose logs -f --tail=100 "$service"
    fi
}

backup_system() {
    print_section "System Backup"
    
    local backup_dir="backups/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup database
    info "Backing up database..."
    docker exec zenith_postgres pg_dump -U zenith zenith_coder > "$backup_dir/database.sql" 2>/dev/null || \
    docker exec zenith_postgres_prod pg_dump -U zenith zenith_coder > "$backup_dir/database.sql" 2>/dev/null || \
    warning "Could not backup database"
    
    # Backup environment files
    info "Backing up environment files..."
    cp .env* "$backup_dir/" 2>/dev/null || true
    
    # Backup docker volumes
    info "Backing up Docker volumes..."
    docker run --rm -v zenith_postgres_data:/data -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/postgres_data.tar.gz /data 2>/dev/null || true
    
    success "Backup completed: $backup_dir"
}

uninstall() {
    print_section "Uninstallation"
    
    warning "This will remove all Zenith Coder containers and data!"
    if ! confirm "Are you sure you want to uninstall?"; then
        info "Uninstallation cancelled"
        return
    fi
    
    if confirm "Create backup before uninstalling?"; then
        backup_system
    fi
    
    info "Stopping services..."
    docker-compose down -v 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
    
    info "Removing containers..."
    docker rm -f $(docker ps -a | grep zenith | awk '{print $1}') 2>/dev/null || true
    
    info "Removing volumes..."
    docker volume rm $(docker volume ls | grep zenith | awk '{print $2}') 2>/dev/null || true
    
    info "Removing images..."
    docker rmi $(docker images | grep zenith | awk '{print $3}') 2>/dev/null || true
    
    success "Uninstallation complete"
}

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                             INTERACTIVE MENU                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

show_menu() {
    print_header
    
    echo -e "${WHITE}Please select an installation option:${NC}"
    echo
    echo "  ${CYAN}1)${NC} Quick Install (Development mode with defaults)"
    echo "  ${CYAN}2)${NC} Development Installation (Full development setup)"
    echo "  ${CYAN}3)${NC} Production Installation (Production deployment)"
    echo "  ${CYAN}4)${NC} Custom Installation (Advanced options)"
    echo
    echo "  ${CYAN}5)${NC} Show System Status"
    echo "  ${CYAN}6)${NC} View Logs"
    echo "  ${CYAN}7)${NC} Backup System"
    echo "  ${CYAN}8)${NC} Uninstall"
    echo
    echo "  ${CYAN}0)${NC} Exit"
    echo
    
    read -p "Enter your choice [0-8]: " choice
    
    case $choice in
        1)
            INSTALL_MODE="quick"
            ENVIRONMENT="development"
            ;;
        2)
            INSTALL_MODE="development"
            ENVIRONMENT="development"
            ;;
        3)
            INSTALL_MODE="production"
            ENVIRONMENT="production"
            ;;
        4)
            custom_installation
            ;;
        5)
            show_status
            exit 0
            ;;
        6)
            show_logs
            exit 0
            ;;
        7)
            backup_system
            exit 0
            ;;
        8)
            uninstall
            exit 0
            ;;
        0)
            echo "Installation cancelled"
            exit 0
            ;;
        *)
            error "Invalid option"
            exit 1
            ;;
    esac
}

custom_installation() {
    print_section "Custom Installation"
    
    # Select environment
    echo "Select environment:"
    echo "  1) Development"
    echo "  2) Production"
    echo "  3) Testing"
    read -p "Choice [1-3]: " env_choice
    
    case $env_choice in
        1) ENVIRONMENT="development" ;;
        2) ENVIRONMENT="production" ;;
        3) ENVIRONMENT="testing" ;;
        *) ENVIRONMENT="development" ;;
    esac
    
    # Additional options
    if confirm "Skip system checks?"; then
        SKIP_CHECKS=true
    fi
    
    if confirm "Enable verbose logging?"; then
        VERBOSE=true
    fi
    
    if confirm "Auto-confirm all prompts?"; then
        AUTO_CONFIRM=true
    fi
    
    # Select installation mode based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        INSTALL_MODE="production"
    else
        INSTALL_MODE="development"
    fi
}

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                              MAIN EXECUTION                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick|-q)
                INSTALL_MODE="quick"
                ENVIRONMENT="development"
                AUTO_CONFIRM=true
                shift
                ;;
            --development|-d)
                INSTALL_MODE="development"
                ENVIRONMENT="development"
                shift
                ;;
            --production|-p)
                INSTALL_MODE="production"
                ENVIRONMENT="production"
                shift
                ;;
            --skip-checks)
                SKIP_CHECKS=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --yes|-y)
                AUTO_CONFIRM=true
                shift
                ;;
            --status)
                show_status
                exit 0
                ;;
            --logs)
                show_logs "$2"
                exit 0
                ;;
            --backup)
                backup_system
                exit 0
                ;;
            --uninstall)
                uninstall
                exit 0
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    print_header
    
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "OPTIONS:"
    echo "  --quick, -q          Quick installation with defaults"
    echo "  --development, -d    Development installation"
    echo "  --production, -p     Production installation"
    echo "  --skip-checks        Skip system requirement checks"
    echo "  --verbose, -v        Enable verbose output"
    echo "  --yes, -y            Auto-confirm all prompts"
    echo "  --status             Show system status"
    echo "  --logs [service]     View logs (optionally for specific service)"
    echo "  --backup             Create system backup"
    echo "  --uninstall          Remove Zenith Coder installation"
    echo "  --help, -h           Show this help message"
    echo
    echo "EXAMPLES:"
    echo "  $0                   Interactive installation"
    echo "  $0 --quick           Quick install with defaults"
    echo "  $0 --production -y   Production install with auto-confirm"
    echo "  $0 --logs backend    View backend logs"
}

main() {
    # Create log file
    touch "$LOG_FILE"
    log "Installation started - Version $SCRIPT_VERSION"
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # If no mode specified, show interactive menu
    if [ -z "$INSTALL_MODE" ]; then
        show_menu
    fi
    
    # Run system checks
    if [ "$SKIP_CHECKS" = false ]; then
        check_system_requirements
    fi
    
    # Check port availability
    check_ports
    
    # Setup environment
    setup_environment
    
    # Execute installation based on mode
    case "$INSTALL_MODE" in
        quick)
            install_quick
            ;;
        development)
            install_development
            ;;
        production)
            install_production
            ;;
        *)
            error "Invalid installation mode"
            exit 1
            ;;
    esac
    
    echo
    success "Installation completed successfully!"
    info "Log file: $LOG_FILE"
    echo
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║${WHITE}              Thank you for installing Zenith Coder!                  ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║${CYAN}                    Happy Vibecoding! 🚀✨                           ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
}

# Run main function
main "$@"