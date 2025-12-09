# Chain Of Record - Architecture Documentation

## Overview

Chain Of Record is an entity, property, and risk intelligence platform designed to track relationships between businesses, properties, and individuals through public record analysis.

## Architecture Principles

### 1. Domain-Driven Design
- **Entities**: Core business entities (LLCs, corporations, trusts)
- **Properties**: Real estate parcels and ownership records
- **Relationships**: Graph connections between entities, people, and properties
- **Events**: Time-series data for entity changes and filings
- **Scoring**: Risk assessment and fraud detection

### 2. Separation of Concerns
```
├── Core (config, db, logging, security)
├── Domain (business logic, models, repositories)
├── API (FastAPI endpoints, schemas)
├── Ingest (ETL pipelines for data sources)
└── Workers (background processing)
```

### 3. Data Architecture

#### Core Tables
- `entities`: Business entities from state registries
- `people`: Individuals (agents, officers, owners)
- `addresses`: Standardized location data
- `properties`: Real estate parcels from county appraisers
- `relationships`: Graph edges connecting all entities
- `events`: Time-series events and changes
- `risk_scores`: Calculated risk assessments

#### Indexing Strategy
- **Search Performance**: GIN indexes for text search
- **Graph Traversal**: Composite indexes on relationship table
- **Time-Series**: Date-based partitioning for events
- **Deduplication**: Hash-based indexes for addresses

### 4. ETL Pipeline Design

#### Abstract Base Classes
```python
class IngestSource(ABC):
    def fetch_batch() -> Iterable[RawRecord]
    def normalize(raw) -> List[NormalizedRecord]  
    def persist(normalized, db) -> int
```

#### Data Sources
- **Sunbiz**: Florida Division of Corporations
- **Marion County PA**: Property Appraiser records
- **Extensible**: Framework supports additional sources

#### Processing Flow
1. **Fetch**: Raw data from external sources
2. **Normalize**: Standardize into common schema
3. **Persist**: Upsert with relationship creation
4. **Score**: Calculate risk assessments

### 5. Scoring Engine

#### Rule-Based System
```python
@dataclass
class ScoringRule:
    name: str
    weight: int
    category: str
    fn: Callable[[ScoringContext], bool]
```

#### Built-in Rules
- **Entity Age**: New entities (< 90 days) score higher risk
- **Property Volume**: High property ownership flags
- **Address Concentration**: Multiple entities at same address
- **Agent Patterns**: Agents representing many entities
- **Status Changes**: Inactive/dissolved entities

#### Scoring Context
- Entity metadata and formation details
- Property ownership counts and values
- Relationship graph analysis
- Time-series event patterns

### 6. API Design

#### Versioned REST API
- `/api/v1/entities` - Entity CRUD and search
- `/api/v1/properties` - Property data and ownership
- `/api/v1/scores` - Risk scoring and analysis
- `/api/v1/health` - System health and statistics

#### Response Patterns
- Pydantic schemas for type safety
- Consistent error handling
- Request tracing with unique IDs
- Pagination for large result sets

### 7. Graph Database Abstraction

#### Relationship Modeling
```sql
relationships(
    from_type, from_id,  -- Source node
    to_type, to_id,      -- Target node
    rel_type,            -- Relationship type
    confidence,          -- 0.0-1.0 confidence
    start_date, end_date -- Temporal validity
)
```

#### Graph Queries
- Entity ownership chains
- Connected entity discovery
- Agent representation networks
- Address concentration analysis

## Technology Stack

### Backend
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with advanced indexing
- **ORM**: SQLAlchemy 2.0 with declarative models
- **Migrations**: Alembic for schema evolution
- **Validation**: Pydantic for type safety

### Infrastructure
- **Containers**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for development
- **Database**: PostgreSQL 15 with extensions
- **Caching**: Redis for future performance optimization

### Development
- **CI/CD**: GitHub Actions with automated testing
- **Code Quality**: Black, flake8, mypy for code standards
- **Documentation**: OpenAPI/Swagger auto-generation
- **Logging**: Structured logging with request tracing

## Deployment Architecture

### Development Environment
```
├── PostgreSQL (local container)
├── Backend API (hot reload)
├── ETL Workers (manual/scheduled)
└── pgAdmin (database management)
```

### Production Environment (Future)
```
├── Load Balancer (nginx/ALB)
├── API Servers (multiple instances)
├── Background Workers (Celery/RQ)
├── Database Cluster (read replicas)
├── Redis Cluster (caching/sessions)
└── Monitoring (Prometheus/Grafana)
```

## Security Considerations

### Data Protection
- No PII storage beyond public records
- SQL injection prevention via ORM
- Input validation at API boundaries
- Structured logging without sensitive data

### Access Control (Future)
- JWT-based authentication
- Role-based permissions
- API rate limiting
- Request/response logging

### Compliance
- Public data only (no GDPR concerns)
- Audit trail for all data changes
- Data retention policies
- Source attribution tracking

## Scalability Design

### Database Optimization
- Query optimization with EXPLAIN plans
- Partitioning for time-series data
- Read replicas for analytical queries
- Connection pooling and prepared statements

### Application Scaling
- Stateless API design for horizontal scaling
- Background worker separation
- Caching strategies for expensive operations
- Async I/O for concurrent processing

### Data Volume Planning
- Estimated 1M+ entities in Florida
- 500K+ properties in target counties
- 10M+ relationships and events
- Daily incremental updates

## Monitoring and Observability

### Health Checks
- Database connectivity
- External API availability
- Worker process status
- Disk and memory usage

### Metrics Collection
- Request latency and throughput
- Database query performance
- ETL processing statistics
- Error rates and patterns

### Alerting
- System health degradation
- ETL pipeline failures
- Unusual scoring patterns
- Security event detection