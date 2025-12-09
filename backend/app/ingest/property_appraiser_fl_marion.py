# Marion County FL Property Appraiser data source
from typing import Iterable, List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from .base import IngestSource, RawRecord, NormalizedRecord
from app.domain.properties.service import PropertyService
from app.domain.graph.service import GraphService
import re


class MarionCountyPropertySource(IngestSource):
    """
    Marion County, FL Property Appraiser data source.
    
    Ingests property records including ownership, valuations, and sales data.
    """
    
    def __init__(self):
        super().__init__(
            name="marion_pa",
            description="Marion County, FL Property Appraiser records"
        )
    
    def fetch_batch(self, batch_size: int = 100, **kwargs) -> Iterable[RawRecord]:
        """
        Fetch property records from Marion County Property Appraiser.
        
        In production, this would:
        1. Connect to county database or API
        2. Parse GIS/parcel data files
        3. Handle bulk downloads and updates
        4. Support geographic filtering
        """
        
        # Sample property data representing Marion County records
        sample_properties = [
            {
                "parcel_id": "15-11-20-0000-00100-0000",
                "owner_name": "SUNRISE PROPERTIES LLC",
                "owner_address1": "456 BUSINESS BLVD STE 200",
                "owner_address2": "",
                "owner_city": "MIAMI",
                "owner_state": "FL",
                "owner_zip": "33101",
                "situs_address": "1234 RANCH RD",
                "situs_city": "OCALA",
                "situs_state": "FL",
                "situs_zip": "34471",
                "legal_description": "LOT 1 SUNSET ACRES SUBDIVISION",
                "land_use_code": "0100",  # Single family residential
                "land_use_description": "SINGLE FAMILY",
                "acreage": "2.50",
                "square_footage": "2400",
                "year_built": "2019",
                "bedrooms": "4",
                "bathrooms": "3",
                "last_sale_date": "2021-06-15",
                "last_sale_price": "485000",
                "deed_book": "3456",
                "deed_page": "789",
                "assessed_value": "465000",
                "market_value": "485000",
                "tax_year": "2023",
                "homestead_exemption": "Y",
                "exemption_amount": "50000"
            },
            {
                "parcel_id": "16-12-21-0000-00200-0000", 
                "owner_name": "COASTAL DEVELOPMENT CORP",
                "owner_address1": "2000 OCEAN DRIVE",
                "owner_city": "MIAMI BEACH", 
                "owner_state": "FL",
                "owner_zip": "33139",
                "situs_address": "5678 COMMERCIAL BLVD",
                "situs_city": "OCALA",
                "situs_state": "FL",
                "situs_zip": "34474",
                "legal_description": "LOTS 5-10 COMMERCE PARK PUD",
                "land_use_code": "0400",  # Commercial
                "land_use_description": "RETAIL COMMERCIAL",
                "acreage": "5.75",
                "square_footage": "12000", 
                "year_built": "2020",
                "last_sale_date": "2022-03-10",
                "last_sale_price": "1250000",
                "deed_book": "3567",
                "deed_page": "123",
                "assessed_value": "1200000",
                "market_value": "1250000",
                "tax_year": "2023",
                "homestead_exemption": "N"
            },
            {
                "parcel_id": "17-13-22-0000-00300-0000",
                "owner_name": "SMITH, JOHN & MARY", 
                "owner_address1": "9999 HOMEOWNER ST",
                "owner_city": "OCALA",
                "owner_state": "FL", 
                "owner_zip": "34471",
                "situs_address": "9999 HOMEOWNER ST",
                "situs_city": "OCALA",
                "situs_state": "FL",
                "situs_zip": "34471", 
                "legal_description": "LOT 15 RESIDENTIAL ESTATES",
                "land_use_code": "0100",
                "land_use_description": "SINGLE FAMILY",
                "acreage": "1.25",
                "square_footage": "1800",
                "year_built": "2018",
                "bedrooms": "3",
                "bathrooms": "2",
                "last_sale_date": "2018-09-20",
                "last_sale_price": "285000",
                "assessed_value": "295000",
                "market_value": "315000",
                "tax_year": "2023",
                "homestead_exemption": "Y",
                "exemption_amount": "50000"
            }
        ]
        
        for i, property_data in enumerate(sample_properties):
            if i >= batch_size:
                break
                
            self.logger.info(f"Fetching property: {property_data['parcel_id']}")
            yield RawRecord(
                property_data,
                source_url=f"https://www.pa.marion.fl.us/search?parcel={property_data['parcel_id']}"
            )
    
    def normalize(self, raw: RawRecord) -> List[NormalizedRecord]:
        """
        Normalize Marion County property data.
        
        Creates:
        1. Property record
        2. Address records (situs and owner)
        3. Owner entity/person records  
        4. Ownership relationships
        """
        normalized_records = []
        
        try:
            # Normalize property
            property_data = self._normalize_property(raw)
            normalized_records.append(NormalizedRecord(
                property_data,
                source_system="marion_pa",
                record_type="property"
            ))
            
            # Normalize situs address
            if raw.get("situs_address"):
                situs_data = self._normalize_situs_address(raw)
                normalized_records.append(NormalizedRecord(
                    situs_data,
                    source_system="marion_pa",
                    record_type="address"
                ))
            
            # Normalize owner address (if different from situs)
            if raw.get("owner_address1"):
                owner_address_data = self._normalize_owner_address(raw)
                normalized_records.append(NormalizedRecord(
                    owner_address_data,
                    source_system="marion_pa", 
                    record_type="address"
                ))
            
            # Normalize owner
            owner_data = self._normalize_owner(raw)
            if owner_data:
                normalized_records.append(NormalizedRecord(
                    owner_data,
                    source_system="marion_pa",
                    record_type="owner"
                ))
            
            # Create ownership relationship
            ownership_data = self._normalize_ownership(raw)
            if ownership_data:
                normalized_records.append(NormalizedRecord(
                    ownership_data,
                    source_system="marion_pa",
                    record_type="relationship"
                ))
        
        except Exception as e:
            self.logger.error(f"Error normalizing property {raw.get('parcel_id')}: {e}")
            return []
        
        return normalized_records
    
    def persist(self, normalized_records: List[NormalizedRecord], db: Session) -> int:
        """
        Persist normalized property records to database.
        """
        property_service = PropertyService(db)
        graph_service = GraphService(db)
        records_persisted = 0
        
        # Separate records by type
        properties = [r for r in normalized_records if r.record_type == "property"]
        addresses = [r for r in normalized_records if r.record_type == "address"]
        owners = [r for r in normalized_records if r.record_type == "owner"]
        relationships = [r for r in normalized_records if r.record_type == "relationship"]
        
        try:
            for property_record in properties:
                # Find related situs address
                situs_data = None
                for addr in addresses:
                    if addr.get("address_type") == "situs":
                        situs_data = {k: v for k, v in addr.items() if k != "address_type"}
                        break
                
                # Create property with address
                property_obj = property_service.create_property_with_address(
                    property_data=dict(property_record),
                    address_data=situs_data
                )
                
                records_persisted += 1
                
                # Handle ownership relationships
                for owner_record in owners:
                    if owner_record.get("owner_type") == "entity":
                        # Look up entity by name (approximate matching)
                        from app.domain.entities.service import EntityService
                        entity_service = EntityService(db)
                        
                        # Try to find matching entity
                        entities = entity_service.search_entities(
                            name=owner_record["legal_name"],
                            limit=5
                        )
                        
                        if entities:
                            # Use first match - in production you'd want better matching logic
                            entity_id = entities[0]["id"]
                            
                            # Create ownership relationship
                            graph_service.create_relationship(
                                from_type="entity",
                                from_id=entity_id,
                                to_type="property",
                                to_id=property_obj.id,
                                rel_type="owns",
                                source_system="marion_pa",
                                confidence=0.8  # Lower confidence for name-based matching
                            )
                            
                            records_persisted += 1
                    
                    elif owner_record.get("owner_type") == "person":
                        # Create or find person
                        from app.domain.entities.service import EntityService
                        entity_service = EntityService(db)
                        
                        person = entity_service.person_repo.upsert_person(owner_record["full_name"])
                        
                        # Create ownership relationship  
                        graph_service.create_relationship(
                            from_type="person",
                            from_id=person.id,
                            to_type="property",
                            to_id=property_obj.id,
                            rel_type="owns",
                            source_system="marion_pa"
                        )
                        
                        records_persisted += 1
        
        except Exception as e:
            self.logger.error(f"Error persisting property records: {e}")
            raise
        
        return records_persisted
    
    def _normalize_property(self, raw: RawRecord) -> Dict[str, Any]:
        """Normalize property data."""
        
        # Parse numeric fields
        acreage = self._parse_decimal(raw.get("acreage"))
        last_sale_price = self._parse_decimal(raw.get("last_sale_price"))
        assessed_value = self._parse_decimal(raw.get("assessed_value"))
        market_value = self._parse_decimal(raw.get("market_value"))
        
        # Parse sale date
        last_sale_date = None
        if raw.get("last_sale_date"):
            try:
                last_sale_date = datetime.strptime(raw["last_sale_date"], "%Y-%m-%d").date()
            except ValueError:
                pass
        
        return {
            "parcel_id": raw["parcel_id"],
            "county": "Marion",
            "jurisdiction": "FL",
            "land_use_code": raw.get("land_use_code"),
            "acreage": float(acreage) if acreage else None,
            "last_sale_date": last_sale_date,
            "last_sale_price": float(last_sale_price) if last_sale_price else None,
            "assessed_value": float(assessed_value) if assessed_value else None,
            "market_value": float(market_value) if market_value else None,
            "homestead_exempt": raw.get("homestead_exemption", "N"),
            "tax_year": raw.get("tax_year"),
            "appraiser_url": f"https://www.pa.marion.fl.us/search?parcel={raw['parcel_id']}"
        }
    
    def _normalize_situs_address(self, raw: RawRecord) -> Dict[str, Any]:
        """Normalize situs (property location) address."""
        return {
            "line1": raw.get("situs_address", "").strip(),
            "city": raw.get("situs_city", "").strip() or None,
            "state": raw.get("situs_state", "").strip() or None,
            "postal_code": raw.get("situs_zip", "").strip() or None,
            "county": "Marion",
            "country": "US",
            "address_type": "situs"
        }
    
    def _normalize_owner_address(self, raw: RawRecord) -> Dict[str, Any]:
        """Normalize owner mailing address."""
        return {
            "line1": raw.get("owner_address1", "").strip(),
            "line2": raw.get("owner_address2", "").strip() or None,
            "city": raw.get("owner_city", "").strip() or None,
            "state": raw.get("owner_state", "").strip() or None,
            "postal_code": raw.get("owner_zip", "").strip() or None,
            "country": "US",
            "address_type": "owner"
        }
    
    def _normalize_owner(self, raw: RawRecord) -> Optional[Dict[str, Any]]:
        """Normalize property owner (entity or person)."""
        owner_name = raw.get("owner_name", "").strip()
        if not owner_name:
            return None
        
        # Detect if owner is likely a business entity or person
        entity_indicators = ["LLC", "CORP", "INC", "LTD", "LP", "COMPANY", "CORPORATION", "TRUST"]
        
        is_entity = any(indicator in owner_name.upper() for indicator in entity_indicators)
        
        if is_entity:
            return {
                "legal_name": owner_name,
                "owner_type": "entity"
            }
        else:
            return {
                "full_name": owner_name,
                "owner_type": "person"
            }
    
    def _normalize_ownership(self, raw: RawRecord) -> Optional[Dict[str, Any]]:
        """Normalize ownership relationship data."""
        # This is handled in the persist method through graph service
        return None
    
    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        """Parse a decimal value from string or number."""
        if not value:
            return None
        
        try:
            # Remove common formatting
            if isinstance(value, str):
                value = value.replace(",", "").replace("$", "").strip()
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None
    
    def validate_raw_record(self, raw: RawRecord) -> bool:
        """Validate property record."""
        required_fields = ["parcel_id", "owner_name"]
        
        for field in required_fields:
            if not raw.get(field):
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate parcel ID format (basic check for Marion County)
        parcel_id = raw.get("parcel_id", "")
        if not re.match(r"^\d{2}-\d{2}-\d{2}-\d{4}-\d{5}-\d{4}$", parcel_id):
            self.logger.warning(f"Invalid parcel ID format: {parcel_id}")
            return False
        
        return True