# Chain Of Record - Setup Guide

Complete guide for setting up Chain Of Record in different environments.

## Table of Contents

1. [Quick Start (5 Minutes)](#quick-start-5-minutes)
2. [Prerequisites](#prerequisites)
3. [Docker Setup](#docker-setup)
4. [Local Development Setup](#local-development-setup)
5. [Database Setup](#database-setup)
6. [Data Seeding](#data-seeding)
7. [API Testing](#api-testing)
8. [Docker Service Management](#docker-service-management)
9. [Troubleshooting](#troubleshooting)
10. [Verification Steps](#verification-steps)

---

## Quick Start (5 Minutes)

Get up and running with Docker in under 5 minutes:

```bash
# Clone the repository
git clone https://github.com/Adahandles/Chain-Of-Record.git
cd Chain-Of-Record

# Start all services with Docker Compose
cd infra
docker-compose up -d

# Wait for services to be healthy (about 30 seconds)
docker-compose ps

# Verify the API is running
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs  # macOS
# or
xdg-open http://localhost:8000/docs  # Linux
# or visit http://localhost:8000/docs in your browser
```

That's it! The database schema is automatically created via Alembic migrations on startup.

### Optional: Seed Sample Data

```bash
# Access the backend container
docker-compose exec backend bash

# Seed initial test data
python scripts/init_db.py

# Add realistic entities with varied risk profiles
python scripts/seed_data.py

# Optional: Add comprehensive sample data
python scripts/seed_sample_data.py

# Exit the container
exit
```

---

## Prerequisites

### For Docker Setup (Recommended)
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: Any recent version
- **curl**: For API testing
- **jq**: (Optional) For JSON response parsing

### For Local Development
- **Python**: 3.12+
- **PostgreSQL**: 15+
- **Git**: Any recent version
- **pip**: Latest version
- **virtualenv**: (Optional but recommended)

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB minimum
- **OS**: Linux, macOS, or Windows with WSL2

### Installing Prerequisites

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install docker docker-compose python@3.12 postgresql jq
```

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install other dependencies
sudo apt install -y docker-compose python3.12 python3-pip postgresql-client jq git
```

#### Windows
1. Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. Install [Python 3.12+](https://www.python.org/downloads/)
3. Install [Git for Windows](https://git-scm.com/download/win)
4. (Optional) Install [Windows Subsystem for Linux (WSL2)](https://docs.microsoft.com/en-us/windows/wsl/install)

---

## Docker Setup

### Starting Services

```bash
cd infra
docker-compose up -d
```

This starts:
- **PostgreSQL** (port 5432) - Main database
- **Backend API** (port 8000) - FastAPI application
- **pgAdmin** (port 5050) - Database management UI
- **Redis** (port 6379) - Caching (for future use)

### Automatic Migration on Startup

The backend service automatically runs Alembic migrations on startup via the Docker entrypoint script. This ensures your database schema is always up to date.

The entrypoint script (`backend/scripts/docker-entrypoint.sh`):
1. Waits for PostgreSQL to be ready
2. Runs `alembic upgrade head` to apply all migrations
3. Optionally seeds initial data if `SEED_DATA=true`
4. Starts the Uvicorn server

### Viewing Logs

```bash
# View all service logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View PostgreSQL logs
docker-compose logs -f postgres
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ destroys data)
docker-compose down -v
```

---

## Local Development Setup

For development without Docker:

### 1. Clone Repository

```bash
git clone https://github.com/Adahandles/Chain-Of-Record.git
cd Chain-Of-Record
```

### 2. Set Up Python Environment

```bash
cd backend

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Update the `.env` file with your configuration:

```env
DATABASE_URL=postgresql://chain:chain@localhost:5432/chain
ENVIRONMENT=local
LOG_LEVEL=INFO
SECRET_KEY=change_this_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Start PostgreSQL

#### Using Docker (Recommended)
```bash
docker run -d \
  --name chain-postgres \
  -e POSTGRES_DB=chain \
  -e POSTGRES_USER=chain \
  -e POSTGRES_PASSWORD=chain \
  -p 5432:5432 \
  postgres:15-alpine
```

#### Using Local PostgreSQL
```bash
# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
# or
brew services start postgresql@15  # macOS

# Create database and user
psql -U postgres -c "CREATE DATABASE chain;"
psql -U postgres -c "CREATE USER chain WITH PASSWORD 'chain';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE chain TO chain;"
```

### 5. Run Migrations

```bash
cd backend

# Run Alembic migrations
python -m alembic upgrade head

# Verify tables were created
psql -U chain -d chain -c "\dt"
```

### 6. Start API Server

```bash
# Start with auto-reload (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or start in production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## Database Setup

### Using Alembic Migrations (Recommended)

Alembic manages database schema changes through versioned migration files.

```bash
cd backend

# View current migration status
python -m alembic current

# View migration history
python -m alembic history

# Apply all pending migrations
python -m alembic upgrade head

# Rollback one migration
python -m alembic downgrade -1

# Rollback all migrations
python -m alembic downgrade base
```

### Using Direct SQL (Development Only)

For quick development setup, you can use the SQL file directly:

```bash
# Using psql
psql -U chain -d chain -f infra/postgres/init.sql

# Or using Docker
docker exec -i chain-postgres psql -U chain -d chain < infra/postgres/init.sql
```

⚠️ **Note**: Direct SQL is not recommended for production. Always use Alembic migrations.

### What Gets Created

The initial migration (`001_initial_core_tables`) creates:

**PostgreSQL Extensions:**
- `uuid-ossp` - UUID generation functions
- `pg_trgm` - Trigram matching for fuzzy text search

**Core Tables:**
- `entities` - Legal entities (LLCs, Corps, Trusts, etc.)
- `people` - Individuals (agents, officers, owners)
- `addresses` - Physical locations
- `properties` - Real estate parcels
- `relationships` - Graph connections between entities
- `events` - Time-series events
- `risk_scores` - Risk assessment data
- `users` - Authentication (for future use)

**Indexes:**
- 45+ indexes for optimal query performance
- Composite indexes for common query patterns
- GIN indexes for full-text search (using pg_trgm)

**Views:**
- `active_entities` - Only active entities
- `latest_risk_scores` - Most recent risk score per entity
- `high_risk_entities` - Entities with risk score > 60

---

## Data Seeding

Chain Of Record provides three seeding scripts with different purposes:

### 1. init_db.py - Basic Test Data

Creates minimal test data for development:
- 1 entity, 1 person, 1 address, 1 property, 1 relationship, 1 event, 1 risk score

```bash
cd backend
python scripts/init_db.py
```

**Use case**: Initial setup, testing basic functionality

### 2. seed_data.py - Realistic Test Entities

Adds 3 entities with varied risk profiles:
- **Acme Holdings LLC** - Low risk (Grade A)
- **Summit Real Estate Corp** - Medium risk (Grade B)
- **Riverside Property Mgmt** - High risk (Grade D)

```bash
cd backend
python scripts/seed_data.py
```

**Use case**: Testing risk scoring, demonstrating varied profiles

### 3. seed_sample_data.py - Comprehensive Dataset

Creates rich interconnected data:
- 10 entities with complex relationships
- 12 people (agents, officers, owners)
- 15 addresses with shared locations
- 10 properties with varied characteristics
- 40+ relationships
- 22 events

```bash
cd backend
python scripts/seed_sample_data.py

# Or clear and reseed
python scripts/seed_sample_data.py --clear-all
```

**Use case**: Full system testing, demos, development

### Recommended Workflow

```bash
# 1. Run migrations first
python -m alembic upgrade head

# 2. Seed basic test data
python scripts/init_db.py

# 3. Add realistic entities
python scripts/seed_data.py

# 4. Optional: Add comprehensive data
python scripts/seed_sample_data.py

# 5. Verify data
psql -U chain -d chain -c "SELECT COUNT(*) FROM entities;"
psql -U chain -d chain -c "SELECT COUNT(*) FROM properties;"
```

---

## API Testing

### Using the Test Script

We provide a comprehensive test script that validates all major endpoints:

```bash
cd backend

# Make script executable (if not already)
chmod +x scripts/test_api.sh

# Run all tests
./scripts/test_api.sh

# Run with verbose output
VERBOSE=true ./scripts/test_api.sh

# Test against a different URL
API_URL=http://production.example.com ./scripts/test_api.sh
```

The script tests:
- Health check endpoints
- Entity CRUD operations
- Property search and filtering
- Risk scoring endpoints
- Relationship graph queries
- Error handling (404s, invalid requests)

### Manual API Testing

#### Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "connected"}
```

#### List Entities
```bash
curl http://localhost:8000/api/v1/entities
```

#### Get Specific Entity
```bash
curl http://localhost:8000/api/v1/entities/1
```

#### Search Entities
```bash
# By name
curl "http://localhost:8000/api/v1/entities?name=ACME"

# By type and jurisdiction
curl "http://localhost:8000/api/v1/entities?entity_type=LLC&jurisdiction=FL"
```

#### Property Search
```bash
# List all properties
curl http://localhost:8000/api/v1/properties

# Filter by county
curl "http://localhost:8000/api/v1/properties?county=Travis"

# Filter by acreage
curl "http://localhost:8000/api/v1/properties?min_acres=5"
```

#### Risk Scores
```bash
# Get entity risk score
curl http://localhost:8000/api/v1/scores/entity/1

# List high-risk entities
curl http://localhost:8000/api/v1/scores/high-risk

# Filter by grade
curl "http://localhost:8000/api/v1/scores/high-risk?grade=D"
```

### Using the Interactive API Docs

Visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI. You can:
- Browse all available endpoints
- View request/response schemas
- Execute API calls directly from the browser
- See example responses

---

## Docker Service Management

### Common Commands

```bash
cd infra

# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend

# View service status
docker-compose ps

# View logs
docker-compose logs -f backend

# Access backend shell
docker-compose exec backend bash

# Access PostgreSQL shell
docker-compose exec postgres psql -U chain -d chain

# Run commands in backend
docker-compose exec backend python scripts/init_db.py
```

### Rebuilding Services

```bash
# Rebuild backend after code changes
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build backend

# Rebuild all services
docker-compose build

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Managing Data

```bash
# Create database backup
docker-compose exec postgres pg_dump -U chain chain > backup.sql

# Restore database backup
docker-compose exec -T postgres psql -U chain chain < backup.sql

# Reset database (⚠️ destroys all data)
docker-compose down -v
docker-compose up -d
```

### Accessing pgAdmin

1. Visit http://localhost:5050
2. Login credentials:
   - Email: `admin@chainofrecord.com`
   - Password: `admin123`
3. Add server:
   - Host: `postgres`
   - Port: `5432`
   - Database: `chain`
   - Username: `chain`
   - Password: `chain`

---

## Troubleshooting

### Database Connection Issues

**Problem**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres

# Verify port is not in use
lsof -i :5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows
```

### Migration Errors

**Problem**: `alembic.util.exc.CommandError: Target database is not up to date`

**Solution**:
```bash
# Check current version
python -m alembic current

# View migration history
python -m alembic history

# Stamp database to current version (if migrations already applied manually)
python -m alembic stamp head

# Or rollback and reapply
python -m alembic downgrade base
python -m alembic upgrade head
```

### Backend Won't Start

**Problem**: Backend container exits immediately

**Solution**:
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait longer or increase health check retries
# 2. Missing dependencies - rebuild image
docker-compose build --no-cache backend

# 3. Port already in use
lsof -i :8000  # macOS/Linux
# Kill process using port 8000
```

### Permission Denied Errors

**Problem**: `permission denied` when running scripts

**Solution**:
```bash
# Make scripts executable
chmod +x backend/scripts/*.sh
chmod +x scripts/*.sh

# For Docker volumes on Linux
sudo chown -R $USER:$USER backend/
```

### Port Already in Use

**Problem**: `port is already allocated`

**Solution**:
```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :5050  # pgAdmin

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
# Change "8000:8000" to "8001:8000" for example
```

### Docker Compose Version Issues

**Problem**: `version is obsolete` or syntax errors

**Solution**:
```bash
# Check Docker Compose version
docker-compose version

# Upgrade Docker Compose
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# macOS
brew upgrade docker-compose
```

### Database Schema Out of Sync

**Problem**: Tables or columns are missing

**Solution**:
```bash
# Reset and reapply migrations
cd backend
python -m alembic downgrade base
python -m alembic upgrade head

# Or recreate database
docker-compose down -v
docker-compose up -d
```

---

## Verification Steps

### 1. Verify Database

```bash
# Connect to database
docker-compose exec postgres psql -U chain -d chain

# Check tables
\dt

# Check views
\dv

# Check extensions
\dx

# Count records
SELECT 'entities' as table_name, COUNT(*) FROM entities
UNION ALL
SELECT 'properties', COUNT(*) FROM properties
UNION ALL
SELECT 'risk_scores', COUNT(*) FROM risk_scores;

# Exit psql
\q
```

Expected output: All tables, views, and extensions should exist.

### 2. Verify API

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected"}

# List entities
curl http://localhost:8000/api/v1/entities | jq .
# Expected: JSON array of entities

# API documentation
curl -I http://localhost:8000/docs
# Expected: HTTP 200 OK
```

### 3. Verify Migrations

```bash
cd backend

# Check current migration
python -m alembic current
# Expected: 001 (head)

# View history
python -m alembic history
# Expected: Shows 001_initial_core_tables
```

### 4. Run Test Script

```bash
cd backend
./scripts/test_api.sh
# Expected: All tests pass
```

### 5. Verify Services

```bash
cd infra
docker-compose ps
# Expected: All services "Up" and "healthy"
```

---

## Next Steps

After completing setup:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read Architecture**: See [docs/ARCHITECTURE.md](ARCHITECTURE.md)
3. **Review API Documentation**: See [docs/API.md](API.md)
4. **Set Up Development**: See [docs/DEVELOPMENT.md](DEVELOPMENT.md)
5. **Run ETL Workers**: Load data from real sources
6. **Calculate Risk Scores**: Run the risk scoring engine

---

## Getting Help

- **Documentation**: Check other docs in the `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/Adahandles/Chain-Of-Record/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Adahandles/Chain-Of-Record/discussions)

---

**Happy Building! 🚀**
