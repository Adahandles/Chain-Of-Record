# Entity domain models
from sqlalchemy import Column, BigInteger, String, Date, Boolean, Text, DateTime, func, Index
from sqlalchemy.orm import relationship
from app.core.db import Base


class Entity(Base):
    """
    Core entity model representing legal entities from various sources.
    Supports LLCs, Corporations, Trusts, Nonprofits, and Persons.
    """
    __tablename__ = "entities"

    id = Column(BigInteger, primary_key=True, index=True)
    external_id = Column(String, index=True)  # Source system's ID (e.g., doc number)
    source_system = Column(String, nullable=False, index=True)  # 'sunbiz', 'marion_pa', etc.
    type = Column(String, nullable=False, index=True)  # 'llc','corp','trust','nonprofit','person'
    legal_name = Column(Text, nullable=False, index=True)
    jurisdiction = Column(String, index=True)  # 'FL', 'DE', etc.
    status = Column(String, index=True)  # 'ACTIVE','INACTIVE','DISSOLVED'
    formation_date = Column(Date)
    ein_available = Column(Boolean)
    ein_verified = Column(Boolean)
    registered_agent_id = Column(BigInteger, index=True)  # FK to people table
    primary_address_id = Column(BigInteger, index=True)  # FK to addresses table

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    # Note: We'll define these after other models are created to avoid circular imports

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_entity_source_external', 'source_system', 'external_id'),
        Index('idx_entity_name_type', 'legal_name', 'type'),
        Index('idx_entity_jurisdiction_status', 'jurisdiction', 'status'),
    )

    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, name='{self.legal_name}', type='{self.type}')>"


class Person(Base):
    """
    Person model for registered agents, officers, and other individuals.
    """
    __tablename__ = "people"

    id = Column(BigInteger, primary_key=True, index=True)
    full_name = Column(Text, nullable=False, index=True)
    normalized_name = Column(Text, index=True)  # Uppercase, stripped punctuation for matching
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Person(id={self.id}, name='{self.full_name}')>"


class Address(Base):
    """
    Address model for entity and property locations.
    """
    __tablename__ = "addresses"

    id = Column(BigInteger, primary_key=True, index=True)
    line1 = Column(Text, nullable=False)
    line2 = Column(Text)
    city = Column(Text, index=True)
    state = Column(String(2), index=True)
    postal_code = Column(String(10), index=True)
    county = Column(Text, index=True)
    country = Column(String(2), default='US', index=True)
    normalized_hash = Column(String(64), unique=True, index=True)  # For deduplication
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_address_city_state', 'city', 'state'),
        Index('idx_address_postal_county', 'postal_code', 'county'),
    )

    def __repr__(self) -> str:
        return f"<Address(id={self.id}, line1='{self.line1}', city='{self.city}')>"