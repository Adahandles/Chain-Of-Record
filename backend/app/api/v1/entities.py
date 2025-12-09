# Entity API endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.domain.entities.service import EntityService
from app.schemas.entities import (
    EntityOut, EntityListItem, EntitySearchParams, 
    EntityCreate, AddressCreate
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("/{entity_id}", response_model=EntityOut)
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific entity."""
    service = EntityService(db)
    entity_data = service.get_entity_details(entity_id)
    
    if not entity_data:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    logger.info(f"Retrieved entity details", extra={"entity_id": entity_id})
    return entity_data


@router.get("/", response_model=List[EntityListItem])
def search_entities(
    name: Optional[str] = Query(None, description="Search by entity name"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Maximum number of results", le=1000),
    db: Session = Depends(get_db)
):
    """Search entities with various filters."""
    service = EntityService(db)
    
    entities = service.search_entities(
        name=name,
        jurisdiction=jurisdiction,
        entity_type=entity_type,
        status=status,
        limit=limit
    )
    
    logger.info(
        f"Entity search returned {len(entities)} results",
        extra={"search_name": name, "jurisdiction": jurisdiction}
    )
    
    return entities


@router.post("/", response_model=EntityOut)
def create_entity(
    entity_data: EntityCreate,
    agent_name: Optional[str] = None,
    address_data: Optional[AddressCreate] = None,
    db: Session = Depends(get_db)
):
    """Create a new entity with optional registered agent and address."""
    service = EntityService(db)
    
    # Convert Pydantic models to dicts
    entity_dict = entity_data.dict()
    address_dict = address_data.dict() if address_data else None
    
    try:
        entity = service.create_entity_with_relationships(
            entity_data=entity_dict,
            agent_name=agent_name,
            address_data=address_dict
        )
        
        # Return detailed entity data
        entity_details = service.get_entity_details(entity.id)
        
        logger.info(
            f"Created new entity: {entity.legal_name}",
            extra={"entity_id": entity.id, "source_system": entity.source_system}
        )
        
        return entity_details
        
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{entity_id}/relationships")
def get_entity_relationships(
    entity_id: int,
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    db: Session = Depends(get_db)
):
    """Get all relationships for an entity."""
    from app.domain.graph.service import GraphService
    
    # Verify entity exists
    service = EntityService(db)
    entity_data = service.get_entity_details(entity_id)
    if not entity_data:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    graph_service = GraphService(db)
    
    # Get outgoing relationships
    outgoing = graph_service.get_outgoing_relationships(
        node_type="entity",
        node_id=entity_id,
        rel_type=relationship_type
    )
    
    # Get incoming relationships  
    incoming = graph_service.get_incoming_relationships(
        node_type="entity",
        node_id=entity_id,
        rel_type=relationship_type
    )
    
    def format_relationship(rel, direction):
        return {
            "id": rel.id,
            "direction": direction,
            "type": rel.rel_type,
            "from_type": rel.from_type,
            "from_id": rel.from_id,
            "to_type": rel.to_type,
            "to_id": rel.to_id,
            "source_system": rel.source_system,
            "start_date": rel.start_date.isoformat() if rel.start_date else None,
            "end_date": rel.end_date.isoformat() if rel.end_date else None,
            "confidence": float(rel.confidence) if rel.confidence else None,
        }
    
    relationships = []
    relationships.extend([format_relationship(rel, "outgoing") for rel in outgoing])
    relationships.extend([format_relationship(rel, "incoming") for rel in incoming])
    
    return {
        "entity_id": entity_id,
        "total_relationships": len(relationships),
        "relationships": relationships
    }


@router.get("/{entity_id}/graph")
def get_entity_graph(
    entity_id: int,
    max_depth: int = Query(2, description="Maximum traversal depth", le=5),
    relationship_types: Optional[str] = Query(None, description="Comma-separated relationship types to include"),
    db: Session = Depends(get_db)
):
    """Get the relationship graph for an entity."""
    from app.domain.graph.service import GraphService
    
    # Verify entity exists
    service = EntityService(db)
    entity_data = service.get_entity_details(entity_id)
    if not entity_data:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    graph_service = GraphService(db)
    
    # Parse relationship types
    rel_types = None
    if relationship_types:
        rel_types = [rt.strip() for rt in relationship_types.split(",")]
    
    graph_data = graph_service.find_connected_entities(
        entity_id=entity_id,
        max_depth=max_depth,
        rel_types=rel_types
    )
    
    logger.info(
        f"Generated graph for entity {entity_id}",
        extra={"entity_id": entity_id, "nodes": graph_data["total_nodes"]}
    )
    
    return graph_data