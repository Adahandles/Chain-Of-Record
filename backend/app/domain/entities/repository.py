# Entity repository for database operations
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .models import Entity, Person, Address
from app.core.logging import get_logger
import hashlib

logger = get_logger(__name__)


class EntityRepository:
    """Repository for entity-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, entity_id: int) -> Optional[Entity]:
        """Get entity by ID."""
        return self.db.query(Entity).filter(Entity.id == entity_id).first()

    def get_by_external_id(self, source_system: str, external_id: str) -> Optional[Entity]:
        """Get entity by source system and external ID."""
        return self.db.query(Entity).filter(
            and_(
                Entity.source_system == source_system,
                Entity.external_id == external_id
            )
        ).first()

    def search_by_name(self, name: str, limit: int = 50) -> List[Entity]:
        """Search entities by name (case-insensitive partial match)."""
        return self.db.query(Entity).filter(
            Entity.legal_name.ilike(f"%{name}%")
        ).limit(limit).all()

    def get_by_jurisdiction(self, jurisdiction: str, limit: int = 100) -> List[Entity]:
        """Get entities by jurisdiction."""
        return self.db.query(Entity).filter(
            Entity.jurisdiction == jurisdiction
        ).limit(limit).all()

    def upsert_entity(
        self,
        source_system: str,
        external_id: str,
        defaults: dict
    ) -> Entity:
        """Insert or update entity based on source_system and external_id."""
        entity = self.get_by_external_id(source_system, external_id)
        
        if entity is None:
            entity = Entity(
                source_system=source_system,
                external_id=external_id,
                **defaults
            )
            self.db.add(entity)
            logger.info(f"Created new entity: {defaults.get('legal_name')}")
        else:
            # Update existing entity
            for key, value in defaults.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            logger.info(f"Updated entity: {entity.legal_name}")
        
        self.db.flush()
        return entity

    def get_entities_by_status(self, status: str, limit: int = 100) -> List[Entity]:
        """Get entities by status."""
        return self.db.query(Entity).filter(
            Entity.status == status
        ).limit(limit).all()


class PersonRepository:
    """Repository for person-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, person_id: int) -> Optional[Person]:
        """Get person by ID."""
        return self.db.query(Person).filter(Person.id == person_id).first()

    def search_by_name(self, name: str, limit: int = 50) -> List[Person]:
        """Search people by name."""
        normalized_search = self._normalize_name(name)
        return self.db.query(Person).filter(
            or_(
                Person.full_name.ilike(f"%{name}%"),
                Person.normalized_name.ilike(f"%{normalized_search}%")
            )
        ).limit(limit).all()

    def upsert_person(self, full_name: str) -> Person:
        """Insert or update person by normalized name."""
        normalized_name = self._normalize_name(full_name)
        
        person = self.db.query(Person).filter(
            Person.normalized_name == normalized_name
        ).first()
        
        if person is None:
            person = Person(
                full_name=full_name.strip(),
                normalized_name=normalized_name
            )
            self.db.add(person)
            logger.info(f"Created new person: {full_name}")
        else:
            # Update with the most recent version of the name
            person.full_name = full_name.strip()
            logger.info(f"Updated person: {full_name}")
        
        self.db.flush()
        return person

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize name for matching (uppercase, remove punctuation)."""
        import re
        if not name:
            return ""
        # Remove punctuation, convert to uppercase, collapse whitespace
        normalized = re.sub(r'[^\w\s]', '', name.upper())
        return ' '.join(normalized.split())


class AddressRepository:
    """Repository for address-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, address_id: int) -> Optional[Address]:
        """Get address by ID."""
        return self.db.query(Address).filter(Address.id == address_id).first()

    def get_by_hash(self, normalized_hash: str) -> Optional[Address]:
        """Get address by normalized hash."""
        return self.db.query(Address).filter(
            Address.normalized_hash == normalized_hash
        ).first()

    def upsert_address(
        self,
        line1: str,
        line2: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        county: Optional[str] = None,
        country: str = 'US'
    ) -> Address:
        """Insert or update address based on normalized hash."""
        normalized_hash = self._create_address_hash(
            line1, line2, city, state, postal_code, county, country
        )
        
        address = self.get_by_hash(normalized_hash)
        
        if address is None:
            address = Address(
                line1=line1.strip(),
                line2=line2.strip() if line2 else None,
                city=city.strip() if city else None,
                state=state.strip().upper() if state else None,
                postal_code=postal_code.strip() if postal_code else None,
                county=county.strip() if county else None,
                country=country.strip().upper(),
                normalized_hash=normalized_hash
            )
            self.db.add(address)
            logger.info(f"Created new address: {line1}, {city}")
        
        self.db.flush()
        return address

    @staticmethod
    def _create_address_hash(
        line1: str,
        line2: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        county: Optional[str] = None,
        country: str = 'US'
    ) -> str:
        """Create normalized hash for address deduplication."""
        # Normalize all components
        components = []
        
        if line1:
            components.append(line1.strip().upper())
        if line2:
            components.append(line2.strip().upper())
        if city:
            components.append(city.strip().upper())
        if state:
            components.append(state.strip().upper())
        if postal_code:
            # Remove non-alphanumeric for postal codes
            import re
            clean_postal = re.sub(r'[^A-Z0-9]', '', postal_code.upper())
            components.append(clean_postal)
        if county:
            components.append(county.strip().upper())
        
        components.append(country.strip().upper())
        
        # Create hash from normalized components
        normalized_string = '|'.join(components)
        return hashlib.sha256(normalized_string.encode()).hexdigest()[:16]