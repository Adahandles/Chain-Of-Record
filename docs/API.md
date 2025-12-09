# Chain Of Record API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.chainofrecord.com` (future)

## Authentication
Currently open for development. Future versions will require API keys or JWT tokens.

## API Versioning
All endpoints are prefixed with `/api/v1/` for version 1 of the API.

## Common Response Patterns

### Success Response
```json
{
  "id": 123,
  "field": "value",
  "timestamp": "2023-12-07T10:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "request_id": "uuid-string"
}
```

### Pagination (Future)
```json
{
  "items": [...],
  "total": 1000,
  "page": 1,
  "per_page": 50,
  "has_next": true
}
```

## Endpoints

### Health Check

#### GET `/health`
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-07T10:00:00Z",
  "environment": "development",
  "version": "1.0.0"
}
```

#### GET `/health/detailed`
Detailed health check with database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-07T10:00:00Z",
  "system": {
    "database_status": "healthy",
    "python_version": "3.12.0",
    "settings": {...}
  }
}
```

### System Statistics

#### GET `/stats`
High-level system statistics.

**Response:**
```json
{
  "statistics": {
    "entities": {
      "total": 1500,
      "by_type": {"llc": 800, "corp": 600, "nonprofit": 100},
      "by_source": {"sunbiz": 1500}
    },
    "properties": {
      "total": 2500,
      "by_county": {"Marion": 2500}
    },
    "relationships": {
      "total": 5000,
      "by_type": {"owns": 2500, "agent_for": 1500, "officer_of": 1000}
    }
  }
}
```

### Entities

#### GET `/api/v1/entities/{entity_id}`
Get detailed entity information.

**Parameters:**
- `entity_id` (path): Entity ID

**Response:**
```json
{
  "id": 123,
  "external_id": "L21000123456",
  "source_system": "sunbiz",
  "type": "llc",
  "legal_name": "SUNRISE PROPERTIES LLC",
  "jurisdiction": "FL",
  "status": "ACTIVE",
  "formation_date": "2021-03-15",
  "ein_available": false,
  "ein_verified": false,
  "created_at": "2023-12-07T10:00:00Z",
  "updated_at": "2023-12-07T10:00:00Z",
  "registered_agent": {
    "id": 456,
    "full_name": "JOHN SMITH"
  },
  "primary_address": {
    "id": 789,
    "line1": "456 BUSINESS BLVD",
    "line2": "SUITE 200",
    "city": "MIAMI",
    "state": "FL",
    "postal_code": "33101",
    "country": "US"
  }
}
```

#### GET `/api/v1/entities/`
Search entities with filters.

**Query Parameters:**
- `name` (optional): Search by entity name
- `jurisdiction` (optional): Filter by jurisdiction
- `entity_type` (optional): Filter by entity type
- `status` (optional): Filter by status
- `limit` (optional): Maximum results (default: 50, max: 1000)

**Response:**
```json
[
  {
    "id": 123,
    "legal_name": "SUNRISE PROPERTIES LLC",
    "type": "llc",
    "jurisdiction": "FL",
    "status": "ACTIVE",
    "formation_date": "2021-03-15"
  }
]
```

#### POST `/api/v1/entities/`
Create a new entity.

**Request Body:**
```json
{
  "external_id": "L21000123456",
  "source_system": "sunbiz",
  "type": "llc",
  "legal_name": "NEW ENTITY LLC",
  "jurisdiction": "FL",
  "status": "ACTIVE",
  "formation_date": "2023-12-07",
  "agent_name": "JOHN SMITH",
  "address_data": {
    "line1": "123 MAIN ST",
    "city": "MIAMI",
    "state": "FL",
    "postal_code": "33101"
  }
}
```

#### GET `/api/v1/entities/{entity_id}/relationships`
Get all relationships for an entity.

**Query Parameters:**
- `relationship_type` (optional): Filter by relationship type

**Response:**
```json
{
  "entity_id": 123,
  "total_relationships": 5,
  "relationships": [
    {
      "id": 1,
      "direction": "outgoing",
      "type": "owns",
      "from_type": "entity",
      "from_id": 123,
      "to_type": "property",
      "to_id": 456,
      "source_system": "marion_pa",
      "confidence": 1.0
    }
  ]
}
```

#### GET `/api/v1/entities/{entity_id}/graph`
Get relationship graph for an entity.

**Query Parameters:**
- `max_depth` (optional): Maximum traversal depth (default: 2, max: 5)
- `relationship_types` (optional): Comma-separated relationship types

**Response:**
```json
{
  "nodes": {
    "entity:123": {
      "type": "entity",
      "id": 123,
      "depth": 0
    },
    "property:456": {
      "type": "property", 
      "id": 456,
      "depth": 1
    }
  },
  "edges": [
    {
      "from": "entity:123",
      "to": "property:456",
      "relationship": "owns",
      "source": "marion_pa",
      "confidence": 1.0
    }
  ],
  "total_nodes": 2,
  "total_edges": 1
}
```

### Properties

#### GET `/api/v1/properties/{property_id}`
Get detailed property information.

**Response:**
```json
{
  "id": 456,
  "parcel_id": "15-11-20-0000-00100-0000",
  "county": "Marion",
  "jurisdiction": "FL",
  "land_use_code": "0100",
  "acreage": 2.5,
  "last_sale_date": "2021-06-15",
  "last_sale_price": 485000.0,
  "market_value": 485000.0,
  "assessed_value": 465000.0,
  "homestead_exempt": "Y",
  "tax_year": "2023",
  "appraiser_url": "https://www.pa.marion.fl.us/search?parcel=...",
  "situs_address": {
    "id": 789,
    "line1": "1234 RANCH RD",
    "city": "OCALA",
    "state": "FL",
    "postal_code": "34471"
  }
}
```

#### GET `/api/v1/properties/`
Search properties with filters.

**Query Parameters:**
- `county` (optional): Filter by county
- `land_use_code` (optional): Filter by land use
- `min_value` (optional): Minimum property value
- `max_value` (optional): Maximum property value  
- `min_acres` (optional): Minimum acreage
- `limit` (optional): Maximum results

#### GET `/api/v1/properties/{property_id}/owners`
Get ownership information for a property.

**Response:**
```json
{
  "property_id": 456,
  "total_owners": 1,
  "owners": [
    {
      "type": "entity",
      "id": 123,
      "name": "SUNRISE PROPERTIES LLC",
      "relationship_id": 789,
      "source_system": "marion_pa",
      "confidence": 1.0,
      "details": {
        "legal_name": "SUNRISE PROPERTIES LLC",
        "type": "llc",
        "status": "ACTIVE"
      }
    }
  ]
}
```

#### GET `/api/v1/properties/stats/{county}`
Get market statistics for a county.

**Response:**
```json
{
  "county": "Marion",
  "total_properties": 2500,
  "avg_sale_price": 325000.0,
  "median_sale_price": 285000.0,
  "total_sales": 150
}
```

### Risk Scoring

#### GET `/api/v1/scores/entity/{entity_id}`
Calculate current risk score for an entity.

**Response:**
```json
{
  "entity_id": 123,
  "score": 25,
  "grade": "B",
  "flags": [
    "NEW_ENTITY_LT_90_DAYS",
    "OWNS_GT_10_PROPERTIES"
  ],
  "rule_details": [
    {
      "name": "NEW_ENTITY_LT_90_DAYS",
      "weight": 10,
      "category": "entity",
      "description": "Entity formed within last 90 days"
    }
  ],
  "context": {
    "property_count": 15,
    "entity_age_days": 60,
    "agent_entity_count": 25,
    "address_entity_count": 3
  }
}
```

#### GET `/api/v1/scores/entity/{entity_id}/latest`
Get most recent stored score (without recalculating).

#### GET `/api/v1/scores/entity/{entity_id}/history`
Get historical scores for an entity.

**Query Parameters:**
- `limit` (optional): Maximum historical scores (default: 10, max: 100)

#### POST `/api/v1/scores/batch`
Score multiple entities at once.

**Request Body:**
```json
{
  "entity_ids": [123, 456, 789]
}
```

**Response:**
```json
{
  "total_requested": 3,
  "total_scored": 3,
  "scores": [
    {
      "entity_id": 123,
      "score": 25,
      "grade": "B",
      "flags": ["NEW_ENTITY_LT_90_DAYS"]
    }
  ]
}
```

#### GET `/api/v1/scores/high-risk`
Get entities with high risk scores.

**Query Parameters:**
- `grade` (optional): Grade threshold (A-F, default: F)
- `limit` (optional): Maximum results

#### GET `/api/v1/scores/statistics`
Get scoring statistics across the system.

**Response:**
```json
{
  "total_entities_scored": 1500,
  "average_score": 32.5,
  "grade_distribution": {
    "A": 450,
    "B": 400, 
    "C": 350,
    "D": 200,
    "F": 100
  }
}
```

## Error Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

## Rate Limiting (Future)

Future API versions will implement rate limiting:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated access
- Burst allowance of 50 requests per minute

## Data Sources

### Currently Supported
- **Sunbiz**: Florida Division of Corporations
- **Marion County Property Appraiser**: FL property records

### Future Sources
- Additional Florida counties
- Other state registries
- Federal databases (as permitted)

## Changelog

### Version 1.0.0 (December 2023)
- Initial API release
- Entity and property management
- Basic risk scoring
- Sunbiz and Marion County data sources
- Graph relationship queries