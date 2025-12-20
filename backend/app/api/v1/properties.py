# Property API endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.domain.properties.service import PropertyService
from app.schemas.properties import (
    PropertyOut, PropertyListItem, PropertySearchParams,
    PropertyCreate, PropertyStatistics
)
from app.schemas.entities import AddressCreate
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("/{property_id}", response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific property."""
    service = PropertyService(db)
    property_data = service.get_property_details(property_id)
    
    if not property_data:
        raise HTTPException(status_code=404, detail="Property not found")
    
    logger.info(f"Retrieved property details", extra={"property_id": property_id})
    return property_data


@router.get("/", response_model=List[PropertyListItem])
def search_properties(
    county: Optional[str] = Query(None, description="Filter by county"),
    land_use_code: Optional[str] = Query(None, description="Filter by land use code"),
    min_value: Optional[float] = Query(None, description="Minimum property value"),
    max_value: Optional[float] = Query(None, description="Maximum property value"),
    min_acres: Optional[float] = Query(None, description="Minimum acreage"),
    limit: int = Query(50, description="Maximum number of results", le=1000),
    db: Session = Depends(get_db)
):
    """Search properties with various filters."""
    service = PropertyService(db)
    
    properties = service.search_properties(
        county=county,
        land_use_code=land_use_code,
        min_value=min_value,
        max_value=max_value,
        min_acres=min_acres,
        limit=limit
    )
    
    logger.info(
        f"Property search returned {len(properties)} results",
        extra={"county": county, "min_acres": min_acres}
    )
    
    return properties


@router.post("/", response_model=PropertyOut)
def create_property(
    property_data: PropertyCreate,
    address_data: Optional[AddressCreate] = None,
    db: Session = Depends(get_db)
):
    """Create a new property with optional situs address."""
    service = PropertyService(db)
    
    # Convert Pydantic models to dicts
    property_dict = property_data.dict()
    address_dict = address_data.dict() if address_data else None
    
    try:
        property_obj = service.create_property_with_address(
            property_data=property_dict,
            address_data=address_dict
        )
        
        # Return detailed property data
        property_details = service.get_property_details(property_obj.id)
        
        logger.info(
            f"Created new property: {property_obj.county} - {property_obj.parcel_id}",
            extra={"property_id": property_obj.id, "county": property_obj.county}
        )
        
        return property_details
        
    except Exception as e:
        logger.error(f"Error creating property: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{property_id}/owners")
def get_property_owners(property_id: int, db: Session = Depends(get_db)):
    """Get ownership information for a property."""
    from app.domain.graph.service import GraphService
    
    # Verify property exists
    service = PropertyService(db)
    property_data = service.get_property_details(property_id)
    if not property_data:
        raise HTTPException(status_code=404, detail="Property not found")
    
    graph_service = GraphService(db)
    
    # Get incoming "owns" relationships
    ownership_relationships = graph_service.get_incoming_relationships(
        node_type="property",
        node_id=property_id,
        rel_type="owns"
    )
    
    owners = []
    for rel in ownership_relationships:
        owner_info = {
            "type": rel.from_type,
            "id": rel.from_id,
            "relationship_id": rel.id,
            "source_system": rel.source_system,
            "start_date": rel.start_date.isoformat() if rel.start_date else None,
            "end_date": rel.end_date.isoformat() if rel.end_date else None,
            "confidence": float(rel.confidence) if rel.confidence else None,
        }
        
        # Get owner details based on type
        if rel.from_type == "entity":
            from app.domain.entities.service import EntityService
            entity_service = EntityService(db)
            entity_details = entity_service.get_entity_details(rel.from_id)
            if entity_details:
                owner_info["name"] = entity_details["legal_name"]
                owner_info["details"] = entity_details
        elif rel.from_type == "person":
            from app.domain.entities.repository import PersonRepository
            person_repo = PersonRepository(db)
            person = person_repo.get_by_id(rel.from_id)
            if person:
                owner_info["name"] = person.full_name
                owner_info["details"] = {"full_name": person.full_name}
        
        owners.append(owner_info)
    
    return {
        "property_id": property_id,
        "total_owners": len(owners),
        "owners": owners
    }


@router.get("/stats/{county}", response_model=PropertyStatistics)
def get_county_statistics(county: str, db: Session = Depends(get_db)):
    """Get market statistics for a specific county."""
    service = PropertyService(db)
    
    stats = service.get_property_market_statistics(county)
    
    logger.info(
        f"Retrieved statistics for {county}",
        extra={"county": county, "total_properties": stats["total_properties"]}
    )
    
    return stats


@router.get("/recent-sales/")
def get_recent_sales(
    county: Optional[str] = Query(None, description="Filter by county"),
    min_price: Optional[float] = Query(None, description="Minimum sale price"),
    max_price: Optional[float] = Query(None, description="Maximum sale price"),
    limit: int = Query(50, description="Maximum number of results", le=500),
    db: Session = Depends(get_db)
):
    """Get recent property sales with optional filters."""
    from app.domain.properties.repository import PropertyRepository
    
    property_repo = PropertyRepository(db)
    
    recent_sales = property_repo.get_recent_sales(
        county=county,
        min_price=min_price,
        max_price=max_price,
        limit=limit
    )
    
    sales_data = [
        {
            "id": prop.id,
            "parcel_id": prop.parcel_id,
            "county": prop.county,
            "last_sale_date": prop.last_sale_date.isoformat() if prop.last_sale_date else None,
            "last_sale_price": float(prop.last_sale_price) if prop.last_sale_price else None,
            "acreage": float(prop.acreage) if prop.acreage else None,
            "land_use_code": prop.land_use_code
        }
        for prop in recent_sales
    ]
    
    logger.info(
        f"Retrieved {len(recent_sales)} recent sales",
        extra={"county": county, "limit": limit}
    )
    
    return {
        "total_sales": len(sales_data),
        "county": county,
        "sales": sales_data
    }