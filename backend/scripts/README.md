# Chain Of Record - Database Scripts

This directory contains database management scripts for Chain Of Record.

## Prerequisites

1. **Install Python dependencies:**
   ```bash
   cd /path/to/Chain-Of-Record/backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Ensure your `.env` file contains the database connection string:
   ```bash
   DATABASE_URL=postgresql://chain:chain@localhost:5432/chain
   ```

3. **Initialize database schema:**
   The database must be initialized with the schema before seeding data:
   ```bash
   cd /path/to/Chain-Of-Record/backend
   python -m alembic upgrade head
   ```

## Scripts

### `seed_sample_data.py`

Creates comprehensive sample data to validate the complete data pipeline, including entities, people, addresses, properties, relationships, and events.

#### Usage

**Basic usage:**
```bash
cd /path/to/Chain-Of-Record/backend
python scripts/seed_sample_data.py
```

**Clear existing data and reseed:**
```bash
python scripts/seed_sample_data.py --clear-all
```

**Specify batch size for inserts:**
```bash
python scripts/seed_sample_data.py --batch-size 50
```

#### What It Creates

The seeding script creates a rich, interconnected dataset:

**Entities (10 total)**
- 3 LLCs with different ages:
  - New LLC (< 90 days) - triggers "New Entity Risk"
  - Medium-age LLC (~1 year)
  - Established LLC (> 2 years) - owns multiple properties
- 2 Corporations (Delaware and Texas jurisdictions)
- 1 Trust
- 1 Nonprofit
- 1 Inactive LLC
- 1 Dissolved LLC (triggers "Status Change Risk")
- 1 Additional LLC at shared address

**People (12 total)**
- 4 Registered Agents (one serves 4+ entities - triggers "Shared Agent Risk")
- 4 Officers/Managers
- 4 Property Owners

**Addresses (15 total)**
- 5 Business addresses (3 shared by multiple entities - triggers "Address Concentration Risk")
- 3 Residential addresses
- 7 Property situs addresses

**Properties (10 total)**
- Marion County, FL properties only
- 3 Residential (land use code 0100)
- 2 Agricultural (land use code 0200)
- 2 Commercial (land use code 0400)
- 3 Investment properties (owned by same entity - triggers "High Property Volume Risk")
- Various acreages: 0.25 to 50 acres
- Market values: $185K to $925K
- Some with recent sales (potential "Rapid Turnover Risk")
- Multiple homestead exemptions for single owner (potential "Homestead Fraud Risk")

**Relationships (40+ total)**
- Entity → Agent (registered agent relationships)
- Entity → Officer (corporate officer relationships)
- Entity → Located At → Address (entity addresses)
- Entity → Owns → Property (property ownership)
- Property → Located At → Address (property situs)
- Temporal relationships with start dates
- Confidence scores (0.85 to 1.0)

**Events (22 total)**
- `FORMATION` - All entity formations
- `OFFICER_CHANGE` - Corporate officer changes
- `ADDRESS_CHANGE` - Entity address updates
- `DEED_TRANSFER` - Property sales/transfers
- `ANNUAL_REPORT` - Annual report filings
- `STATUS_CHANGE` - Entity status changes (e.g., dissolution)

#### Risk Scoring Patterns

The sample data is designed to trigger various risk scoring rules:

1. **New Entity Risk**: Rapid Property Holdings LLC (< 90 days old)
2. **High Property Volume**: Triple Crown Properties LLC (owns 4 properties)
3. **Address Concentration**: 3 entities at 123 Main Street
4. **Shared Agent**: Corporate Agents Inc (represents 4+ entities)
5. **Status Change**: Dissolved Ventures LLC (dissolved)
6. **Homestead Fraud**: Triple Crown has multiple properties, some with homestead exemptions
7. **Rapid Turnover**: Recent property purchases and sales

#### Expected Output

```
================================================================================
CHAIN OF RECORD - SAMPLE DATA SEEDING
================================================================================

Creating sample data...
2024-12-14 10:00:00 - __main__ - INFO - Creating people...
2024-12-14 10:00:00 - __main__ - INFO - Created 12 people
2024-12-14 10:00:00 - __main__ - INFO - Creating addresses...
2024-12-14 10:00:00 - __main__ - INFO - Created 15 addresses
2024-12-14 10:00:00 - __main__ - INFO - Creating entities...
2024-12-14 10:00:00 - __main__ - INFO - Created 10 entities
2024-12-14 10:00:00 - __main__ - INFO - Creating properties...
2024-12-14 10:00:00 - __main__ - INFO - Created 10 properties
2024-12-14 10:00:00 - __main__ - INFO - Creating relationships...
2024-12-14 10:00:00 - __main__ - INFO - Created 42 relationships
2024-12-14 10:00:00 - __main__ - INFO - Creating events...
2024-12-14 10:00:00 - __main__ - INFO - Created 22 events

Sample data creation complete!

================================================================================
DATA VERIFICATION
================================================================================

Record Counts:
  Entities: 10
  People: 12
  Addresses: 15
  Properties: 10
  Relationships: 42
  Events: 22
  Risk Scores: 0

High-Risk Patterns Identified:
  New Entities (< 90 days): 1
    - Rapid Property Holdings LLC (formed 2024-10-30)
  High Property Volume (3+ properties): 1
    - Triple Crown Properties LLC: 4 properties
  Address Concentration (3+ entities): 1
    - 123 Main Street, Ocala: 3 entities
  Shared Agents (4+ entities): 1
    - Corporate Agents Inc: 4 entities

================================================================================
VERIFICATION COMPLETE
================================================================================

✅ SUCCESS: Sample data seeded successfully

Next steps:
  1. Run risk scoring: python -m app.domain.scoring.score_all
  2. Query the API: curl http://localhost:8000/api/v1/entities
  3. Explore the data in your PostgreSQL client
```

#### Features

- **Idempotent**: Can be run multiple times. Use `--clear-all` to reset data.
- **Transaction Safety**: All operations are wrapped in transactions with proper rollback on error.
- **Detailed Logging**: Progress updates and statistics throughout execution.
- **Verification Queries**: Automatic validation of created data and risk patterns.

## Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not translate host name "db" to address
```

**Solution**: Ensure PostgreSQL is running and the `DATABASE_URL` in your `.env` file is correct.

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Or if running locally
pg_isready -h localhost -p 5432
```

### Schema Not Initialized

```
sqlalchemy.exc.ProgrammingError: relation "entities" does not exist
```

**Solution**: Run the Alembic migrations first:

```bash
cd /path/to/Chain-Of-Record/backend
python -m alembic upgrade head
```

### Permission Denied

```
psycopg2.errors.InsufficientPrivilege: permission denied for table entities
```

**Solution**: Ensure your database user has proper permissions:

```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chain;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chain;
```

### Foreign Key Violations

If you see foreign key constraint errors, ensure you're using the `--clear-all` flag to properly reset the database:

```bash
python scripts/seed_sample_data.py --clear-all
```

## Data Model Overview

The Chain Of Record data model consists of several interconnected domains:

### Core Entities Domain
- **entities**: Legal entities (LLCs, Corps, Trusts, Nonprofits)
- **people**: Individuals (agents, officers, owners)
- **addresses**: Physical locations

### Properties Domain
- **properties**: Real estate parcels with county appraiser data

### Graph Domain
- **relationships**: Connections between entities, people, and properties
- **events**: Time-series events (formations, filings, transfers)
- **risk_scores**: Risk assessment scores for entities

### Relationship Types

Common relationship types in the system:

- `agent_for`: Person acts as registered agent for entity
- `officer`: Person is officer/manager of entity
- `located_at`: Entity or property is located at address
- `owns`: Entity owns property
- `grants_to`: Trust grants to beneficiary

### Event Types

Common event types in the system:

- `FORMATION`: Entity formation/creation
- `OFFICER_CHANGE`: Corporate officer appointment/removal
- `ADDRESS_CHANGE`: Entity address update
- `DEED_TRANSFER`: Property sale/transfer
- `ANNUAL_REPORT`: Annual report filing
- `STATUS_CHANGE`: Entity status change (active, dissolved, etc.)

## Next Steps

After seeding the database:

1. **Run Risk Scoring**: Calculate risk scores for all entities
   ```bash
   python -m app.domain.scoring.score_all
   ```

2. **Start the API Server**: Launch the FastAPI application
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Explore the Data**: Use your PostgreSQL client or API endpoints to query the data
   ```bash
   # List all entities
   curl http://localhost:8000/api/v1/entities
   
   # Get specific entity with relationships
   curl http://localhost:8000/api/v1/entities/1
   
   # View high-risk entities
   curl http://localhost:8000/api/v1/entities?risk_grade=D,F
   ```

4. **Run Tests**: Validate the data pipeline
   ```bash
   pytest tests/
   ```

## Additional Resources

- **Database Models**: `backend/app/domain/*/models.py`
- **Alembic Migrations**: `backend/alembic/versions/`
- **API Documentation**: Start the server and visit http://localhost:8000/docs
- **Configuration**: `backend/app/core/config.py`
