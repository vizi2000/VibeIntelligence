#!/bin/bash

# VibeIntelligence Configuration Script
# Manages API keys and configuration settings

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REMOTE_HOST="vizi@borgtools.ddns.net"
REMOTE_DIR="~/vibeintelligence"
LOCAL_ENV_FILE=".env.production"
CONFIG_MODE=""

# Helper functions
print_header() {
    echo
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║${WHITE}             VibeIntelligence Configuration Manager                   ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${CYAN}ℹ️  $1${NC}"; }

# Function to read secure input
read_secret() {
    local prompt="$1"
    local var_name="$2"
    echo -n "$prompt"
    read -s value
    echo
    eval "$var_name='$value'"
}

# Function to validate API key format
validate_api_key() {
    local key="$1"
    local service="$2"
    
    if [ -z "$key" ]; then
        return 1
    fi
    
    case "$service" in
        "openrouter")
            if [[ "$key" =~ ^sk-or-v[0-9]-[a-zA-Z0-9]{48,}$ ]]; then
                return 0
            fi
            ;;
        "anthropic")
            if [[ "$key" =~ ^sk-ant-[a-zA-Z0-9]{48,}$ ]]; then
                return 0
            fi
            ;;
        "openai")
            if [[ "$key" =~ ^sk-[a-zA-Z0-9]{48,}$ ]]; then
                return 0
            fi
            ;;
        "huggingface")
            if [[ "$key" =~ ^hf_[a-zA-Z0-9]{30,}$ ]]; then
                return 0
            fi
            ;;
        *)
            # Generic validation - at least 20 characters
            if [ ${#key} -ge 20 ]; then
                return 0
            fi
            ;;
    esac
    
    return 1
}

# Configure API Keys
configure_api_keys() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  API Keys Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # OpenRouter API Key
    echo -e "${CYAN}1. OpenRouter API Key${NC}"
    echo "   Get your key from: https://openrouter.ai/keys"
    read_secret "   Enter OpenRouter API Key (or press Enter to skip): " OPENROUTER_KEY
    if [ ! -z "$OPENROUTER_KEY" ]; then
        if validate_api_key "$OPENROUTER_KEY" "openrouter"; then
            success "OpenRouter API key format valid"
        else
            warning "OpenRouter API key format may be incorrect"
        fi
    fi
    echo
    
    # HuggingFace Token
    echo -e "${CYAN}2. HuggingFace API Token${NC}"
    echo "   Get your token from: https://huggingface.co/settings/tokens"
    read_secret "   Enter HuggingFace API Token (or press Enter to skip): " HUGGINGFACE_TOKEN
    if [ ! -z "$HUGGINGFACE_TOKEN" ]; then
        if validate_api_key "$HUGGINGFACE_TOKEN" "huggingface"; then
            success "HuggingFace token format valid"
        else
            warning "HuggingFace token format may be incorrect"
        fi
    fi
    echo
    
    # Anthropic API Key (Optional)
    echo -e "${CYAN}3. Anthropic API Key (Optional)${NC}"
    echo "   Get your key from: https://console.anthropic.com/settings/keys"
    read_secret "   Enter Anthropic API Key (or press Enter to skip): " ANTHROPIC_KEY
    if [ ! -z "$ANTHROPIC_KEY" ]; then
        if validate_api_key "$ANTHROPIC_KEY" "anthropic"; then
            success "Anthropic API key format valid"
        else
            warning "Anthropic API key format may be incorrect"
        fi
    fi
    echo
    
    # OpenAI API Key (Optional)
    echo -e "${CYAN}4. OpenAI API Key (Optional)${NC}"
    echo "   Get your key from: https://platform.openai.com/api-keys"
    read_secret "   Enter OpenAI API Key (or press Enter to skip): " OPENAI_KEY
    if [ ! -z "$OPENAI_KEY" ]; then
        if validate_api_key "$OPENAI_KEY" "openai"; then
            success "OpenAI API key format valid"
        else
            warning "OpenAI API key format may be incorrect"
        fi
    fi
    echo
}

# Configure Database
configure_database() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Database Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    echo "Current defaults:"
    echo "  • Database: vi_db"
    echo "  • User: vi_user"
    echo
    
    read -p "Change database password? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read_secret "Enter new database password: " DB_PASSWORD
        read_secret "Confirm database password: " DB_PASSWORD_CONFIRM
        
        if [ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]; then
            error "Passwords do not match!"
            DB_PASSWORD=""
        else
            success "Database password updated"
        fi
    fi
    echo
}

# Configure Domain
configure_domain() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Domain Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    echo "Current configuration:"
    echo "  • Primary domain: borg.tools"
    echo "  • Subdomain: vi.borg.tools"
    echo "  • Path access: borg.tools/vi"
    echo
    
    read -p "Change domain configuration? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter primary domain (e.g., borg.tools): " DOMAIN
        read -p "Enter subdomain (e.g., vi.borg.tools): " SUBDOMAIN
        read -p "Enter admin email for SSL certificates: " LETSENCRYPT_EMAIL
        success "Domain configuration updated"
    else
        DOMAIN="borg.tools"
        SUBDOMAIN="vi.borg.tools"
        LETSENCRYPT_EMAIL="admin@borg.tools"
    fi
    echo
}

# Configure Advanced Settings
configure_advanced() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Advanced Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # AI Model Selection
    echo -e "${CYAN}AI Model Configuration:${NC}"
    echo "  1) OpenRouter Horizon (default, recommended)"
    echo "  2) OpenAI GPT-4"
    echo "  3) Anthropic Claude"
    echo "  4) Local Models (requires setup)"
    read -p "Select AI model preference [1-4]: " model_choice
    
    case $model_choice in
        2) AI_MODEL="openai/gpt-4-turbo-preview" ;;
        3) AI_MODEL="anthropic/claude-3-opus" ;;
        4) AI_MODEL="local/llama-3" ;;
        *) AI_MODEL="openrouter/horizon-beta" ;;
    esac
    echo
    
    # Resource Limits
    echo -e "${CYAN}Resource Limits:${NC}"
    read -p "Max concurrent scans (default: 5): " MAX_SCANS
    MAX_SCANS=${MAX_SCANS:-5}
    
    read -p "Max project size in MB (default: 500): " MAX_PROJECT_SIZE
    MAX_PROJECT_SIZE=${MAX_PROJECT_SIZE:-500}
    
    read -p "Cache TTL in seconds (default: 3600): " CACHE_TTL
    CACHE_TTL=${CACHE_TTL:-3600}
    echo
    
    # Security Settings
    echo -e "${CYAN}Security Settings:${NC}"
    read -p "Enable rate limiting? [Y/n]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        RATE_LIMITING="true"
        read -p "Rate limit (requests per minute, default: 60): " RATE_LIMIT
        RATE_LIMIT=${RATE_LIMIT:-60}
    else
        RATE_LIMITING="false"
    fi
    echo
    
    success "Advanced settings configured"
}

# Generate environment file
generate_env_file() {
    info "Generating environment configuration..."
    
    # Generate secure defaults if not provided
    DB_PASSWORD=${DB_PASSWORD:-$(openssl rand -hex 16)}
    REDIS_PASSWORD=${REDIS_PASSWORD:-$(openssl rand -hex 16)}
    SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}
    JWT_SECRET=${JWT_SECRET:-$(openssl rand -hex 32)}
    
    cat > "$LOCAL_ENV_FILE" << EOF
# ═══════════════════════════════════════════════════════════════════════════
# VibeIntelligence Configuration
# Generated: $(date)
# ═══════════════════════════════════════════════════════════════════════════

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Environment
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Database Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POSTGRES_USER=vi_user
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_DB=vi_db
DATABASE_URL=postgresql://vi_user:$DB_PASSWORD@postgres:5432/vi_db
DB_PASSWORD=$DB_PASSWORD

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Redis Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379
CACHE_TTL=${CACHE_TTL:-3600}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Security
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
CORS_ORIGINS=["https://${SUBDOMAIN:-vi.borg.tools}","https://${DOMAIN:-borg.tools}","http://localhost:3000","http://localhost:5173"]

# Rate Limiting
RATE_LIMITING=${RATE_LIMITING:-true}
RATE_LIMIT_PER_MINUTE=${RATE_LIMIT:-60}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI Services
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPENROUTER_API_KEY=$OPENROUTER_KEY
HUGGINGFACE_API_TOKEN=$HUGGINGFACE_TOKEN
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
OPENAI_API_KEY=$OPENAI_KEY

# AI Model Configuration
DEFAULT_AI_MODEL=${AI_MODEL:-openrouter/horizon-beta}
ENABLE_LOCAL_MODELS=false

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Application Settings
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_PORT=8000
FRONTEND_PORT=80
PROJECT_SCAN_PATH=/ai_projects
AI_PROJECTS_PATH=/home/vizi/projects

# Resource Limits
MAX_CONCURRENT_SCANS=${MAX_SCANS:-5}
MAX_PROJECT_SIZE_MB=${MAX_PROJECT_SIZE:-500}
MAX_FILE_SIZE_MB=50
SCAN_TIMEOUT_SECONDS=300

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Domain Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOMAIN=${DOMAIN:-borg.tools}
SUBDOMAIN=${SUBDOMAIN:-vi.borg.tools}
LETSENCRYPT_EMAIL=${LETSENCRYPT_EMAIL:-admin@borg.tools}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Feature Flags
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ENABLE_AGENT_SYSTEM=true
ENABLE_DOCUMENTATION_GENERATION=true
ENABLE_DEPLOYMENT_MANAGER=true
ENABLE_AI_SUGGESTIONS=true
ENABLE_METRICS_COLLECTION=true
ENABLE_CHROMADB=false

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Monitoring
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SENTRY_DSN=
PROMETHEUS_ENABLED=false
GRAFANA_ENABLED=false
EOF
    
    success "Environment file generated: $LOCAL_ENV_FILE"
}

# Deploy configuration to server
deploy_config() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Deploying Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # Backup existing configuration
    info "Backing up existing configuration..."
    ssh $REMOTE_HOST "cd $REMOTE_DIR && [ -f .env ] && cp .env .env.backup.\$(date +%Y%m%d_%H%M%S) || true"
    
    # Upload new configuration
    info "Uploading new configuration..."
    scp "$LOCAL_ENV_FILE" "$REMOTE_HOST:$REMOTE_DIR/.env"
    
    # Set proper permissions
    info "Setting secure permissions..."
    ssh $REMOTE_HOST "cd $REMOTE_DIR && chmod 600 .env"
    
    # Restart services
    read -p "Restart services now? [Y/n]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        info "Restarting services..."
        ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml restart"
        success "Services restarted with new configuration"
    else
        warning "Remember to restart services for changes to take effect:"
        echo "  ssh $REMOTE_HOST 'cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml restart'"
    fi
    
    echo
    success "Configuration deployed successfully!"
}

# View current configuration
view_config() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Current Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    ssh $REMOTE_HOST "cd $REMOTE_DIR && if [ -f .env ]; then cat .env | grep -E '^[A-Z]' | sed 's/=.*$/=<hidden>/' | grep -E '(API_KEY|TOKEN|PASSWORD)' || echo 'No sensitive configuration found'; else echo 'No configuration file found'; fi"
}

# Test configuration
test_config() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Testing Configuration${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # Test database connection
    info "Testing database connection..."
    ssh $REMOTE_HOST "cd $REMOTE_DIR && docker exec vi_backend python -c 'from src.core.database import engine; print(\"✅ Database connection successful\")' 2>/dev/null || echo '❌ Database connection failed'"
    
    # Test Redis connection
    info "Testing Redis connection..."
    ssh $REMOTE_HOST "cd $REMOTE_DIR && docker exec vi_backend python -c 'import redis; r = redis.from_url(\"redis://redis:6379\"); r.ping(); print(\"✅ Redis connection successful\")' 2>/dev/null || echo '❌ Redis connection failed'"
    
    # Test API endpoints
    info "Testing API health endpoint..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://borgtools.ddns.net:8100/api/v1/health)
    if [ "$response" = "200" ]; then
        success "API health check passed"
    else
        error "API health check failed (HTTP $response)"
    fi
    
    # Test frontend
    info "Testing frontend..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://borgtools.ddns.net:8101)
    if [ "$response" = "200" ]; then
        success "Frontend accessible"
    else
        error "Frontend not accessible (HTTP $response)"
    fi
    
    echo
}

# Interactive menu
show_menu() {
    echo "Select configuration option:"
    echo
    echo "  ${CYAN}1)${NC} Quick Setup (API keys only)"
    echo "  ${CYAN}2)${NC} Full Configuration (all settings)"
    echo "  ${CYAN}3)${NC} View Current Configuration"
    echo "  ${CYAN}4)${NC} Test Configuration"
    echo "  ${CYAN}5)${NC} Deploy Existing .env File"
    echo
    echo "  ${CYAN}0)${NC} Exit"
    echo
    
    read -p "Enter your choice [0-5]: " choice
    
    case $choice in
        1)
            CONFIG_MODE="quick"
            ;;
        2)
            CONFIG_MODE="full"
            ;;
        3)
            view_config
            exit 0
            ;;
        4)
            test_config
            exit 0
            ;;
        5)
            if [ -f "$LOCAL_ENV_FILE" ]; then
                deploy_config
            else
                error "No local .env.production file found"
            fi
            exit 0
            ;;
        0)
            echo "Configuration cancelled"
            exit 0
            ;;
        *)
            error "Invalid option"
            exit 1
            ;;
    esac
}

# Main execution
main() {
    print_header
    
    # Parse command line arguments
    case "${1:-}" in
        --quick|-q)
            CONFIG_MODE="quick"
            ;;
        --full|-f)
            CONFIG_MODE="full"
            ;;
        --view|-v)
            view_config
            exit 0
            ;;
        --test|-t)
            test_config
            exit 0
            ;;
        --deploy|-d)
            if [ -f "$LOCAL_ENV_FILE" ]; then
                deploy_config
            else
                error "No local .env.production file found"
                exit 1
            fi
            exit 0
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "OPTIONS:"
            echo "  --quick, -q     Quick setup (API keys only)"
            echo "  --full, -f      Full configuration"
            echo "  --view, -v      View current configuration"
            echo "  --test, -t      Test configuration"
            echo "  --deploy, -d    Deploy existing .env file"
            echo "  --help, -h      Show this help message"
            echo
            echo "Without options, runs in interactive mode"
            exit 0
            ;;
        "")
            show_menu
            ;;
        *)
            error "Unknown option: $1"
            echo "Run $0 --help for usage"
            exit 1
            ;;
    esac
    
    # Execute configuration based on mode
    if [ "$CONFIG_MODE" = "quick" ]; then
        configure_api_keys
        generate_env_file
        deploy_config
    elif [ "$CONFIG_MODE" = "full" ]; then
        configure_api_keys
        configure_database
        configure_domain
        configure_advanced
        generate_env_file
        deploy_config
    fi
    
    echo
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Configuration Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo
    echo "Access your VibeIntelligence instance at:"
    echo "  • http://borgtools.ddns.net:8101 (Frontend)"
    echo "  • http://borgtools.ddns.net:8100/api/v1/health (API)"
    echo
    echo "Future domain access (pending DNS/nginx setup):"
    echo "  • https://vi.borg.tools"
    echo "  • https://borg.tools/vi"
    echo
}

# Run main function
main "$@"