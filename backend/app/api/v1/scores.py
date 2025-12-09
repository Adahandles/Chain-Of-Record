# Scoring API endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.domain.scoring.engine import ScoringEngine
from app.schemas.scores import (
    RiskScore, HistoricalScore, BatchScoreRequest, BatchScoreResponse
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/scores", tags=["scoring"])


@router.get("/entity/{entity_id}", response_model=RiskScore)
def score_entity(entity_id: int, db: Session = Depends(get_db)):
    """Calculate and return the current risk score for an entity."""
    scoring_engine = ScoringEngine(db)
    
    try:
        score_data = scoring_engine.score_entity(entity_id)
        
        logger.info(
            f"Scored entity {entity_id}: {score_data['score']} ({score_data['grade']})",
            extra={"entity_id": entity_id, "score": score_data['score']}
        )
        
        return score_data
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error scoring entity {entity_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal error calculating score")


@router.get("/entity/{entity_id}/history", response_model=List[HistoricalScore])
def get_entity_score_history(
    entity_id: int,
    limit: int = Query(10, description="Maximum number of historical scores", le=100),
    db: Session = Depends(get_db)
):
    """Get historical risk scores for an entity."""
    from app.domain.graph.models import RiskScore
    from sqlalchemy import desc
    
    # Verify entity exists
    from app.domain.entities.service import EntityService
    entity_service = EntityService(db)
    entity_data = entity_service.get_entity_details(entity_id)
    if not entity_data:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Get historical scores
    historical_scores = db.query(RiskScore).filter(
        RiskScore.entity_id == entity_id
    ).order_by(desc(RiskScore.calculated_at)).limit(limit).all()
    
    return historical_scores


@router.get("/entity/{entity_id}/latest")
def get_latest_entity_score(entity_id: int, db: Session = Depends(get_db)):
    """Get the most recent stored score for an entity (without recalculating)."""
    scoring_engine = ScoringEngine(db)
    
    latest_score = scoring_engine.get_latest_score(entity_id)
    
    if not latest_score:
        raise HTTPException(
            status_code=404, 
            detail="No scores found for this entity. Use POST /scores/entity/{entity_id} to calculate."
        )
    
    return latest_score


@router.post("/batch", response_model=BatchScoreResponse)
def batch_score_entities(request: BatchScoreRequest, db: Session = Depends(get_db)):
    """Score multiple entities in a single request."""
    scoring_engine = ScoringEngine(db)
    
    try:
        results = scoring_engine.batch_score_entities(request.entity_ids)
        
        logger.info(
            f"Batch scored {len(results)} entities out of {len(request.entity_ids)} requested",
            extra={"requested": len(request.entity_ids), "scored": len(results)}
        )
        
        return BatchScoreResponse(
            total_requested=len(request.entity_ids),
            total_scored=len(results),
            scores=results
        )
        
    except Exception as e:
        logger.error(f"Error in batch scoring: {e}")
        raise HTTPException(status_code=500, detail="Error processing batch scoring request")


@router.get("/high-risk")
def get_high_risk_entities(
    grade: str = Query("F", description="Risk grade threshold (A-F)"),
    limit: int = Query(100, description="Maximum number of results", le=1000),
    db: Session = Depends(get_db)
):
    """Get entities with high risk scores."""
    from app.domain.graph.models import RiskScore
    from sqlalchemy import desc, distinct
    
    # Validate grade
    if grade not in ['A', 'B', 'C', 'D', 'F']:
        raise HTTPException(status_code=400, detail="Grade must be A, B, C, D, or F")
    
    # Map grades to score ranges for filtering
    grade_thresholds = {
        'A': 20, 'B': 40, 'C': 60, 'D': 80, 'F': 100
    }
    
    min_score = grade_thresholds.get(grade, 80)
    
    # Get latest scores for entities meeting criteria
    # Using a subquery to get the most recent score per entity
    from sqlalchemy.orm import aliased
    from sqlalchemy import func
    
    subq = db.query(
        RiskScore.entity_id,
        func.max(RiskScore.calculated_at).label('latest_calc')
    ).group_by(RiskScore.entity_id).subquery()
    
    latest_scores = db.query(RiskScore).join(
        subq,
        (RiskScore.entity_id == subq.c.entity_id) &
        (RiskScore.calculated_at == subq.c.latest_calc)
    ).filter(
        RiskScore.score >= min_score
    ).order_by(desc(RiskScore.score)).limit(limit).all()
    
    # Enrich with entity details
    results = []
    for score in latest_scores:
        from app.domain.entities.service import EntityService
        entity_service = EntityService(db)
        entity_data = entity_service.get_entity_details(score.entity_id)
        
        if entity_data:
            results.append({
                "entity": {
                    "id": entity_data["id"],
                    "legal_name": entity_data["legal_name"],
                    "type": entity_data["type"],
                    "jurisdiction": entity_data["jurisdiction"],
                    "status": entity_data["status"]
                },
                "score": float(score.score),
                "grade": score.grade,
                "flags": score.flags,
                "calculated_at": score.calculated_at.isoformat()
            })
    
    logger.info(
        f"Retrieved {len(results)} high-risk entities (grade >= {grade})",
        extra={"grade_threshold": grade, "result_count": len(results)}
    )
    
    return {
        "grade_threshold": grade,
        "total_entities": len(results),
        "entities": results
    }


@router.get("/statistics")
def get_scoring_statistics(db: Session = Depends(get_db)):
    """Get overall scoring statistics across the system."""
    from app.domain.graph.models import RiskScore
    from sqlalchemy import func, distinct
    
    # Total entities scored
    total_scored = db.query(func.count(distinct(RiskScore.entity_id))).scalar()
    
    # Distribution by grade
    grade_distribution = db.query(
        RiskScore.grade,
        func.count(distinct(RiskScore.entity_id))
    ).group_by(RiskScore.grade).all()
    
    # Average score
    avg_score = db.query(func.avg(RiskScore.score)).scalar()
    
    return {
        "total_entities_scored": total_scored,
        "average_score": float(avg_score) if avg_score else None,
        "grade_distribution": {grade: count for grade, count in grade_distribution}
    }