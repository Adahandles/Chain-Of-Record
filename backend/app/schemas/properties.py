# Property schemas for API requests and responses
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from .entities import AddressOut


class PropertyOut(BaseModel):
    """Property output schema."""
    id: int
    parcel_id: str
    county: str
    jurisdiction: Optional[str]
    land_use_code: Optional[str]
    acreage: Optional[float]
    last_sale_date: Optional[date]
    last_sale_price: Optional[float]
    market_value: Optional[float]
    assessed_value: Optional[float]
    homestead_exempt: Optional[str]
    tax_year: Optional[str]
    appraiser_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    situs_address: Optional[AddressOut]

    class Config:
        from_attributes = True


class PropertySearchParams(BaseModel):
    """Property search parameters."""
    county: Optional[str] = None
    land_use_code: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_acres: Optional[float] = None
    limit: int = 50

    @validator('limit')
    def limit_must_be_reasonable(cls, v):
        if v > 1000:
            raise ValueError('Limit cannot exceed 1000')
        return v

    @validator('min_acres', 'min_value', 'max_value')
    def values_must_be_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('Values must be positive')
        return v


class PropertyListItem(BaseModel):
    """Simplified property for list views."""
    id: int
    parcel_id: str
    county: str
    land_use_code: Optional[str]
    acreage: Optional[float]
    last_sale_price: Optional[float]
    market_value: Optional[float]

    class Config:
        from_attributes = True


class PropertyCreate(BaseModel):
    """Property creation schema."""
    parcel_id: str
    county: str
    jurisdiction: Optional[str] = None
    land_use_code: Optional[str] = None
    acreage: Optional[float] = None
    last_sale_date: Optional[date] = None
    last_sale_price: Optional[float] = None
    market_value: Optional[float] = None
    assessed_value: Optional[float] = None
    homestead_exempt: Optional[str] = None
    tax_year: Optional[str] = None
    appraiser_url: Optional[str] = None

    @validator('acreage', 'last_sale_price', 'market_value', 'assessed_value')
    def values_must_be_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('Values must be positive')
        return v


class PropertyStatistics(BaseModel):
    """Property market statistics schema."""
    county: str
    total_properties: int
    avg_sale_price: Optional[float]
    median_sale_price: Optional[float]
    total_sales: int