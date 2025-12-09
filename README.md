# Chain Of Record

**Entity, Property, and Risk Intelligence Platform**

Chain Of Record is a comprehensive platform for analyzing relationships between business entities, properties, and individuals through public record data. Built for transparency, investigation, and risk assessment.

## 🎯 Features

### Core Capabilities
- **Entity Tracking**: Business registrations from state databases (starting with Florida Sunbiz)
- **Property Intelligence**: County property appraiser records with ownership tracking
- **Relationship Mapping**: Graph-based connections between entities, people, and properties
- **Risk Scoring**: Automated fraud detection and risk assessment
- **Time-Series Analysis**: Event tracking for entity changes and filings

### Data Sources
- ✅ **Florida Sunbiz**: Division of Corporations business registry
- ✅ **Marion County, FL**: Property Appraiser records
- 🚧 **Expanding**: Additional counties and state registries

### API Features
- RESTful API with OpenAPI/Swagger documentation
- Advanced search and filtering
- Graph traversal queries
- Batch processing capabilities
- Real-time risk scoring

## 🏗️ Architecture

```
Chain-Of-Record/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── core/     # Configuration, DB, logging
│   │   ├── domain/   # Business logic (entities, properties, scoring)
│   │   ├── api/      # REST endpoints
│   │   ├── schemas/  # Pydantic models
│   │   └── ingest/   # ETL data sources
│   └── alembic/      # Database migrations
├── workers/          # Background ETL processes
├── infra/           # Docker Compose, database setup
├── docs/            # Architecture and API documentation
└── .github/         # CI/CD workflows
```

### Technology Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **ETL**: Custom pluggable ingestion framework
- **Infrastructure**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Documentation**: OpenAPI/Swagger

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ (for local development)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Adahandles/Chain-Of-Record.git
cd Chain-Of-Record
```

### 2. Start with Docker Compose
```bash
cd infra
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- Backend API (port 8000)
- pgAdmin UI (port 5050)

### 3. Verify Installation
```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

### 4. Run Initial Data Load
```bash
# Load sample data from Sunbiz and Marion County
docker-compose exec backend python /app/workers/etl_worker/main.py full
```

### 5. Explore the Data
```bash
# Get system statistics
curl http://localhost:8000/api/v1/stats

# Search entities
curl "http://localhost:8000/api/v1/entities/?name=SUNRISE"

# Get risk scores
curl http://localhost:8000/api/v1/scores/high-risk
```

## 📊 Usage Examples

### Entity Search
```bash
# Search by name
curl "http://localhost:8000/api/v1/entities/?name=PROPERTIES&limit=10"

# Filter by jurisdiction and type
curl "http://localhost:8000/api/v1/entities/?jurisdiction=FL&entity_type=llc"
```

### Property Analysis
```bash
# Search properties in Marion County
curl "http://localhost:8000/api/v1/properties/?county=Marion&min_acres=5"

# Get property ownership details
curl http://localhost:8000/api/v1/properties/123/owners
```

### Risk Assessment
```bash
# Score a specific entity
curl http://localhost:8000/api/v1/scores/entity/123

# Get high-risk entities
curl "http://localhost:8000/api/v1/scores/high-risk?grade=D&limit=20"

# Batch score multiple entities
curl -X POST http://localhost:8000/api/v1/scores/batch \
  -H "Content-Type: application/json" \
  -d '{"entity_ids": [123, 456, 789]}'
```

### Graph Relationships
```bash
# Get entity relationship graph
curl "http://localhost:8000/api/v1/entities/123/graph?max_depth=2"

# Get direct relationships
curl http://localhost:8000/api/v1/entities/123/relationships
```

## 🔧 Development Setup

### Local Development
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Database setup (requires PostgreSQL)
export DATABASE_URL="postgresql://chain:chain@localhost:5432/chain"
alembic upgrade head

# Start API server
uvicorn app.main:app --reload

# Run ETL workers
cd ../workers
python etl_worker/main.py sunbiz
```

### Running Tests
```bash
cd backend
pytest -v --cov=app
```

### Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 📖 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)**: System design and technical details
- **[API Documentation](docs/API.md)**: Complete API reference
- **[Data Sources](docs/DATA_SOURCES.md)**: Information about data sources
- **Interactive API Docs**: Available at `/docs` when running locally

## 🛡️ Risk Scoring

The platform includes a sophisticated risk scoring engine that evaluates entities based on:

### Scoring Categories
- **Entity Characteristics**: Age, status, formation patterns
- **Property Holdings**: Volume, concentration, value patterns  
- **Relationship Analysis**: Agent patterns, address clustering
- **Temporal Patterns**: Formation timing, event sequences

### Risk Factors
- New entities (< 90 days): Higher risk weighting
- High property ownership concentration
- Shared registered agents across many entities
- Address clustering (multiple entities at same location)
- Inactive or dissolved status with active operations

### Output
- Numeric risk score (0-100+)
- Letter grade (A through F)
- Detailed flags explaining score components
- Historical score tracking

## 🔗 Data Integration

### Current Sources
- **Sunbiz (FL)**: 1.5M+ business entities, updated continuously
- **Marion County PA**: 250K+ property records with ownership data

### ETL Framework
- Pluggable architecture for adding new data sources
- Automatic deduplication and normalization
- Relationship inference and validation
- Incremental update support

### Data Quality
- Source attribution for all records
- Confidence scoring for inferred relationships
- Data validation and error handling
- Audit trails for all changes

## 🚦 Production Deployment

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db
ENVIRONMENT=production

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
SUNBIZ_API_KEY=your-api-key
```

### Scaling Considerations
- Database read replicas for analytical queries
- Background worker scaling with Celery/RQ
- API server horizontal scaling
- Redis caching for expensive operations

## 🤝 Contributing

### Development Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with tests
4. Run quality checks (`black`, `flake8`, `pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Include docstrings for public APIs
- Use type hints throughout

### Adding Data Sources
1. Implement `IngestSource` abstract base class
2. Add normalization logic for source data
3. Include validation and error handling
4. Write integration tests
5. Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Adahandles/Chain-Of-Record/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Adahandles/Chain-Of-Record/discussions)
- **Email**: support@chainofrecord.com

## 🔮 Roadmap

### Version 1.1 (Q1 2024)
- [ ] Additional Florida counties (Orange, Broward, Miami-Dade)
- [ ] Enhanced search with fuzzy matching
- [ ] Export capabilities (CSV, JSON)
- [ ] Basic authentication system

### Version 1.2 (Q2 2024)
- [ ] Delaware Division of Corporations
- [ ] Advanced graph visualization
- [ ] API rate limiting and quotas
- [ ] Webhook notifications

### Version 2.0 (2024)
- [ ] Machine learning risk models
- [ ] Real-time data streaming
- [ ] Multi-tenant architecture
- [ ] Advanced analytics dashboard

## 🏆 Acknowledgments

- Florida Division of Corporations for public data access
- County Property Appraisers for transparency
- Open source community for foundational tools
- Contributors and early adopters

---

**Chain Of Record** - Bringing transparency to entity relationships through public data.

*Built with ❤️ for transparency and accountability.*