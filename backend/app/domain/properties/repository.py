# Property repository for database operations
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from .models import Property
from app.core.logging import get_logger

logger = get_logger(__name__)


class PropertyRepository:
    """Repository for property-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, property_id: int) -> Optional[Property]:
        """Get property by ID."""
        return self.db.query(Property).filter(Property.id == property_id).first()

    def get_by_parcel_id(self, county: str, parcel_id: str) -> Optional[Property]:
        """Get property by county and parcel ID."""
        return self.db.query(Property).filter(
            and_(
                Property.county == county,
                Property.parcel_id == parcel_id
            )
        ).first()

    def get_by_county(self, county: str, limit: int = 100) -> List[Property]:
        """Get properties by county."""
        return self.db.query(Property).filter(
            Property.county == county
        ).order_by(desc(Property.updated_at)).limit(limit).all()

    def get_by_land_use(self, county: str, land_use_code: str, limit: int = 100) -> List[Property]:
        """Get properties by land use code within a county."""
        return self.db.query(Property).filter(
            and_(
                Property.county == county,
                Property.land_use_code == land_use_code
            )
        ).limit(limit).all()

    def get_by_address(self, address_id: int) -> List[Property]:
        """Get properties at a specific address."""
        return self.db.query(Property).filter(
            Property.situs_address_id == address_id
        ).all()

    def get_recent_sales(
        self,
        county: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 100
    ) -> List[Property]:
        """Get properties with recent sales, optionally filtered by county and price."""
        query = self.db.query(Property).filter(
            Property.last_sale_date.isnot(None)
        )
        
        if county:
            query = query.filter(Property.county == county)
        if min_price:
            query = query.filter(Property.last_sale_price >= min_price)
        if max_price:
            query = query.filter(Property.last_sale_price <= max_price)
        
        return query.order_by(desc(Property.last_sale_date)).limit(limit).all()

    def upsert_property(
        self,
        county: str,
        parcel_id: str,
        defaults: dict
    ) -> Property:
        """Insert or update property based on county and parcel_id."""
        property_obj = self.get_by_parcel_id(county, parcel_id)
        
        if property_obj is None:
            property_obj = Property(
                county=county,
                parcel_id=parcel_id,
                **defaults
            )
            self.db.add(property_obj)
            logger.info(f"Created new property: {county} - {parcel_id}")
        else:
            # Update existing property
            for key, value in defaults.items():
                if hasattr(property_obj, key):
                    setattr(property_obj, key, value)
            logger.info(f"Updated property: {county} - {parcel_id}")
        
        self.db.flush()
        return property_obj

    def search_by_value_range(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        county: Optional[str] = None,
        limit: int = 100
    ) -> List[Property]:
        """Search properties by assessed or market value range."""
        query = self.db.query(Property)
        
        if county:
            query = query.filter(Property.county == county)
        
        if min_value:
            query = query.filter(
                (Property.market_value >= min_value) |
                (Property.assessed_value >= min_value)
            )
        
        if max_value:
            query = query.filter(
                (Property.market_value <= max_value) |
                (Property.assessed_value <= max_value)
            )
        
        return query.order_by(desc(Property.market_value)).limit(limit).all()

    def get_large_parcels(
        self,
        min_acres: float = 10.0,
        county: Optional[str] = None,
        limit: int = 100
    ) -> List[Property]:
        """Get large parcels by acreage."""
        query = self.db.query(Property).filter(
            Property.acreage >= min_acres
        )
        
        if county:
            query = query.filter(Property.county == county)
        
        return query.order_by(desc(Property.acreage)).limit(limit).all()