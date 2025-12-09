# Graph relationship models
from sqlalchemy import Column, BigInteger, String, Date, DateTime, Numeric, Index, func
from app.core.db import Base


class Relationship(Base):
    """
    Generic graph table for relationships between entities, people, and properties.
    Enables tracking ownership, management, agency, and other connections.
    """
    __tablename__ = "relationships"

    id = Column(BigInteger, primary_key=True, index=True)
    
    # From node
    from_type = Column(String, nullable=False, index=True)  # 'entity', 'person', 'property'
    from_id = Column(BigInteger, nullable=False, index=True)
    
    # To node  
    to_type = Column(String, nullable=False, index=True)
    to_id = Column(BigInteger, nullable=False, index=True)
    
    # Relationship metadata
    rel_type = Column(String, nullable=False, index=True)  # 'owns', 'manages', 'agent_for', 'grants_to'
    source_system = Column(String, nullable=False, index=True)  # Where this relationship was discovered
    start_date = Column(Date)  # When relationship began
    end_date = Column(Date)    # When relationship ended (NULL = active)
    confidence = Column(Numeric(3, 2))  # 0.0-1.0 confidence score
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite indexes for efficient graph traversal
    __table_args__ = (
        Index('idx_relationship_from', 'from_type', 'from_id', 'rel_type'),
        Index('idx_relationship_to', 'to_type', 'to_id', 'rel_type'),
        Index('idx_relationship_active', 'end_date'),  # NULL end_date = active
        Index('idx_relationship_source', 'source_system', 'rel_type'),
    )

    def __repr__(self) -> str:
        return f"<Relationship({self.from_type}:{self.from_id} -> {self.rel_type} -> {self.to_type}:{self.to_id})>"


class Event(Base):
    """
    Time-series events for entities (officer changes, filings, deeds, etc.)
    """
    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True, index=True)
    entity_id = Column(BigInteger, nullable=False, index=True)  # Always tied to an entity
    event_type = Column(String, nullable=False, index=True)     # 'OFFICER_CHANGE', 'DEED', 'TAX_DELINQ'
    event_date = Column(Date, nullable=False, index=True)
    source_system = Column(String, nullable=False, index=True)
    payload = Column('payload', type_=func.JSON)  # JSON data specific to event type
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_event_entity_type', 'entity_id', 'event_type'),
        Index('idx_event_date_type', 'event_date', 'event_type'),
        Index('idx_event_source', 'source_system', 'event_type'),
    )

    def __repr__(self) -> str:
        return f"<Event(entity_id={self.entity_id}, type='{self.event_type}', date={self.event_date})>"


class RiskScore(Base):
    """
    Risk assessment scores for entities
    """
    __tablename__ = "risk_scores"

    id = Column(BigInteger, primary_key=True, index=True)
    entity_id = Column(BigInteger, nullable=False, index=True)
    score = Column(Numeric(5, 2), nullable=False)  # Numeric risk score
    grade = Column(String(1), nullable=False, index=True)  # 'A' through 'F'
    flags = Column('flags', type_=func.JSON, nullable=False)  # List of triggered rule names
    
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index('idx_risk_score_grade', 'grade', 'score'),
        Index('idx_risk_score_entity_date', 'entity_id', 'calculated_at'),
    )

    def __repr__(self) -> str:
        return f"<RiskScore(entity_id={self.entity_id}, score={self.score}, grade='{self.grade}')>"