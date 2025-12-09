# Property service layer for business logic
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from .repository import PropertyRepository
from .models import Property
from app.domain.entities.repository import AddressRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class PropertyService:
    """Service layer for property-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.property_repo = PropertyRepository(db)
        self.address_repo = AddressRepository(db)

    def get_property_details(self, property_id: int) -> Optional[Dict[str, Any]]:
        """Get comprehensive property details."""
        property_obj = self.property_repo.get_by_id(property_id)
        if not property_obj:
            return None

        result = {
            "id": property_obj.id,
            "parcel_id": property_obj.parcel_id,
            "county": property_obj.county,
            "jurisdiction": property_obj.jurisdiction,
            "land_use_code": property_obj.land_use_code,
            "acreage": float(property_obj.acreage) if property_obj.acreage else None,
            "last_sale_date": property_obj.last_sale_date.isoformat() if property_obj.last_sale_date else None,
            "last_sale_price": float(property_obj.last_sale_price) if property_obj.last_sale_price else None,
            "market_value": float(property_obj.market_value) if property_obj.market_value else None,
            "assessed_value": float(property_obj.assessed_value) if property_obj.assessed_value else None,
            "homestead_exempt": property_obj.homestead_exempt,
            "tax_year": property_obj.tax_year,
            "appraiser_url": property_obj.appraiser_url,
            "created_at": property_obj.created_at.isoformat(),
            "updated_at": property_obj.updated_at.isoformat(),
        }

        # Add situs address if available
        if property_obj.situs_address_id:
            address = self.address_repo.get_by_id(property_obj.situs_address_id)
            if address:
                result["situs_address"] = {
                    "id": address.id,
                    "line1": address.line1,
                    "line2": address.line2,
                    "city": address.city,
                    "state": address.state,
                    "postal_code": address.postal_code,
                    "county": address.county,
                    "country": address.country
                }

        return result

    def search_properties(
        self,
        county: Optional[str] = None,
        land_use_code: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        min_acres: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search properties with various filters."""
        
        if min_acres:
            properties = self.property_repo.get_large_parcels(min_acres, county, limit)
        elif min_value or max_value:
            properties = self.property_repo.search_by_value_range(min_value, max_value, county, limit)
        elif county and land_use_code:
            properties = self.property_repo.get_by_land_use(county, land_use_code, limit)
        elif county:
            properties = self.property_repo.get_by_county(county, limit)
        else:
            # Default to recent sales
            properties = self.property_repo.get_recent_sales(county, limit=limit)

        return [
            {
                "id": prop.id,
                "parcel_id": prop.parcel_id,
                "county": prop.county,
                "land_use_code": prop.land_use_code,
                "acreage": float(prop.acreage) if prop.acreage else None,
                "last_sale_price": float(prop.last_sale_price) if prop.last_sale_price else None,
                "market_value": float(prop.market_value) if prop.market_value else None,
            }
            for prop in properties
        ]

    def create_property_with_address(
        self,
        property_data: Dict[str, Any],
        address_data: Optional[Dict[str, Any]] = None
    ) -> Property:
        """Create property with optional situs address."""
        
        # Handle situs address
        address_id = None
        if address_data:
            address = self.address_repo.upsert_address(**address_data)
            address_id = address.id

        # Prepare property data with address
        property_defaults = property_data.copy()
        property_defaults["situs_address_id"] = address_id

        # Remove county and parcel_id from defaults (they're used as keys)
        county = property_defaults.pop("county")
        parcel_id = property_defaults.pop("parcel_id")

        # Create/update property
        property_obj = self.property_repo.upsert_property(
            county=county,
            parcel_id=parcel_id,
            defaults=property_defaults
        )

        self.db.commit()
        
        logger.info(
            f"Created/updated property with address",
            extra={
                "property_id": property_obj.id,
                "county": county,
                "parcel_id": parcel_id,
                "has_address": address_id is not None
            }
        )

        return property_obj

    def get_property_market_statistics(self, county: str) -> Dict[str, Any]:
        """Get basic market statistics for a county."""
        recent_sales = self.property_repo.get_recent_sales(county=county, limit=1000)
        
        if not recent_sales:
            return {
                "county": county,
                "total_properties": 0,
                "avg_sale_price": None,
                "median_sale_price": None,
                "total_sales": 0
            }

        sale_prices = [float(prop.last_sale_price) for prop in recent_sales if prop.last_sale_price]
        
        if not sale_prices:
            return {
                "county": county,
                "total_properties": len(recent_sales),
                "avg_sale_price": None,
                "median_sale_price": None,
                "total_sales": 0
            }

        sale_prices.sort()
        median_price = sale_prices[len(sale_prices) // 2]
        avg_price = sum(sale_prices) / len(sale_prices)

        return {
            "county": county,
            "total_properties": len(recent_sales),
            "avg_sale_price": round(avg_price, 2),
            "median_sale_price": round(median_price, 2),
            "total_sales": len(sale_prices)
        }