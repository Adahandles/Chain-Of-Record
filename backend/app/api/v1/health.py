# Health check and system status endpoints
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.config import settings
from datetime import datetime
import sys

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
        "version": "1.0.0"
    }


@router.get("/health/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check including database connectivity."""
    
    # Test database connection
    db_status = "healthy"
    try:
        db.execute("SELECT 1")
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # System information
    system_info = {
        "python_version": sys.version,
        "database_status": db_status,
        "settings": {
            "environment": settings.environment,
            "log_level": settings.log_level,
            "api_prefix": settings.api_v1_prefix
        }
    }
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "system": system_info
    }


@router.get("/stats")
def get_system_statistics(db: Session = Depends(get_db)):
    """Get high-level system statistics."""
    from app.domain.entities.models import Entity
    from app.domain.properties.models import Property
    from app.domain.graph.models import Relationship, Event, RiskScore
    from sqlalchemy import func
    
    try:
        stats = {
            "entities": {
                "total": db.query(func.count(Entity.id)).scalar() or 0,
                "by_type": dict(db.query(Entity.type, func.count(Entity.id)).group_by(Entity.type).all()),
                "by_source": dict(db.query(Entity.source_system, func.count(Entity.id)).group_by(Entity.source_system).all())
            },
            "properties": {
                "total": db.query(func.count(Property.id)).scalar() or 0,
                "by_county": dict(db.query(Property.county, func.count(Property.id)).group_by(Property.county).all())
            },
            "relationships": {
                "total": db.query(func.count(Relationship.id)).scalar() or 0,
                "by_type": dict(db.query(Relationship.rel_type, func.count(Relationship.id)).group_by(Relationship.rel_type).all())
            },
            "events": {
                "total": db.query(func.count(Event.id)).scalar() or 0,
                "by_type": dict(db.query(Event.event_type, func.count(Event.id)).group_by(Event.event_type).all())
            },
            "risk_scores": {
                "total": db.query(func.count(RiskScore.id)).scalar() or 0,
                "by_grade": dict(db.query(RiskScore.grade, func.count(RiskScore.id)).group_by(RiskScore.grade).all())
            }
        }
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats
        }
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }