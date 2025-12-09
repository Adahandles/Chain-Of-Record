# Advanced scoring engine with pluggable rules
from dataclasses import dataclass
from typing import Callable, List, Dict, Any, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.domain.entities.models import Entity
from app.domain.graph.service import GraphService
from app.domain.graph.models import RiskScore
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ScoringRule:
    """A single scoring rule with metadata."""
    name: str
    weight: int
    category: str  # 'entity', 'relationships', 'temporal', 'property'
    description: str
    fn: Callable[['ScoringContext'], bool]


@dataclass
class ScoringContext:
    """Context object containing all data needed for scoring an entity."""
    entity: Entity
    db: Session
    property_count: int = 0
    entity_age_days: Optional[int] = None
    agent_entity_count: int = 0  # How many entities this agent represents
    address_entity_count: int = 0  # How many entities at this address
    recent_events: List[Any] = None
    graph_service: Optional[GraphService] = None
    
    def __post_init__(self):
        if self.recent_events is None:
            self.recent_events = []
        if self.graph_service is None:
            self.graph_service = GraphService(self.db)


def grade_score(score: int) -> str:
    """Convert numeric score to letter grade."""
    if score <= 20:
        return "A"
    elif score <= 40:
        return "B"
    elif score <= 60:
        return "C"
    elif score <= 80:
        return "D"
    else:
        return "F"


class RuleRegistry:
    """Registry for all scoring rules, organized by category."""
    
    def __init__(self):
        self._rules: List[ScoringRule] = []
        self._register_default_rules()
    
    def register_rule(self, rule: ScoringRule) -> None:
        """Register a new scoring rule."""
        self._rules.append(rule)
        logger.info(f"Registered scoring rule: {rule.name}")
    
    def get_rules(self, category: Optional[str] = None) -> List[ScoringRule]:
        """Get all rules, optionally filtered by category."""
        if category:
            return [rule for rule in self._rules if rule.category == category]
        return self._rules.copy()
    
    def _register_default_rules(self) -> None:
        """Register the default set of scoring rules."""
        
        # Entity-based rules
        self.register_rule(ScoringRule(
            name="NEW_ENTITY_LT_90_DAYS",
            weight=10,
            category="entity",
            description="Entity formed within last 90 days",
            fn=lambda ctx: ctx.entity_age_days is not None and ctx.entity_age_days < 90
        ))
        
        self.register_rule(ScoringRule(
            name="NEW_ENTITY_LT_30_DAYS", 
            weight=15,
            category="entity",
            description="Entity formed within last 30 days",
            fn=lambda ctx: ctx.entity_age_days is not None and ctx.entity_age_days < 30
        ))
        
        self.register_rule(ScoringRule(
            name="NO_PRIMARY_ADDRESS",
            weight=5,
            category="entity", 
            description="Entity has no primary address on file",
            fn=lambda ctx: ctx.entity.primary_address_id is None
        ))
        
        self.register_rule(ScoringRule(
            name="INACTIVE_STATUS",
            weight=8,
            category="entity",
            description="Entity status is inactive or dissolved", 
            fn=lambda ctx: ctx.entity.status and ctx.entity.status.upper() in ['INACTIVE', 'DISSOLVED']
        ))
        
        # Property-based rules
        self.register_rule(ScoringRule(
            name="OWNS_GT_10_PROPERTIES",
            weight=10,
            category="property",
            description="Entity owns more than 10 properties",
            fn=lambda ctx: ctx.property_count > 10
        ))
        
        self.register_rule(ScoringRule(
            name="OWNS_GT_25_PROPERTIES", 
            weight=20,
            category="property",
            description="Entity owns more than 25 properties",
            fn=lambda ctx: ctx.property_count > 25
        ))
        
        self.register_rule(ScoringRule(
            name="NO_PROPERTY_OWNERSHIP",
            weight=5,
            category="property", 
            description="Entity owns no properties (may be shell)",
            fn=lambda ctx: ctx.property_count == 0 and ctx.entity_age_days and ctx.entity_age_days > 365
        ))
        
        # Relationship-based rules
        self.register_rule(ScoringRule(
            name="AGENT_REPRESENTS_GT_50_ENTITIES",
            weight=15,
            category="relationships",
            description="Registered agent represents more than 50 entities",
            fn=lambda ctx: ctx.agent_entity_count > 50
        ))
        
        self.register_rule(ScoringRule(
            name="ADDRESS_GT_20_ENTITIES",
            weight=12,
            category="relationships", 
            description="More than 20 entities at same address",
            fn=lambda ctx: ctx.address_entity_count > 20
        ))
        
        self.register_rule(ScoringRule(
            name="ADDRESS_GT_5_ENTITIES_NEW",
            weight=8,
            category="relationships",
            description="More than 5 entities at same address, entity is new",
            fn=lambda ctx: ctx.address_entity_count > 5 and ctx.entity_age_days and ctx.entity_age_days < 180
        ))


class ScoringEngine:
    """Main scoring engine that evaluates entities against registered rules."""
    
    def __init__(self, db: Session):
        self.db = db
        self.rule_registry = RuleRegistry()
        self.graph_service = GraphService(db)
    
    def score_entity(self, entity_id: int) -> Dict[str, Any]:
        """Score an entity and return detailed results."""
        entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")
        
        # Build scoring context
        ctx = self._build_context(entity)
        
        # Evaluate all rules
        score = 0
        triggered_flags = []
        rule_details = []
        
        for rule in self.rule_registry.get_rules():
            try:
                if rule.fn(ctx):
                    score += rule.weight
                    triggered_flags.append(rule.name)
                    rule_details.append({
                        "name": rule.name,
                        "weight": rule.weight,
                        "category": rule.category,
                        "description": rule.description
                    })
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
                continue
        
        grade = grade_score(score)
        
        result = {
            "entity_id": entity_id,
            "score": score,
            "grade": grade,
            "flags": triggered_flags,
            "rule_details": rule_details,
            "context": {
                "property_count": ctx.property_count,
                "entity_age_days": ctx.entity_age_days,
                "agent_entity_count": ctx.agent_entity_count,
                "address_entity_count": ctx.address_entity_count
            }
        }
        
        # Persist the score
        self._save_score(entity_id, score, grade, triggered_flags)
        
        return result
    
    def _build_context(self, entity: Entity) -> ScoringContext:
        """Build comprehensive context for scoring."""
        
        # Calculate entity age
        entity_age_days = None
        if entity.formation_date:
            entity_age_days = (date.today() - entity.formation_date).days
        
        # Count properties owned
        property_relationships = self.graph_service.get_outgoing_relationships(
            node_type="entity",
            node_id=entity.id,
            rel_type="owns"
        )
        property_count = len([r for r in property_relationships if r.to_type == "property"])
        
        # Count entities represented by same agent
        agent_entity_count = 0
        if entity.registered_agent_id:
            agent_relationships = self.graph_service.get_outgoing_relationships(
                node_type="person", 
                node_id=entity.registered_agent_id,
                rel_type="agent_for"
            )
            agent_entity_count = len([r for r in agent_relationships if r.to_type == "entity"])
        
        # Count entities at same address  
        address_entity_count = 0
        if entity.primary_address_id:
            address_entities = self.graph_service.get_entities_at_address(entity.primary_address_id)
            address_entity_count = len(address_entities)
        
        return ScoringContext(
            entity=entity,
            db=self.db,
            property_count=property_count,
            entity_age_days=entity_age_days,
            agent_entity_count=agent_entity_count,
            address_entity_count=address_entity_count,
            graph_service=self.graph_service
        )
    
    def _save_score(self, entity_id: int, score: int, grade: str, flags: List[str]) -> None:
        """Save the calculated score to the database."""
        risk_score = RiskScore(
            entity_id=entity_id,
            score=score,
            grade=grade,
            flags=flags
        )
        self.db.add(risk_score)
        self.db.commit()
        
        logger.info(
            f"Saved risk score for entity {entity_id}: {score} ({grade})",
            extra={"entity_id": entity_id, "score": score, "grade": grade}
        )
    
    def get_latest_score(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """Get the most recent score for an entity."""
        latest_score = self.db.query(RiskScore).filter(
            RiskScore.entity_id == entity_id
        ).order_by(RiskScore.calculated_at.desc()).first()
        
        if not latest_score:
            return None
        
        return {
            "entity_id": entity_id,
            "score": float(latest_score.score),
            "grade": latest_score.grade,
            "flags": latest_score.flags,
            "calculated_at": latest_score.calculated_at.isoformat()
        }
    
    def batch_score_entities(self, entity_ids: List[int]) -> List[Dict[str, Any]]:
        """Score multiple entities in batch."""
        results = []
        for entity_id in entity_ids:
            try:
                result = self.score_entity(entity_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scoring entity {entity_id}: {e}")
                continue
        return results