# Scoring schemas for API requests and responses
from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


class RuleDetail(BaseModel):
    """Details about a triggered scoring rule."""
    name: str
    weight: int
    category: str
    description: str


class ScoringContext(BaseModel):
    """Context information used in scoring."""
    property_count: int
    entity_age_days: Optional[int]
    agent_entity_count: int
    address_entity_count: int


class RiskScore(BaseModel):
    """Risk score output schema."""
    entity_id: int
    score: int
    grade: str
    flags: List[str]
    rule_details: List[RuleDetail]
    context: ScoringContext
    calculated_at: Optional[datetime] = None

    @validator('grade')
    def validate_grade(cls, v):
        if v not in ['A', 'B', 'C', 'D', 'F']:
            raise ValueError('Grade must be A, B, C, D, or F')
        return v

    @validator('score')
    def validate_score(cls, v):
        if v < 0:
            raise ValueError('Score must be non-negative')
        return v


class HistoricalScore(BaseModel):
    """Historical risk score without detailed context."""
    entity_id: int
    score: float
    grade: str
    flags: List[str]
    calculated_at: datetime

    class Config:
        from_attributes = True


class BatchScoreRequest(BaseModel):
    """Request schema for batch scoring."""
    entity_ids: List[int]

    @validator('entity_ids')
    def validate_entity_ids(cls, v):
        if len(v) > 100:
            raise ValueError('Cannot score more than 100 entities at once')
        if not v:
            raise ValueError('Must provide at least one entity ID')
        return v


class BatchScoreResponse(BaseModel):
    """Response schema for batch scoring."""
    total_requested: int
    total_scored: int
    scores: List[RiskScore]