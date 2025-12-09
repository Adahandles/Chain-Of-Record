# Pydantic schemas for API requests and responses
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime


class AddressOut(BaseModel):
    """Address output schema."""
    id: int
    line1: str
    line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    county: Optional[str]
    country: str

    class Config:
        from_attributes = True


class PersonOut(BaseModel):
    """Person output schema."""
    id: int
    full_name: str

    class Config:
        from_attributes = True


class EntityOut(BaseModel):
    """Entity output schema."""
    id: int
    external_id: Optional[str]
    source_system: str
    type: str
    legal_name: str
    jurisdiction: Optional[str]
    status: Optional[str]
    formation_date: Optional[date]
    ein_available: Optional[bool]
    ein_verified: Optional[bool]
    created_at: datetime
    updated_at: datetime
    registered_agent: Optional[PersonOut]
    primary_address: Optional[AddressOut]

    class Config:
        from_attributes = True


class EntitySearchParams(BaseModel):
    """Entity search parameters."""
    name: Optional[str] = None
    jurisdiction: Optional[str] = None
    entity_type: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50

    @validator('limit')
    def limit_must_be_reasonable(cls, v):
        if v > 1000:
            raise ValueError('Limit cannot exceed 1000')
        return v


class EntityListItem(BaseModel):
    """Simplified entity for list views."""
    id: int
    legal_name: str
    type: str
    jurisdiction: Optional[str]
    status: Optional[str]
    formation_date: Optional[date]

    class Config:
        from_attributes = True


class EntityCreate(BaseModel):
    """Entity creation schema."""
    external_id: str
    source_system: str
    type: str
    legal_name: str
    jurisdiction: Optional[str]
    status: Optional[str]
    formation_date: Optional[date]
    ein_available: Optional[bool] = None
    ein_verified: Optional[bool] = None

    @validator('type')
    def validate_entity_type(cls, v):
        valid_types = ['llc', 'corp', 'trust', 'nonprofit', 'person']
        if v.lower() not in valid_types:
            raise ValueError(f'Entity type must be one of: {valid_types}')
        return v.lower()


class AddressCreate(BaseModel):
    """Address creation schema."""
    line1: str
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    county: Optional[str] = None
    country: str = 'US'