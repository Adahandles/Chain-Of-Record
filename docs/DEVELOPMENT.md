# Chain Of Record - Development Guide

Guide for developers contributing to Chain Of Record.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Code Quality Tools](#code-quality-tools)
3. [Testing](#testing)
4. [Database Migrations](#database-migrations)
5. [Adding Data Sources](#adding-data-sources)
6. [Debugging](#debugging)
7. [Git Workflow](#git-workflow)
8. [Code Style Guidelines](#code-style-guidelines)
9. [Performance Optimization](#performance-optimization)

---

## Development Environment Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Git
- Docker (optional, for testing)
- IDE with Python support (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/Adahandles/Chain-Of-Record.git
cd Chain-Of-Record

# Create virtual environment
cd backend
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
# or .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black flake8 mypy pytest pytest-cov pytest-asyncio

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. Open project
2. Set interpreter: File → Settings → Project → Python Interpreter
3. Enable formatters: Settings → Tools → Black
4. Enable linters: Settings → Tools → External Tools

---

## Code Quality Tools

### Black - Code Formatter

Black is the opinionated code formatter used for consistent style.

```bash
# Format all Python files
black app/

# Format specific files
black app/domain/entities/models.py

# Check without modifying
black --check app/

# Format with line length (default is 88)
black --line-length 100 app/
```

**Configuration** (in `pyproject.toml`):

```toml
[tool.black]
line-length = 88
target-version = ['py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### Flake8 - Linter

Flake8 checks for style issues and potential errors.

```bash
# Lint all code
flake8 app/

# Lint specific files
flake8 app/domain/entities/models.py

# Show statistics
flake8 --statistics app/
```

**Configuration** (in `.flake8`):

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, E501, W503
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    alembic
per-file-ignores =
    __init__.py:F401
```

### Mypy - Type Checker

Mypy performs static type checking using type hints.

```bash
# Check all code
mypy app/

# Check specific module
mypy app/domain/entities/

# Strict mode
mypy --strict app/domain/entities/models.py
```

**Configuration** (in `mypy.ini`):

```ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
strict_equality = True

[mypy-alembic.*]
ignore_missing_imports = True

[mypy-sqlalchemy.*]
ignore_missing_imports = True
```

### Running All Quality Checks

```bash
# Create a script: scripts/check_quality.sh
#!/bin/bash
set -e

echo "Running Black..."
black --check app/

echo "Running Flake8..."
flake8 app/

echo "Running Mypy..."
mypy app/

echo "✓ All quality checks passed!"
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_entities.py

# Run specific test
pytest tests/test_entities.py::test_create_entity

# Run with verbose output
pytest -v

# Run with print statements
pytest -s

# Stop on first failure
pytest -x

# Run tests matching pattern
pytest -k "entity"
```

### Writing Tests

#### Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures
│   ├── test_entities.py      # Entity tests
│   ├── test_properties.py    # Property tests
│   ├── test_scoring.py       # Risk scoring tests
│   └── api/
│       ├── __init__.py
│       ├── test_entity_api.py
│       └── test_property_api.py
```

#### Example Test

```python
# tests/test_entities.py
import pytest
from sqlalchemy.orm import Session
from app.domain.entities.models import Entity
from app.domain.entities.service import EntityService


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Setup test database
    engine = create_engine("postgresql://test:test@localhost/test_chain")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Teardown
    session.close()
    Base.metadata.drop_all(engine)


def test_create_entity(db_session: Session):
    """Test creating an entity."""
    service = EntityService(db_session)
    
    entity_data = {
        "external_id": "TEST123",
        "source_system": "test",
        "type": "LLC",
        "legal_name": "Test Company LLC",
        "jurisdiction": "FL",
        "status": "ACTIVE"
    }
    
    entity = service.create_entity(entity_data)
    
    assert entity.id is not None
    assert entity.legal_name == "Test Company LLC"
    assert entity.type == "LLC"


def test_search_entities_by_name(db_session: Session):
    """Test searching entities by name."""
    service = EntityService(db_session)
    
    # Create test entities
    service.create_entity({
        "source_system": "test",
        "type": "LLC",
        "legal_name": "Acme Holdings LLC",
        "jurisdiction": "FL"
    })
    
    # Search
    results = service.search_by_name("Acme")
    
    assert len(results) == 1
    assert "Acme" in results[0].legal_name
```

#### Testing API Endpoints

```python
# tests/api/test_entity_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_entities():
    """Test GET /api/v1/entities endpoint."""
    response = client.get("/api/v1/entities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_entity():
    """Test GET /api/v1/entities/{id} endpoint."""
    response = client.get("/api/v1/entities/1")
    assert response.status_code in [200, 404]


def test_search_entities():
    """Test entity search with query parameters."""
    response = client.get("/api/v1/entities?name=Test&jurisdiction=FL")
    assert response.status_code == 200
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

Aim for:
- **Overall**: 80%+ coverage
- **Critical paths**: 95%+ coverage (risk scoring, data ingestion)
- **API endpoints**: 100% coverage

---

## Database Migrations

### Creating New Migrations

```bash
cd backend

# Auto-generate migration from model changes
python -m alembic revision --autogenerate -m "add column to entities"

# Create empty migration for manual changes
python -m alembic revision -m "add custom indexes"
```

### Migration Structure

```python
# alembic/versions/YYYYMMDDHHMMSS_description.py
"""description

Revision ID: abc123
Revises: xyz789
Create Date: 2024-12-14 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123'
down_revision: Union[str, None] = 'xyz789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add your upgrade operations here
    op.add_column('entities', sa.Column('new_field', sa.String(), nullable=True))
    op.create_index('idx_entities_new_field', 'entities', ['new_field'])


def downgrade() -> None:
    # Add your downgrade operations here (reverse of upgrade)
    op.drop_index('idx_entities_new_field', table_name='entities')
    op.drop_column('entities', 'new_field')
```

### Best Practices

1. **Always test migrations**
   ```bash
   # Apply migration
   python -m alembic upgrade head
   
   # Test rollback
   python -m alembic downgrade -1
   
   # Reapply
   python -m alembic upgrade head
   ```

2. **Keep migrations small and focused**
   - One logical change per migration
   - Easier to review and rollback

3. **Write reversible migrations**
   - Always implement `downgrade()`
   - Test rollback functionality

4. **Add indexes for new columns**
   - Consider query patterns
   - Add composite indexes for common queries

5. **Handle data migrations carefully**
   ```python
   # Good: Update existing data
   op.execute("UPDATE entities SET new_field = 'default' WHERE new_field IS NULL")
   
   # Bad: Don't lose data
   # op.drop_column('entities', 'important_field')  # Without backup!
   ```

### Testing Migrations

```bash
# Test upgrade/downgrade cycle
python -m alembic upgrade head
python -m alembic downgrade base
python -m alembic upgrade head

# Test with fresh database
docker run --rm -e POSTGRES_PASSWORD=test -p 5433:5432 postgres:15-alpine
DATABASE_URL=postgresql://postgres:test@localhost:5433/postgres python -m alembic upgrade head
```

---

## Adding Data Sources

Chain Of Record uses a pluggable architecture for data ingestion.

### 1. Create Ingest Source

```python
# app/ingest/my_source.py
from app.ingest.base import IngestSource
from typing import List, Dict, Any
import httpx


class MySourceIngestor(IngestSource):
    """
    Ingest data from My Data Source.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.mydatasource.com"
    
    def fetch_entities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch entities from My Data Source API.
        """
        response = httpx.get(
            f"{self.base_url}/entities",
            params={"limit": limit},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()["entities"]
    
    def normalize_entity(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform source data into standard entity format.
        """
        return {
            "external_id": raw_data["id"],
            "source_system": "my_source",
            "type": self._map_entity_type(raw_data["entity_type"]),
            "legal_name": raw_data["name"],
            "jurisdiction": raw_data["state"],
            "status": raw_data["status"],
            "formation_date": raw_data["formed_date"],
        }
    
    def _map_entity_type(self, source_type: str) -> str:
        """Map source entity type to standard type."""
        mapping = {
            "LIMITED_LIABILITY_COMPANY": "LLC",
            "CORPORATION": "CORP",
            "PARTNERSHIP": "PARTNERSHIP",
        }
        return mapping.get(source_type, "UNKNOWN")
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate normalized data before inserting.
        """
        required_fields = ["external_id", "source_system", "type", "legal_name"]
        return all(field in data for field in required_fields)
```

### 2. Register Source

```python
# app/ingest/__init__.py
from app.ingest.sunbiz import SunbizIngestor
from app.ingest.property_appraiser_fl_marion import MarionPropertyAppraiserIngestor
from app.ingest.my_source import MySourceIngestor

INGEST_SOURCES = {
    "sunbiz": SunbizIngestor,
    "marion_pa": MarionPropertyAppraiserIngestor,
    "my_source": MySourceIngestor,
}
```

### 3. Add Configuration

```python
# app/core/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # My Data Source settings
    my_source_api_key: str = ""
    my_source_enabled: bool = False
```

### 4. Create ETL Worker

```python
# workers/etl_worker/my_source_worker.py
import logging
from app.core.db import SessionLocal
from app.ingest import INGEST_SOURCES
from app.domain.entities.service import EntityService

logger = logging.getLogger(__name__)


def run_my_source_etl():
    """
    Run ETL process for My Data Source.
    """
    logger.info("Starting My Source ETL")
    
    # Initialize
    ingestor = INGEST_SOURCES["my_source"](api_key="...")
    db = SessionLocal()
    service = EntityService(db)
    
    try:
        # Fetch data
        raw_entities = ingestor.fetch_entities(limit=1000)
        logger.info(f"Fetched {len(raw_entities)} entities")
        
        # Process each entity
        created = 0
        updated = 0
        errors = 0
        
        for raw_entity in raw_entities:
            try:
                # Normalize
                normalized = ingestor.normalize_entity(raw_entity)
                
                # Validate
                if not ingestor.validate_data(normalized):
                    logger.warning(f"Invalid data: {normalized}")
                    errors += 1
                    continue
                
                # Upsert
                existing = service.get_by_external_id(
                    normalized["external_id"],
                    normalized["source_system"]
                )
                
                if existing:
                    service.update_entity(existing.id, normalized)
                    updated += 1
                else:
                    service.create_entity(normalized)
                    created += 1
                    
            except Exception as e:
                logger.error(f"Error processing entity: {e}")
                errors += 1
        
        db.commit()
        logger.info(f"ETL complete: {created} created, {updated} updated, {errors} errors")
        
    except Exception as e:
        logger.error(f"ETL failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_my_source_etl()
```

### 5. Add Tests

```python
# tests/ingest/test_my_source.py
import pytest
from app.ingest.my_source import MySourceIngestor


def test_normalize_entity():
    """Test entity normalization."""
    ingestor = MySourceIngestor(api_key="test")
    
    raw_data = {
        "id": "ABC123",
        "entity_type": "LIMITED_LIABILITY_COMPANY",
        "name": "Test Company LLC",
        "state": "FL",
        "status": "ACTIVE",
        "formed_date": "2020-01-15"
    }
    
    normalized = ingestor.normalize_entity(raw_data)
    
    assert normalized["external_id"] == "ABC123"
    assert normalized["type"] == "LLC"
    assert normalized["legal_name"] == "Test Company LLC"
```

---

## Debugging

### Local Debugging

#### Using Python Debugger (pdb)

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

#### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

### Database Debugging

```bash
# Connect to database
psql -U chain -d chain

# View query execution plan
EXPLAIN ANALYZE SELECT * FROM entities WHERE legal_name LIKE '%TEST%';

# Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

# Check table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### API Debugging

```bash
# Enable debug logging
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Test with curl
curl -v http://localhost:8000/api/v1/entities

# View request/response details
curl -v -H "Content-Type: application/json" \
  -d '{"name": "Test"}' \
  http://localhost:8000/api/v1/entities
```

### Docker Debugging

```bash
# View container logs
docker-compose logs -f backend

# Access running container
docker-compose exec backend bash

# Check environment variables
docker-compose exec backend env

# Run Python in container
docker-compose exec backend python

# Check file permissions
docker-compose exec backend ls -la /app
```

---

## Git Workflow

### Branch Strategy

```bash
# Main branches
main          # Production-ready code
develop       # Integration branch

# Feature branches
feature/add-user-auth
feature/improve-risk-scoring

# Bug fix branches
fix/entity-search-bug
fix/migration-error

# Hotfix branches
hotfix/security-patch
```

### Workflow

```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# 2. Make changes
# ... edit files ...
git add .
git commit -m "Add my feature"

# 3. Keep up to date
git fetch origin
git rebase origin/develop

# 4. Push and create PR
git push origin feature/my-feature
# Create Pull Request on GitHub

# 5. After review and approval
# PR is merged to develop

# 6. Delete feature branch
git branch -d feature/my-feature
```

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

```bash
feat(entities): add full-text search capability

Implement PostgreSQL full-text search using pg_trgm extension
for fuzzy matching on entity names.

Closes #123
```

```bash
fix(scoring): correct risk score calculation

Fixed bug where inactive entities were included in
high-risk calculations.

Fixes #456
```

---

## Code Style Guidelines

### Python Style

Follow PEP 8 with Black formatting:

- Line length: 88 characters
- Use type hints for all functions
- Docstrings for all public APIs
- Use f-strings for formatting

### Naming Conventions

```python
# Classes: PascalCase
class EntityService:
    pass

# Functions/methods: snake_case
def get_entity_by_id(entity_id: int) -> Entity:
    pass

# Variables: snake_case
entity_count = 10
risk_threshold = 60.0

# Constants: UPPER_SNAKE_CASE
MAX_BATCH_SIZE = 1000
DEFAULT_RISK_GRADE = "C"

# Private methods: _leading_underscore
def _calculate_internal_score(self) -> float:
    pass
```

### Documentation

```python
def calculate_risk_score(
    entity_id: int,
    include_property_risk: bool = True
) -> RiskScore:
    """
    Calculate risk score for an entity.
    
    Args:
        entity_id: ID of the entity to score
        include_property_risk: Whether to include property-based risk factors
        
    Returns:
        RiskScore object with score, grade, and flags
        
    Raises:
        EntityNotFoundError: If entity does not exist
        ScoringError: If calculation fails
        
    Example:
        >>> score = calculate_risk_score(123)
        >>> print(f"Grade: {score.grade}, Score: {score.score}")
        Grade: B, Score: 42.5
    """
    pass
```

---

## Performance Optimization

### Database Optimization

1. **Use indexes effectively**
   ```python
   # Good: Query uses index
   entities = db.query(Entity).filter(Entity.external_id == "ABC123").all()
   
   # Bad: Query scans full table
   entities = db.query(Entity).filter(Entity.legal_name.like("%test%")).all()
   
   # Better: Use GIN index with pg_trgm
   entities = db.query(Entity).filter(
       Entity.legal_name.op("%%")("test")
   ).all()
   ```

2. **Batch operations**
   ```python
   # Bad: N+1 queries
   for entity_id in entity_ids:
       entity = db.query(Entity).get(entity_id)
       process(entity)
   
   # Good: Single query
   entities = db.query(Entity).filter(Entity.id.in_(entity_ids)).all()
   for entity in entities:
       process(entity)
   ```

3. **Use connection pooling**
   ```python
   # In app/core/db.py
   engine = create_engine(
       settings.database_url,
       poolclass=pool.QueuePool,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True
   )
   ```

### API Optimization

1. **Add caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_entity_risk_score(entity_id: int) -> RiskScore:
       # Expensive calculation
       return calculate_risk_score(entity_id)
   ```

2. **Use pagination**
   ```python
   @router.get("/entities")
   def list_entities(
       skip: int = 0,
       limit: int = 100,
       db: Session = Depends(get_db)
   ):
       entities = db.query(Entity).offset(skip).limit(limit).all()
       return entities
   ```

3. **Optimize serialization**
   ```python
   # Use orjson for faster JSON serialization
   from fastapi.responses import ORJSONResponse
   
   @router.get("/entities", response_class=ORJSONResponse)
   def list_entities():
       pass
   ```

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

**Happy Coding! 🚀**
