#!/bin/bash
# Chain Of Record - Quick Start Script
# One-command setup for development environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA_DIR="$REPO_DIR/infra"
BACKEND_DIR="$REPO_DIR/backend"
MAX_WAIT=120  # Maximum seconds to wait for services

echo "=================================================================="
echo -e "${CYAN}CHAIN OF RECORD - QUICK START${NC}"
echo "=================================================================="
echo "Repository: $REPO_DIR"
echo "Time: $(date)"
echo ""

# Function to print status
print_status() {
    local message=$1
    echo -e "${BLUE}==>${NC} $message"
}

print_success() {
    local message=$1
    echo -e "${GREEN}✓${NC} $message"
}

print_warning() {
    local message=$1
    echo -e "${YELLOW}⚠${NC} $message"
}

print_error() {
    local message=$1
    echo -e "${RED}✗${NC} $message"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check prerequisites
print_status "Checking prerequisites..."
echo ""

MISSING_DEPS=0

if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker installed: $DOCKER_VERSION"
else
    print_error "Docker not found"
    MISSING_DEPS=1
fi

if command_exists docker-compose; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_success "Docker Compose installed: $COMPOSE_VERSION"
else
    print_error "Docker Compose not found"
    MISSING_DEPS=1
fi

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python installed: $PYTHON_VERSION"
else
    print_warning "Python not found (optional for local dev)"
fi

if command_exists git; then
    GIT_VERSION=$(git --version)
    print_success "Git installed: $GIT_VERSION"
else
    print_warning "Git not found (optional)"
fi

if command_exists curl; then
    print_success "curl installed"
else
    print_error "curl not found (required for testing)"
    MISSING_DEPS=1
fi

echo ""

if [ $MISSING_DEPS -eq 1 ]; then
    print_error "Missing required dependencies. Please install and try again."
    echo ""
    echo "Installation instructions:"
    echo "  Docker: https://docs.docker.com/get-docker/"
    echo "  Docker Compose: https://docs.docker.com/compose/install/"
    echo "  curl: apt install curl (Ubuntu) or brew install curl (macOS)"
    exit 1
fi

# Step 2: Check if services are already running
print_status "Checking for running services..."

if docker ps | grep -q "chain-postgres\|chain-backend"; then
    print_warning "Chain Of Record services are already running"
    echo ""
    read -p "Stop and restart services? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping existing services..."
        cd "$INFRA_DIR"
        docker-compose down
        print_success "Services stopped"
    else
        print_status "Skipping service restart"
    fi
else
    print_success "No existing services found"
fi

echo ""

# Step 3: Start Docker Compose services
print_status "Starting Docker Compose services..."
cd "$INFRA_DIR"

if docker-compose up -d; then
    print_success "Docker Compose started"
else
    print_error "Failed to start Docker Compose"
    exit 1
fi

echo ""

# Step 4: Wait for services to be healthy
print_status "Waiting for services to be healthy..."
echo ""

WAIT_TIME=0
POSTGRES_READY=0
BACKEND_READY=0

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    # Check PostgreSQL
    if [ $POSTGRES_READY -eq 0 ]; then
        if docker-compose exec -T postgres pg_isready -U chain -d chain >/dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            POSTGRES_READY=1
        else
            echo -n "."
        fi
    fi
    
    # Check Backend (only after PostgreSQL is ready)
    if [ $POSTGRES_READY -eq 1 ] && [ $BACKEND_READY -eq 0 ]; then
        if curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend API is ready"
            BACKEND_READY=1
        else
            echo -n "."
        fi
    fi
    
    # Break if all services are ready
    if [ $POSTGRES_READY -eq 1 ] && [ $BACKEND_READY -eq 1 ]; then
        break
    fi
    
    sleep 2
    WAIT_TIME=$((WAIT_TIME + 2))
done

echo ""

if [ $POSTGRES_READY -eq 0 ] || [ $BACKEND_READY -eq 0 ]; then
    print_error "Services did not become healthy within ${MAX_WAIT}s"
    echo ""
    print_status "Checking service status..."
    docker-compose ps
    echo ""
    print_status "Backend logs:"
    docker-compose logs --tail=20 backend
    exit 1
fi

# Step 5: Verify database schema
print_status "Verifying database schema..."

TABLE_COUNT=$(docker-compose exec -T postgres psql -U chain -d chain -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null | tr -d ' ')

if [ "$TABLE_COUNT" -ge 8 ]; then
    print_success "Database schema created ($TABLE_COUNT tables)"
else
    print_warning "Database may not be fully initialized ($TABLE_COUNT tables)"
fi

echo ""

# Step 6: Optional data seeding
print_status "Data seeding (optional)"
echo ""
echo "Would you like to seed the database with sample data?"
echo "  1) No seeding (empty database)"
echo "  2) Basic test data (1 entity, quick)"
echo "  3) Realistic entities (3 entities with varied risk profiles)"
echo "  4) Comprehensive dataset (10 entities, full demo)"
echo ""
read -p "Enter choice (1-4) [default: 1]: " SEED_CHOICE

case $SEED_CHOICE in
    2)
        print_status "Seeding basic test data..."
        docker-compose exec -T backend python scripts/init_db.py
        print_success "Basic data seeded"
        ;;
    3)
        print_status "Seeding realistic entities..."
        docker-compose exec -T backend python scripts/init_db.py
        docker-compose exec -T backend python scripts/seed_data.py
        print_success "Realistic data seeded"
        ;;
    4)
        print_status "Seeding comprehensive dataset..."
        docker-compose exec -T backend python scripts/init_db.py
        docker-compose exec -T backend python scripts/seed_data.py
        docker-compose exec -T backend python scripts/seed_sample_data.py
        print_success "Comprehensive data seeded"
        ;;
    *)
        print_status "Skipping data seeding"
        ;;
esac

echo ""

# Step 7: Display service information
echo "=================================================================="
echo -e "${GREEN}✓ SETUP COMPLETE${NC}"
echo "=================================================================="
echo ""
echo "Services are running:"
echo ""
echo -e "  ${CYAN}API Server:${NC}          http://localhost:8000"
echo -e "  ${CYAN}API Documentation:${NC}   http://localhost:8000/docs"
echo -e "  ${CYAN}OpenAPI Schema:${NC}      http://localhost:8000/openapi.json"
echo -e "  ${CYAN}pgAdmin:${NC}             http://localhost:5050"
echo -e "  ${CYAN}PostgreSQL:${NC}          localhost:5432"
echo ""
echo "pgAdmin credentials:"
echo "  Email:    admin@chainofrecord.com"
echo "  Password: admin123"
echo ""
echo "Database credentials:"
echo "  Host:     localhost"
echo "  Port:     5432"
echo "  Database: chain"
echo "  User:     chain"
echo "  Password: chain"
echo ""

# Step 8: Test API
print_status "Testing API endpoints..."
echo ""

HEALTH_STATUS=$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' || echo "error")
if echo "$HEALTH_STATUS" | grep -q "healthy"; then
    print_success "API health check passed"
else
    print_warning "API health check returned: $HEALTH_STATUS"
fi

ENTITY_COUNT=$(curl -s "http://localhost:8000/api/v1/entities" | grep -o '"id"' | wc -l || echo "0")
echo -e "${BLUE}==>${NC} Entities in database: $ENTITY_COUNT"

echo ""

# Step 9: Provide next steps
echo "=================================================================="
echo "NEXT STEPS"
echo "=================================================================="
echo ""
echo "1. Explore the API:"
echo "   ${CYAN}open http://localhost:8000/docs${NC}"
echo ""
echo "2. Test API endpoints:"
echo "   ${CYAN}curl http://localhost:8000/api/v1/entities${NC}"
echo "   ${CYAN}curl http://localhost:8000/api/v1/properties${NC}"
echo "   ${CYAN}curl http://localhost:8000/api/v1/scores/high-risk${NC}"
echo ""
echo "3. Run comprehensive API tests:"
echo "   ${CYAN}cd backend && ./scripts/test_api.sh${NC}"
echo ""
echo "4. Access database with pgAdmin:"
echo "   ${CYAN}open http://localhost:5050${NC}"
echo ""
echo "5. View service logs:"
echo "   ${CYAN}cd infra && docker-compose logs -f backend${NC}"
echo ""
echo "6. Stop services:"
echo "   ${CYAN}cd infra && docker-compose down${NC}"
echo ""
echo "7. Read documentation:"
echo "   ${CYAN}cat docs/SETUP_GUIDE.md${NC}"
echo "   ${CYAN}cat docs/DEVELOPMENT.md${NC}"
echo ""

# Step 10: Optional - Open browser
if command_exists open; then
    # macOS
    read -p "Open API documentation in browser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:8000/docs
        print_success "Browser opened"
    fi
elif command_exists xdg-open; then
    # Linux
    read -p "Open API documentation in browser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open http://localhost:8000/docs
        print_success "Browser opened"
    fi
fi

echo ""
echo "=================================================================="
echo -e "${GREEN}Happy Building! 🚀${NC}"
echo "=================================================================="
