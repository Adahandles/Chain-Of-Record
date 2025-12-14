# Graph service for relationship queries and analysis
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from .models import Relationship, Event, RiskScore
from app.core.logging import get_logger

logger = get_logger(__name__)


class GraphService:
    """Service for graph traversal and relationship analysis."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_relationship(
        self,
        from_type: str,
        from_id: int,
        to_type: str, 
        to_id: int,
        rel_type: str,
        source_system: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> Relationship:
        """Create a new relationship between two nodes."""
        
        # Check if relationship already exists
        existing = self.db.query(Relationship).filter(
            and_(
                Relationship.from_type == from_type,
                Relationship.from_id == from_id,
                Relationship.to_type == to_type,
                Relationship.to_id == to_id,
                Relationship.rel_type == rel_type,
                Relationship.end_date.is_(None)  # Only active relationships
            )
        ).first()
        
        if existing:
            logger.info(f"Relationship already exists: {rel_type}")
            return existing
        
        relationship = Relationship(
            from_type=from_type,
            from_id=from_id,
            to_type=to_type,
            to_id=to_id,
            rel_type=rel_type,
            source_system=source_system,
            start_date=start_date,
            end_date=end_date,
            confidence=confidence or 1.0
        )
        
        self.db.add(relationship)
        self.db.flush()
        
        logger.info(
            f"Created relationship: {from_type}:{from_id} -> {rel_type} -> {to_type}:{to_id}",
            extra={"source_system": source_system}
        )
        
        return relationship

    def get_outgoing_relationships(
        self,
        node_type: str,
        node_id: int,
        rel_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Relationship]:
        """Get relationships where this node is the source."""
        query = self.db.query(Relationship).filter(
            and_(
                Relationship.from_type == node_type,
                Relationship.from_id == node_id
            )
        )
        
        if rel_type:
            query = query.filter(Relationship.rel_type == rel_type)
        
        if active_only:
            query = query.filter(Relationship.end_date.is_(None))
        
        return query.all()

    def get_incoming_relationships(
        self,
        node_type: str,
        node_id: int,
        rel_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Relationship]:
        """Get relationships where this node is the target."""
        query = self.db.query(Relationship).filter(
            and_(
                Relationship.to_type == node_type,
                Relationship.to_id == node_id
            )
        )
        
        if rel_type:
            query = query.filter(Relationship.rel_type == rel_type)
        
        if active_only:
            query = query.filter(Relationship.end_date.is_(None))
        
        return query.all()

    def get_properties_owned_by_entity(self, entity_id: int) -> List[int]:
        """Get property IDs owned by an entity."""
        relationships = self.get_outgoing_relationships(
            node_type="entity",
            node_id=entity_id,
            rel_type="owns"
        )
        return [r.to_id for r in relationships if r.to_type == "property"]

    def get_entities_at_address(self, address_id: int) -> List[int]:
        """Get entity IDs that have primary address at this location."""
        # This would require a join with the entities table
        from app.domain.entities.models import Entity
        
        entities = self.db.query(Entity).filter(
            Entity.primary_address_id == address_id
        ).all()
        
        return [e.id for e in entities]

    def get_agent_relationships(self, person_id: int) -> List[Relationship]:
        """Get all entities where this person is a registered agent."""
        return self.get_outgoing_relationships(
            node_type="person",
            node_id=person_id,
            rel_type="agent_for"
        )

    def find_connected_entities(
        self,
        entity_id: int,
        max_depth: int = 2,
        rel_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Find entities connected through various relationship types.
        Returns a graph structure with nodes and edges.
        """
        visited = set()
        nodes = {}
        edges = []
        
        def traverse(current_type: str, current_id: int, depth: int):
            if depth > max_depth or (current_type, current_id) in visited:
                return
            
            visited.add((current_type, current_id))
            nodes[f"{current_type}:{current_id}"] = {
                "type": current_type,
                "id": current_id,
                "depth": depth
            }
            
            # Get outgoing relationships
            outgoing = self.get_outgoing_relationships(current_type, current_id)
            for rel in outgoing:
                if rel_types and rel.rel_type not in rel_types:
                    continue
                
                edge = {
                    "from": f"{current_type}:{current_id}",
                    "to": f"{rel.to_type}:{rel.to_id}",
                    "relationship": rel.rel_type,
                    "source": rel.source_system,
                    "confidence": float(rel.confidence) if rel.confidence else 1.0
                }
                edges.append(edge)
                
                traverse(rel.to_type, rel.to_id, depth + 1)
            
            # Get incoming relationships
            incoming = self.get_incoming_relationships(current_type, current_id)
            for rel in incoming:
                if rel_types and rel.rel_type not in rel_types:
                    continue
                
                edge = {
                    "from": f"{rel.from_type}:{rel.from_id}",
                    "to": f"{current_type}:{current_id}",
                    "relationship": rel.rel_type,
                    "source": rel.source_system,
                    "confidence": float(rel.confidence) if rel.confidence else 1.0
                }
                edges.append(edge)
                
                traverse(rel.from_type, rel.from_id, depth + 1)
        
        traverse("entity", entity_id, 0)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }

    def get_relationship_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about relationships in the graph."""
        total_relationships = self.db.query(Relationship).count()
        
        # Count by relationship type
        rel_type_counts = self.db.query(
            Relationship.rel_type,
            func.count(Relationship.id)
        ).group_by(Relationship.rel_type).all()
        
        # Count by source system
        source_counts = self.db.query(
            Relationship.source_system,
            func.count(Relationship.id)
        ).group_by(Relationship.source_system).all()
        
        return {
            "total_relationships": total_relationships,
            "by_type": {rel_type: count for rel_type, count in rel_type_counts},
            "by_source": {source: count for source, count in source_counts}
        }