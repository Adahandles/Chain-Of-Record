# Sunbiz data source implementation
from typing import Iterable, List, Dict, Any, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from .base import IngestSource, RawRecord, NormalizedRecord
from app.domain.entities.service import EntityService
from app.domain.graph.service import GraphService
import re


class SunbizSource(IngestSource):
    """
    Florida Division of Corporations (Sunbiz) data source.
    
    Ingests entity data from Florida business registrations.
    """
    
    def __init__(self):
        super().__init__(
            name="sunbiz",
            description="Florida Division of Corporations business entity records"
        )
    
    def fetch_batch(self, batch_size: int = 100, **kwargs) -> Iterable[RawRecord]:
        """
        Fetch entity records from Sunbiz.
        
        For now, this returns sample data. In production, this would:
        1. Make API calls to Sunbiz search endpoints
        2. Parse HTML responses 
        3. Handle pagination and rate limiting
        4. Support incremental updates based on filing dates
        """
        
        # Sample data representing typical Sunbiz records
        sample_entities = [
            {
                "doc_number": "L21000123456",
                "entity_name": "SUNRISE PROPERTIES LLC",
                "entity_type": "LIMITED LIABILITY COMPANY",
                "status": "ACTIVE",
                "filed_date": "2021-03-15",
                "state": "FL",
                "registered_agent": "JOHN SMITH",
                "registered_agent_address": "123 MAIN ST, MIAMI, FL 33101",
                "principal_address_line1": "456 BUSINESS BLVD",
                "principal_address_line2": "SUITE 200",
                "principal_city": "MIAMI",
                "principal_state": "FL",
                "principal_zip": "33101",
                "annual_report_due": "2024-05-01",
                "last_event_date": "2023-04-01",
                "officers": [
                    {
                        "name": "JANE DOE", 
                        "title": "MANAGER",
                        "address": "789 RESIDENTIAL ST, MIAMI, FL 33102"
                    }
                ]
            },
            {
                "doc_number": "P22000789012",
                "entity_name": "COASTAL DEVELOPMENT CORP",
                "entity_type": "CORPORATION",
                "status": "ACTIVE", 
                "filed_date": "2022-01-10",
                "state": "FL",
                "registered_agent": "CORPORATE SERVICES INC",
                "registered_agent_address": "100 CORPORATE WAY, TALLAHASSEE, FL 32301",
                "principal_address_line1": "2000 OCEAN DRIVE",
                "principal_city": "MIAMI BEACH",
                "principal_state": "FL", 
                "principal_zip": "33139",
                "annual_report_due": "2024-03-01",
                "last_event_date": "2023-06-15",
                "officers": [
                    {
                        "name": "ROBERT WILSON",
                        "title": "PRESIDENT", 
                        "address": "2000 OCEAN DRIVE, MIAMI BEACH, FL 33139"
                    },
                    {
                        "name": "SARAH JOHNSON",
                        "title": "SECRETARY",
                        "address": "2000 OCEAN DRIVE, MIAMI BEACH, FL 33139"
                    }
                ]
            },
            {
                "doc_number": "N23000345678",
                "entity_name": "COMMUNITY HEALTH FOUNDATION INC",
                "entity_type": "NONPROFIT CORPORATION",
                "status": "ACTIVE",
                "filed_date": "2023-06-01",
                "state": "FL",
                "registered_agent": "MARY THOMPSON", 
                "registered_agent_address": "500 CHARITY ST, ORLANDO, FL 32801",
                "principal_address_line1": "500 CHARITY ST",
                "principal_city": "ORLANDO",
                "principal_state": "FL",
                "principal_zip": "32801"
            }
        ]
        
        for i, entity_data in enumerate(sample_entities):
            if i >= batch_size:
                break
            
            self.logger.info(f"Fetching entity: {entity_data['entity_name']}")
            yield RawRecord(entity_data, source_url=f"https://search.sunbiz.org/Inquiry/CorporationSearch/ByDocumentNumber?documentNumber={entity_data['doc_number']}")
    
    def normalize(self, raw: RawRecord) -> List[NormalizedRecord]:
        """
        Normalize Sunbiz data into standardized format.
        
        Creates:
        1. Entity record
        2. Person records for registered agent and officers
        3. Address records
        4. Relationship records
        """
        normalized_records = []
        
        try:
            # Normalize entity
            entity_data = self._normalize_entity(raw)
            normalized_records.append(NormalizedRecord(
                entity_data,
                source_system="sunbiz",
                record_type="entity"
            ))
            
            # Normalize addresses
            if raw.get("principal_address_line1"):
                address_data = self._normalize_address(raw, "principal")
                normalized_records.append(NormalizedRecord(
                    address_data,
                    source_system="sunbiz", 
                    record_type="address"
                ))
            
            # Normalize people (registered agent and officers)
            people_data = self._normalize_people(raw)
            for person_data in people_data:
                normalized_records.append(NormalizedRecord(
                    person_data,
                    source_system="sunbiz",
                    record_type="person"
                ))
            
            # Normalize relationships
            relationships = self._normalize_relationships(raw)
            for rel_data in relationships:
                normalized_records.append(NormalizedRecord(
                    rel_data,
                    source_system="sunbiz",
                    record_type="relationship"
                ))
        
        except Exception as e:
            self.logger.error(f"Error normalizing record {raw.get('doc_number')}: {e}")
            return []
        
        return normalized_records
    
    def persist(self, normalized_records: List[NormalizedRecord], db: Session) -> int:
        """
        Persist normalized Sunbiz records to database.
        """
        entity_service = EntityService(db)
        graph_service = GraphService(db)
        records_persisted = 0
        
        # Separate records by type
        entities = [r for r in normalized_records if r.record_type == "entity"]
        addresses = [r for r in normalized_records if r.record_type == "address"] 
        people = [r for r in normalized_records if r.record_type == "person"]
        relationships = [r for r in normalized_records if r.record_type == "relationship"]
        
        try:
            # Process entities with relationships
            for entity_record in entities:
                # Find related address and agent
                agent_name = None
                address_data = None
                
                # Find agent in people records
                for person in people:
                    if person.get("role") == "agent":
                        agent_name = person.get("full_name")
                        break
                
                # Find primary address
                for addr in addresses:
                    if addr.get("address_type") == "principal":
                        address_data = {k: v for k, v in addr.items() if k != "address_type"}
                        break
                
                # Create entity with relationships
                entity = entity_service.create_entity_with_relationships(
                    entity_data=dict(entity_record),
                    agent_name=agent_name,
                    address_data=address_data
                )
                
                records_persisted += 1
                
                # Create officer relationships
                for person in people:
                    if person.get("role") == "officer":
                        # Create person record
                        person_obj = entity_service.person_repo.upsert_person(person["full_name"])
                        
                        # Create relationship
                        graph_service.create_relationship(
                            from_type="person",
                            from_id=person_obj.id,
                            to_type="entity", 
                            to_id=entity.id,
                            rel_type="officer_of",
                            source_system="sunbiz"
                        )
                        
                        records_persisted += 1
        
        except Exception as e:
            self.logger.error(f"Error persisting Sunbiz records: {e}")
            raise
        
        return records_persisted
    
    def _normalize_entity(self, raw: RawRecord) -> Dict[str, Any]:
        """Normalize entity data."""
        entity_type = self._normalize_entity_type(raw.get("entity_type", ""))
        
        # Parse formation date
        formation_date = None
        if raw.get("filed_date"):
            try:
                formation_date = datetime.strptime(raw["filed_date"], "%Y-%m-%d").date()
            except ValueError:
                pass
        
        return {
            "external_id": raw["doc_number"],
            "type": entity_type,
            "legal_name": raw["entity_name"].strip(),
            "jurisdiction": "FL",
            "status": raw.get("status", "").upper(),
            "formation_date": formation_date,
            "ein_available": False,  # Sunbiz doesn't provide EIN
            "ein_verified": False
        }
    
    def _normalize_address(self, raw: RawRecord, addr_type: str) -> Dict[str, Any]:
        """Normalize address data."""
        prefix = f"{addr_type}_address_" if addr_type != "principal" else "principal_"
        
        return {
            "line1": raw.get(f"{prefix}line1", "").strip(),
            "line2": raw.get(f"{prefix}line2", "").strip() or None,
            "city": raw.get(f"{prefix}city", "").strip() or None,
            "state": raw.get(f"{prefix}state", "").strip() or None,
            "postal_code": raw.get(f"{prefix}zip", "").strip() or None,
            "country": "US",
            "address_type": addr_type
        }
    
    def _normalize_people(self, raw: RawRecord) -> List[Dict[str, Any]]:
        """Normalize people (agent and officers)."""
        people = []
        
        # Registered agent
        if raw.get("registered_agent"):
            people.append({
                "full_name": raw["registered_agent"].strip(),
                "role": "agent"
            })
        
        # Officers
        for officer in raw.get("officers", []):
            people.append({
                "full_name": officer["name"].strip(),
                "role": "officer",
                "title": officer.get("title", "").strip()
            })
        
        return people
    
    def _normalize_relationships(self, raw: RawRecord) -> List[Dict[str, Any]]:
        """Normalize relationships that will be created separately."""
        # These are handled in the persist method
        return []
    
    def _normalize_entity_type(self, entity_type: str) -> str:
        """Normalize entity type to standard values."""
        entity_type = entity_type.upper()
        
        if "LLC" in entity_type or "LIMITED LIABILITY" in entity_type:
            return "llc"
        elif "CORP" in entity_type or "CORPORATION" in entity_type:
            return "corp"
        elif "NONPROFIT" in entity_type or "NON-PROFIT" in entity_type:
            return "nonprofit"
        elif "TRUST" in entity_type:
            return "trust"
        else:
            return "entity"  # Generic fallback
    
    def validate_raw_record(self, raw: RawRecord) -> bool:
        """Validate Sunbiz record."""
        required_fields = ["doc_number", "entity_name"]
        
        for field in required_fields:
            if not raw.get(field):
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate doc number format (basic check)
        doc_number = raw.get("doc_number", "")
        if not re.match(r"^[A-Z]\d{11}$", doc_number):
            self.logger.warning(f"Invalid doc number format: {doc_number}")
            return False
        
        return True