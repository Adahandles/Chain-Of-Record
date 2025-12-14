# Chain Of Record - Root Scripts

This directory contains root-level automation scripts for Chain Of Record.

## Available Scripts

### quickstart.sh

One-command setup script for getting the entire system up and running.

**Purpose**: Automates the complete setup process including:
- Prerequisites checking (Docker, Docker Compose, curl)
- Starting all services via Docker Compose
- Waiting for services to be healthy
- Verifying database schema
- Optional data seeding
- Opening API documentation in browser

**Usage**:
```bash
# From repository root
./scripts/quickstart.sh

# Or from any directory
/path/to/Chain-Of-Record/scripts/quickstart.sh
```

**What it does**:
1. ✅ Checks for required tools (Docker, curl)
2. 🐳 Starts Docker Compose services
3. ⏳ Waits for PostgreSQL and Backend to be healthy
4. 🗄️ Verifies database schema was created
5. 📊 Optionally seeds test data (user choice)
6. 🌐 Displays service URLs and credentials
7. 🧪 Tests API health endpoint
8. 📖 Opens API docs in browser (optional)

**Interactive Prompts**:
- Stop existing services? (y/N)
- Seed database? (1-4):
  - 1: No seeding (empty database)
  - 2: Basic test data (1 entity)
  - 3: Realistic entities (3 entities with varied risk)
  - 4: Comprehensive dataset (10 entities, full demo)
- Open API docs in browser? (y/N)

**Environment Variables**:
- `MAX_WAIT`: Maximum seconds to wait for services (default: 120)

**Example Output**:
```
==================================================================
CHAIN OF RECORD - QUICK START
==================================================================
Repository: /path/to/Chain-Of-Record
Time: Sat Dec 14 10:00:00 UTC 2024

==> Checking prerequisites...

✓ Docker installed: Docker version 24.0.0, build 1234567
✓ Docker Compose installed: Docker Compose version v2.20.0
✓ Python installed: Python 3.12.0
✓ Git installed: git version 2.40.0
✓ curl installed

==> Starting Docker Compose services...
✓ Docker Compose started

==> Waiting for services to be healthy...

✓ PostgreSQL is ready
✓ Backend API is ready

==> Verifying database schema...
✓ Database schema created (9 tables)

==================================================================
✓ SETUP COMPLETE
==================================================================

Services are running:

  API Server:          http://localhost:8000
  API Documentation:   http://localhost:8000/docs
  OpenAPI Schema:      http://localhost:8000/openapi.json
  pgAdmin:             http://localhost:5050
  PostgreSQL:          localhost:5432
```

**Troubleshooting**:
- If services don't start, check Docker is running: `docker ps`
- If services timeout, check logs: `cd infra && docker-compose logs`
- If ports are in use, stop conflicting services or change ports in `infra/docker-compose.yml`

---

## Backend Scripts

For backend-specific scripts (database seeding, migrations, testing), see:
- `backend/scripts/` directory
- `backend/scripts/README.md`

## Documentation

For detailed setup and development guides, see:
- `docs/SETUP_GUIDE.md` - Complete setup instructions
- `docs/DEVELOPMENT.md` - Development workflow and best practices
- `docs/ARCHITECTURE.md` - System architecture overview
- `docs/API.md` - API documentation

---

**Note**: All scripts are designed to be idempotent (safe to run multiple times).
