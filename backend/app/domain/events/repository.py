# Events repository for time-series data
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import date, datetime, timedelta
from app.domain.graph.models import Event
from app.core.logging import get_logger

logger = get_logger(__name__)


class EventRepository:
    """Repository for event-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_event(
        self,
        entity_id: int,
        event_type: str,
        event_date: date,
        source_system: str,
        payload: Dict[str, Any]
    ) -> Event:
        """Create a new event."""
        event = Event(
            entity_id=entity_id,
            event_type=event_type,
            event_date=event_date,
            source_system=source_system,
            payload=payload
        )
        self.db.add(event)
        self.db.flush()
        
        logger.info(
            f"Created event: {event_type} for entity {entity_id}",
            extra={"entity_id": entity_id, "event_type": event_type}
        )
        
        return event

    def get_events_for_entity(
        self,
        entity_id: int,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get events for a specific entity."""
        query = self.db.query(Event).filter(Event.entity_id == entity_id)
        
        if event_type:
            query = query.filter(Event.event_type == event_type)
        
        return query.order_by(desc(Event.event_date)).limit(limit).all()

    def get_recent_events(
        self,
        days: int = 30,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get recent events across all entities."""
        since_date = date.today() - timedelta(days=days)
        
        query = self.db.query(Event).filter(Event.event_date >= since_date)
        
        if event_type:
            query = query.filter(Event.event_type == event_type)
        
        return query.order_by(desc(Event.event_date)).limit(limit).all()

    def get_events_by_type(
        self,
        event_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get events of a specific type within date range."""
        query = self.db.query(Event).filter(Event.event_type == event_type)
        
        if start_date:
            query = query.filter(Event.event_date >= start_date)
        if end_date:
            query = query.filter(Event.event_date <= end_date)
        
        return query.order_by(desc(Event.event_date)).limit(limit).all()

    def get_event_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about events."""
        from sqlalchemy import func
        
        total_events = self.db.query(Event).count()
        
        # Count by event type
        event_type_counts = self.db.query(
            Event.event_type,
            func.count(Event.id)
        ).group_by(Event.event_type).all()
        
        # Count by source system
        source_counts = self.db.query(
            Event.source_system,
            func.count(Event.id)
        ).group_by(Event.source_system).all()
        
        # Recent activity (last 30 days)
        recent_cutoff = date.today() - timedelta(days=30)
        recent_count = self.db.query(Event).filter(
            Event.event_date >= recent_cutoff
        ).count()
        
        return {
            "total_events": total_events,
            "recent_events_30d": recent_count,
            "by_type": {event_type: count for event_type, count in event_type_counts},
            "by_source": {source: count for source, count in source_counts}
        }