# Entity service layer for business logic
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime
from .repository import EntityRepository, PersonRepository, AddressRepository
from .models import Entity, Person, Address
from app.core.logging import get_logger

logger = get_logger(__name__)


class EntityService:
    """Service layer for entity-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.entity_repo = EntityRepository(db)
        self.person_repo = PersonRepository(db)
        self.address_repo = AddressRepository(db)

    def get_entity_details(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """Get comprehensive entity details including relationships."""
        entity = self.entity_repo.get_by_id(entity_id)
        if not entity:
            return None

        result = {
            "id": entity.id,
            "external_id": entity.external_id,
            "source_system": entity.source_system,
            "type": entity.type,
            "legal_name": entity.legal_name,
            "jurisdiction": entity.jurisdiction,
            "status": entity.status,
            "formation_date": entity.formation_date.isoformat() if entity.formation_date else None,
            "ein_available": entity.ein_available,
            "ein_verified": entity.ein_verified,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
        }

        # Add registered agent if available
        if entity.registered_agent_id:
            agent = self.person_repo.get_by_id(entity.registered_agent_id)
            if agent:
                result["registered_agent"] = {
                    "id": agent.id,
                    "full_name": agent.full_name
                }

        # Add primary address if available
        if entity.primary_address_id:
            address = self.address_repo.get_by_id(entity.primary_address_id)
            if address:
                result["primary_address"] = {
                    "id": address.id,
                    "line1": address.line1,
                    "line2": address.line2,
                    "city": address.city,
                    "state": address.state,
                    "postal_code": address.postal_code,
                    "county": address.county,
                    "country": address.country
                }

        return result

    def search_entities(
        self,
        name: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        entity_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search entities with various filters."""
        # This is a simplified version - in production you'd want more sophisticated search
        if name:
            entities = self.entity_repo.search_by_name(name, limit)
        elif jurisdiction:
            entities = self.entity_repo.get_by_jurisdiction(jurisdiction, limit)
        elif status:
            entities = self.entity_repo.get_entities_by_status(status, limit)
        else:
            # Default query - get recent entities
            entities = self.db.query(Entity).order_by(Entity.created_at.desc()).limit(limit).all()

        return [
            {
                "id": entity.id,
                "legal_name": entity.legal_name,
                "type": entity.type,
                "jurisdiction": entity.jurisdiction,
                "status": entity.status,
                "formation_date": entity.formation_date.isoformat() if entity.formation_date else None,
            }
            for entity in entities
        ]

    def create_entity_with_relationships(
        self,
        entity_data: Dict[str, Any],
        agent_name: Optional[str] = None,
        address_data: Optional[Dict[str, Any]] = None
    ) -> Entity:
        """Create entity with related person and address records."""
        
        # Handle registered agent
        agent_id = None
        if agent_name:
            agent = self.person_repo.upsert_person(agent_name)
            agent_id = agent.id

        # Handle primary address
        address_id = None
        if address_data:
            address = self.address_repo.upsert_address(**address_data)
            address_id = address.id

        # Prepare entity data with relationships
        entity_defaults = entity_data.copy()
        entity_defaults["registered_agent_id"] = agent_id
        entity_defaults["primary_address_id"] = address_id

        # Create/update entity
        entity = self.entity_repo.upsert_entity(
            source_system=entity_data["source_system"],
            external_id=entity_data["external_id"],
            defaults=entity_defaults
        )

        self.db.commit()
        
        logger.info(
            f"Created/updated entity with relationships",
            extra={
                "entity_id": entity.id,
                "source_system": entity.source_system,
                "has_agent": agent_id is not None,
                "has_address": address_id is not None
            }
        )

        return entity

    def get_entity_age_days(self, entity: Entity) -> Optional[int]:
        """Calculate entity age in days."""
        if not entity.formation_date:
            return None
        return (date.today() - entity.formation_date).days

    def get_entities_by_agent(self, agent_id: int) -> List[Entity]:
        """Get all entities for a registered agent."""
        return self.db.query(Entity).filter(
            Entity.registered_agent_id == agent_id
        ).all()

    def get_entities_by_address(self, address_id: int) -> List[Entity]:
        """Get all entities at a specific address."""
        return self.db.query(Entity).filter(
            Entity.primary_address_id == address_id
        ).all()