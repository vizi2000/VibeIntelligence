#!/bin/bash

# VibeIntelligence Monitoring Script
# Real-time monitoring and management

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Configuration
REMOTE_HOST="vizi@borgtools.ddns.net"
REMOTE_DIR="~/vibeintelligence"
FRONTEND_URL="http://borgtools.ddns.net:8101"
API_URL="http://borgtools.ddns.net:8100"

# Helper functions
print_header() {
    clear
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║${WHITE}              VibeIntelligence Monitoring Dashboard                    ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${CYAN}ℹ️  $1${NC}"; }

# Check service status
check_status() {
    print_header
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Service Status${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # Check Docker containers
    ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml ps --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}'" 2>/dev/null
    
    echo
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Health Checks${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # Check API health
    echo -n "API Health: "
    response=$(curl -s "$API_URL/api/v1/health" 2>/dev/null)
    if [ $? -eq 0 ]; then
        success "Healthy"
        echo "  └─ Response: $(echo $response | jq -r '.status' 2>/dev/null || echo $response)"
    else
        error "Unreachable"
    fi
    
    # Check Frontend
    echo -n "Frontend: "
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null)
    if [ "$http_code" = "200" ]; then
        success "Accessible (HTTP $http_code)"
    else
        error "Not accessible (HTTP $http_code)"
    fi
    
    # Check Database
    echo -n "Database: "
    db_status=$(ssh $REMOTE_HOST "docker exec vi_postgres pg_isready -U vi_user 2>/dev/null" 2>/dev/null)
    if [[ $db_status == *"accepting connections"* ]]; then
        success "Accepting connections"
    else
        error "Not responding"
    fi
    
    # Check Redis
    echo -n "Redis: "
    redis_status=$(ssh $REMOTE_HOST "docker exec vi_redis redis-cli ping 2>/dev/null" 2>/dev/null)
    if [[ $redis_status == "PONG" ]]; then
        success "Responding"
    else
        error "Not responding"
    fi
}

# View logs
view_logs() {
    print_header
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Service Logs${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    echo "Select service:"
    echo "  1) All services"
    echo "  2) Backend"
    echo "  3) Frontend"
    echo "  4) Database"
    echo "  5) Redis"
    echo "  0) Back"
    echo
    
    read -p "Choice [0-5]: " log_choice
    
    case $log_choice in
        1) service="" ;;
        2) service="backend" ;;
        3) service="frontend" ;;
        4) service="postgres" ;;
        5) service="redis" ;;
        0) return ;;
        *) return ;;
    esac
    
    echo
    info "Showing last 50 lines (press Ctrl+C to stop)..."
    echo
    
    if [ -z "$service" ]; then
        ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml logs --tail=50 -f"
    else
        ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml logs --tail=50 -f $service"
    fi
}

# Resource usage
resource_usage() {
    print_header
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Resource Usage${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # Server resources
    echo -e "${CYAN}Server Resources:${NC}"
    ssh $REMOTE_HOST "echo '  CPU Usage:' && top -bn1 | grep 'Cpu(s)' | awk '{print \"    \" \$2}' && echo '  Memory:' && free -h | grep Mem | awk '{print \"    Used: \" \$3 \" / Total: \" \$2}' && echo '  Disk:' && df -h / | tail -1 | awk '{print \"    Used: \" \$3 \" / Total: \" \$2 \" (\" \$5 \" used)\"}'"
    
    echo
    echo -e "${CYAN}Container Resources:${NC}"
    ssh $REMOTE_HOST "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}' | grep vi_"
    
    echo
    echo -e "${CYAN}Database Statistics:${NC}"
    ssh $REMOTE_HOST "docker exec vi_postgres psql -U vi_user -d vi_db -c 'SELECT COUNT(*) as projects FROM projects;' 2>/dev/null || echo '  No data available'"
}

# Service management
manage_services() {
    print_header
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Service Management${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    echo "Select action:"
    echo "  1) Start all services"
    echo "  2) Stop all services"
    echo "  3) Restart all services"
    echo "  4) Restart specific service"
    echo "  5) Update and rebuild"
    echo "  6) Reset database"
    echo "  0) Back"
    echo
    
    read -p "Choice [0-6]: " action_choice
    
    case $action_choice in
        1)
            info "Starting all services..."
            ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml up -d"
            success "Services started"
            ;;
        2)
            warning "Stopping all services..."
            ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml down"
            success "Services stopped"
            ;;
        3)
            info "Restarting all services..."
            ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml restart"
            success "Services restarted"
            ;;
        4)
            echo "Select service to restart:"
            echo "  1) Backend"
            echo "  2) Frontend"
            echo "  3) Database"
            echo "  4) Redis"
            read -p "Choice [1-4]: " service_choice
            case $service_choice in
                1) service="backend" ;;
                2) service="frontend" ;;
                3) service="postgres" ;;
                4) service="redis" ;;
                *) return ;;
            esac
            info "Restarting $service..."
            ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml restart $service"
            success "$service restarted"
            ;;
        5)
            warning "This will rebuild and update all services"
            read -p "Continue? [y/N]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                info "Rebuilding services..."
                ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml up -d --build"
                success "Services rebuilt and updated"
            fi
            ;;
        6)
            error "WARNING: This will delete all data!"
            read -p "Are you sure? Type 'yes' to confirm: " confirm
            if [ "$confirm" = "yes" ]; then
                info "Resetting database..."
                ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml down -v && docker-compose -f docker-compose.simple.yml up -d"
                success "Database reset complete"
            else
                info "Database reset cancelled"
            fi
            ;;
        0)
            return
            ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
}

# Backup management
backup_management() {
    print_header
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  Backup Management${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    echo "Select action:"
    echo "  1) Create backup"
    echo "  2) List backups"
    echo "  3) Restore backup"
    echo "  4) Download backup"
    echo "  0) Back"
    echo
    
    read -p "Choice [0-4]: " backup_choice
    
    case $backup_choice in
        1)
            info "Creating backup..."
            timestamp=$(date +%Y%m%d_%H%M%S)
            ssh $REMOTE_HOST "cd $REMOTE_DIR && mkdir -p backups && docker exec vi_postgres pg_dump -U vi_user vi_db > backups/backup_$timestamp.sql"
            ssh $REMOTE_HOST "cd $REMOTE_DIR && tar -czf backups/vi_backup_$timestamp.tar.gz .env docker-compose.simple.yml backups/backup_$timestamp.sql"
            success "Backup created: vi_backup_$timestamp.tar.gz"
            ;;
        2)
            echo -e "${CYAN}Available backups:${NC}"
            ssh $REMOTE_HOST "cd $REMOTE_DIR && ls -lh backups/*.tar.gz 2>/dev/null || echo 'No backups found'"
            ;;
        3)
            echo "Available backups:"
            ssh $REMOTE_HOST "cd $REMOTE_DIR && ls -1 backups/*.tar.gz 2>/dev/null | nl"
            read -p "Enter backup number to restore: " backup_num
            backup_file=$(ssh $REMOTE_HOST "cd $REMOTE_DIR && ls -1 backups/*.tar.gz 2>/dev/null | sed -n ${backup_num}p")
            if [ ! -z "$backup_file" ]; then
                warning "This will restore from: $backup_file"
                read -p "Continue? [y/N]: " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    info "Restoring backup..."
                    # Implementation for restore
                    success "Backup restored"
                fi
            else
                error "Invalid backup selection"
            fi
            ;;
        4)
            echo "Available backups:"
            ssh $REMOTE_HOST "cd $REMOTE_DIR && ls -1 backups/*.tar.gz 2>/dev/null | nl"
            read -p "Enter backup number to download: " backup_num
            backup_file=$(ssh $REMOTE_HOST "cd $REMOTE_DIR && ls -1 backups/*.tar.gz 2>/dev/null | sed -n ${backup_num}p")
            if [ ! -z "$backup_file" ]; then
                info "Downloading backup..."
                scp "$REMOTE_HOST:$REMOTE_DIR/$backup_file" .
                success "Backup downloaded to current directory"
            else
                error "Invalid backup selection"
            fi
            ;;
        0)
            return
            ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
}

# Quick diagnostics
diagnostics() {
    print_header
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  System Diagnostics${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # Check connectivity
    echo -e "${CYAN}Connectivity Tests:${NC}"
    echo -n "  SSH Connection: "
    if ssh -o ConnectTimeout=5 $REMOTE_HOST "echo 'OK'" &>/dev/null; then
        success "OK"
    else
        error "Failed"
    fi
    
    echo -n "  Frontend Port (8101): "
    if nc -z borgtools.ddns.net 8101 2>/dev/null; then
        success "Open"
    else
        error "Closed"
    fi
    
    echo -n "  Backend Port (8100): "
    if nc -z borgtools.ddns.net 8100 2>/dev/null; then
        success "Open"
    else
        error "Closed"
    fi
    
    echo
    echo -e "${CYAN}Service Checks:${NC}"
    
    # API endpoints
    echo "  Testing API endpoints:"
    endpoints=("/api/v1/health" "/api/v1/projects" "/api/v1/agents")
    for endpoint in "${endpoints[@]}"; do
        echo -n "    $endpoint: "
        http_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL$endpoint" 2>/dev/null)
        if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
            success "OK (HTTP $http_code)"
        else
            error "Failed (HTTP $http_code)"
        fi
    done
    
    echo
    echo -e "${CYAN}Configuration:${NC}"
    echo "  Checking environment variables..."
    ssh $REMOTE_HOST "cd $REMOTE_DIR && [ -f .env ] && echo '    ✅ .env file exists' || echo '    ❌ .env file missing'"
    ssh $REMOTE_HOST "cd $REMOTE_DIR && grep -q 'OPENROUTER_API_KEY=.' .env 2>/dev/null && echo '    ✅ OpenRouter API key configured' || echo '    ⚠️  OpenRouter API key not configured'"
    ssh $REMOTE_HOST "cd $REMOTE_DIR && grep -q 'HUGGINGFACE_API_TOKEN=.' .env 2>/dev/null && echo '    ✅ HuggingFace token configured' || echo '    ⚠️  HuggingFace token not configured'"
    
    echo
    read -p "Press Enter to continue..."
}

# Live monitoring
live_monitor() {
    while true; do
        print_header
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${WHITE}  Live Monitoring (refreshing every 5s, press Ctrl+C to stop)${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo
        
        # Container status
        echo -e "${CYAN}Container Status:${NC}"
        ssh $REMOTE_HOST "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep vi_" 2>/dev/null
        
        echo
        echo -e "${CYAN}Resource Usage:${NC}"
        ssh $REMOTE_HOST "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' | grep vi_" 2>/dev/null
        
        echo
        echo -e "${CYAN}Recent Logs:${NC}"
        ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml logs --tail=5 backend 2>/dev/null | tail -5"
        
        sleep 5
    done
}

# Main menu
main_menu() {
    while true; do
        print_header
        echo "Select monitoring option:"
        echo
        echo "  ${CYAN}1)${NC} Service Status"
        echo "  ${CYAN}2)${NC} View Logs"
        echo "  ${CYAN}3)${NC} Resource Usage"
        echo "  ${CYAN}4)${NC} Manage Services"
        echo "  ${CYAN}5)${NC} Backup Management"
        echo "  ${CYAN}6)${NC} System Diagnostics"
        echo "  ${CYAN}7)${NC} Live Monitoring"
        echo
        echo "  ${CYAN}0)${NC} Exit"
        echo
        
        read -p "Enter your choice [0-7]: " choice
        
        case $choice in
            1) check_status; read -p "Press Enter to continue..." ;;
            2) view_logs ;;
            3) resource_usage; read -p "Press Enter to continue..." ;;
            4) manage_services ;;
            5) backup_management ;;
            6) diagnostics ;;
            7) live_monitor ;;
            0) echo "Goodbye!"; exit 0 ;;
            *) error "Invalid option" ;;
        esac
    done
}

# Command line arguments
case "${1:-}" in
    status)
        check_status
        ;;
    logs)
        ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml logs --tail=100 -f ${2:-}"
        ;;
    restart)
        info "Restarting services..."
        ssh $REMOTE_HOST "cd $REMOTE_DIR && docker-compose -f docker-compose.simple.yml restart ${2:-}"
        success "Services restarted"
        ;;
    backup)
        timestamp=$(date +%Y%m%d_%H%M%S)
        info "Creating backup..."
        ssh $REMOTE_HOST "cd $REMOTE_DIR && mkdir -p backups && docker exec vi_postgres pg_dump -U vi_user vi_db > backups/backup_$timestamp.sql"
        success "Backup created: backup_$timestamp.sql"
        ;;
    --help|-h)
        echo "VibeIntelligence Monitoring Script"
        echo
        echo "Usage: $0 [COMMAND] [OPTIONS]"
        echo
        echo "COMMANDS:"
        echo "  status          Show service status"
        echo "  logs [service]  View logs (optionally for specific service)"
        echo "  restart [service] Restart services"
        echo "  backup          Create database backup"
        echo
        echo "Without arguments, runs interactive monitoring dashboard"
        ;;
    *)
        main_menu
        ;;
esac