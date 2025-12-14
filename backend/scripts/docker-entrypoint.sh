#!/bin/bash
# Docker entrypoint script for Chain Of Record backend
# Waits for PostgreSQL and runs Alembic migrations before starting the server

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=================================================================="
echo "CHAIN OF RECORD - BACKEND STARTUP"
echo "=================================================================="

# Configuration
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-chain}"
DB_NAME="${DB_NAME:-chain}"
MAX_RETRIES="${MAX_RETRIES:-30}"
RETRY_INTERVAL="${RETRY_INTERVAL:-2}"

echo "Database: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""

# Function to check if PostgreSQL is ready
wait_for_postgres() {
    echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
    
    retries=0
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
        retries=$((retries + 1))
        
        if [ $retries -ge $MAX_RETRIES ]; then
            echo -e "${RED}✗ PostgreSQL is not available after $MAX_RETRIES attempts${NC}"
            exit 1
        fi
        
        echo -e "  Attempt $retries/$MAX_RETRIES: PostgreSQL is unavailable - sleeping ${RETRY_INTERVAL}s"
        sleep $RETRY_INTERVAL
    done
    
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
    echo ""
}

# Function to run Alembic migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    
    # Check if alembic is available
    if ! command -v alembic &> /dev/null; then
        echo -e "${RED}✗ Alembic not found. Installing...${NC}"
        pip install alembic
    fi
    
    # Run migrations
    if python -m alembic upgrade head; then
        echo -e "${GREEN}✓ Migrations completed successfully${NC}"
    else
        echo -e "${RED}✗ Migration failed${NC}"
        exit 1
    fi
    echo ""
}

# Function to seed initial data (optional)
seed_initial_data() {
    if [ "${SEED_DATA:-false}" == "true" ]; then
        echo -e "${YELLOW}Seeding initial data...${NC}"
        
        if [ -f "/app/scripts/init_db.py" ]; then
            if python /app/scripts/init_db.py; then
                echo -e "${GREEN}✓ Initial data seeded${NC}"
            else
                echo -e "${YELLOW}⚠ Initial data seeding failed (may already exist)${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ init_db.py not found, skipping seeding${NC}"
        fi
        echo ""
    fi
}

# Main execution
wait_for_postgres
run_migrations
seed_initial_data

echo "=================================================================="
echo "STARTING UVICORN SERVER"
echo "=================================================================="
echo "Host: ${HOST:-0.0.0.0}"
echo "Port: ${PORT:-8000}"
echo "Reload: ${RELOAD:-false}"
echo ""

# Start the application
if [ "${RELOAD:-false}" == "true" ]; then
    exec uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}" --reload
else
    exec uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
fi
