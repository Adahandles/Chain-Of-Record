#!/usr/bin/env python3
"""
Sample Data Seeding Script for Chain Of Record

This script creates comprehensive sample data to validate the complete data pipeline:
- Entities (LLCs, Corporations, Trusts, Nonprofits)
- People (Registered Agents, Officers, Property Owners)
- Addresses (Business, Residential, Property Situs)
- Properties (Marion County, FL real estate)
- Relationships (Entity->Agent, Entity->Property, etc.)
- Events (Formation, Officer Changes, Deeds, etc.)

The data is designed to trigger various risk scoring patterns.

Usage:
    python scripts/seed_sample_data.py [--clear-all] [--batch-size N]

Options:
    --clear-all     Delete all existing data before seeding
    --batch-size    Number of records to insert per batch (default: 100)
"""

import sys
import os
import argparse
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
import hashlib

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, text
from app.core.db import SessionLocal
from app.domain.entities.models import Entity, Person, Address
from app.domain.properties.models import Property
from app.domain.graph.models import Relationship, Event, RiskScore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_address_hash(line1: str, city: str, state: str, postal_code: str) -> str:
    """Generate normalized hash for address deduplication."""
    normalized = f"{line1.upper().strip()}|{city.upper().strip()}|{state.upper().strip()}|{postal_code[:5]}"
    return hashlib.sha256(normalized.encode()).hexdigest()


def normalize_name(name: str) -> str:
    """Normalize person name for matching."""
    return name.upper().replace(',', '').replace('.', '').strip()


def clear_all_data(db) -> None:
    """Delete all data from all tables."""
    logger.info("Clearing all existing data...")
    
    try:
        # Delete in reverse order of dependencies
        db.execute(text("DELETE FROM risk_scores"))
        db.execute(text("DELETE FROM events"))
        db.execute(text("DELETE FROM relationships"))
        db.execute(text("DELETE FROM properties"))
        db.execute(text("DELETE FROM entities"))
        db.execute(text("DELETE FROM addresses"))
        db.execute(text("DELETE FROM people"))
        
        # Reset sequences
        db.execute(text("ALTER SEQUENCE entities_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE people_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE addresses_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE properties_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE relationships_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE events_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE risk_scores_id_seq RESTART WITH 1"))
        
        db.commit()
        logger.info("All data cleared successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing data: {e}")
        raise


def create_people(db) -> Dict[str, Person]:
    """Create sample people (registered agents, officers, property owners)."""
    logger.info("Creating people...")
    
    people_data = [
        # Registered agents (some representing multiple entities)
        {"full_name": "John Smith", "role": "agent"},
        {"full_name": "Sarah Johnson", "role": "agent"},
        {"full_name": "Corporate Agents Inc", "role": "agent"},  # Shared agent
        {"full_name": "Michael Brown", "role": "agent"},
        
        # Officers/Managers
        {"full_name": "Robert Davis", "role": "officer"},
        {"full_name": "Jennifer Wilson", "role": "officer"},
        {"full_name": "David Martinez", "role": "officer"},
        {"full_name": "Maria Garcia", "role": "officer"},
        
        # Property owners
        {"full_name": "Thomas Anderson", "role": "owner"},
        {"full_name": "Lisa Rodriguez", "role": "owner"},
        {"full_name": "James Taylor", "role": "owner"},
        {"full_name": "Patricia White", "role": "owner"},
    ]
    
    people = {}
    for person_data in people_data:
        person = Person(
            full_name=person_data["full_name"],
            normalized_name=normalize_name(person_data["full_name"])
        )
        db.add(person)
        people[person_data["role"] + "_" + person_data["full_name"].replace(" ", "_").lower()] = person
    
    db.commit()
    logger.info(f"Created {len(people_data)} people")
    
    return people


def create_addresses(db) -> Dict[str, Address]:
    """Create sample addresses (business, residential, property situs)."""
    logger.info("Creating addresses...")
    
    addresses_data = [
        # Business addresses (some shared by multiple entities)
        {"line1": "123 Main Street", "line2": "Suite 100", "city": "Ocala", "state": "FL", "postal_code": "34470", "county": "Marion", "type": "business_shared"},
        {"line1": "456 Commerce Blvd", "line2": None, "city": "Ocala", "state": "FL", "postal_code": "34471", "county": "Marion", "type": "business"},
        {"line1": "789 Enterprise Way", "line2": "Floor 3", "city": "Ocala", "state": "FL", "postal_code": "34472", "county": "Marion", "type": "business_shared"},
        {"line1": "321 Industry Drive", "line2": None, "city": "Silver Springs", "state": "FL", "postal_code": "34488", "county": "Marion", "type": "business"},
        {"line1": "555 Corporate Park", "line2": "Building A", "city": "Ocala", "state": "FL", "postal_code": "34473", "county": "Marion", "type": "business"},
        
        # Residential addresses
        {"line1": "1010 Oak Avenue", "line2": None, "city": "Ocala", "state": "FL", "postal_code": "34470", "county": "Marion", "type": "residential"},
        {"line1": "2020 Pine Street", "line2": "Apt 5B", "city": "Ocala", "state": "FL", "postal_code": "34471", "county": "Marion", "type": "residential"},
        {"line1": "3030 Maple Road", "line2": None, "city": "Dunnellon", "state": "FL", "postal_code": "34432", "county": "Marion", "type": "residential"},
        
        # Property situs addresses
        {"line1": "4040 Ranch Road", "line2": None, "city": "Ocala", "state": "FL", "postal_code": "34482", "county": "Marion", "type": "property"},
        {"line1": "5050 Farm Lane", "line2": None, "city": "Citra", "state": "FL", "postal_code": "32113", "county": "Marion", "type": "property"},
        {"line1": "6060 Pasture Drive", "line2": None, "city": "Anthony", "state": "FL", "postal_code": "32617", "county": "Marion", "type": "property"},
        {"line1": "7070 Acreage Way", "line2": None, "city": "Reddick", "state": "FL", "postal_code": "32686", "county": "Marion", "type": "property"},
        {"line1": "8080 Commercial Street", "line2": None, "city": "Ocala", "state": "FL", "postal_code": "34474", "county": "Marion", "type": "property"},
        {"line1": "9090 Industrial Blvd", "line2": None, "city": "Ocala", "state": "FL", "postal_code": "34475", "county": "Marion", "type": "property"},
        {"line1": "1515 Residential Circle", "line2": None, "city": "Ocala", "state": "FL", "postal_code": "34476", "county": "Marion", "type": "property"},
    ]
    
    addresses = {}
    type_counters = {}
    
    for addr_data in addresses_data:
        address = Address(
            line1=addr_data["line1"],
            line2=addr_data["line2"],
            city=addr_data["city"],
            state=addr_data["state"],
            postal_code=addr_data["postal_code"],
            county=addr_data["county"],
            country="US",
            normalized_hash=normalize_address_hash(
                addr_data["line1"],
                addr_data["city"],
                addr_data["state"],
                addr_data["postal_code"]
            )
        )
        db.add(address)
        
        # Generate unique key with counter
        addr_type = addr_data["type"]
        counter = type_counters.get(addr_type, 0)
        addresses[f"{addr_type}_{counter}"] = address
        type_counters[addr_type] = counter + 1
    
    db.commit()
    logger.info(f"Created {len(addresses_data)} addresses")
    
    return addresses


def create_entities(db, people: Dict[str, Person], addresses: Dict[str, Address]) -> Dict[str, Entity]:
    """Create sample business entities with varied attributes.
    
    Note: people and addresses must be committed to the database before calling this function,
    as we reference their IDs for foreign key relationships.
    """
    logger.info("Creating entities...")
    
    today = date.today()
    
    entities_data = [
        # New LLC (< 90 days) - HIGH RISK: New Entity
        {
            "external_id": "L23001234",
            "source_system": "sunbiz",
            "type": "llc",
            "legal_name": "Rapid Property Holdings LLC",
            "jurisdiction": "FL",
            "status": "ACTIVE",
            "formation_date": today - timedelta(days=45),
            "ein_available": False,
            "ein_verified": False,
            "agent": "agent_corporate_agents_inc",
            "address": "business_shared_0"
        },
        # Medium-age LLC (~1 year)
        {
            "external_id": "L22005678",
            "source_system": "sunbiz",
            "type": "llc",
            "legal_name": "Sunshine Investments LLC",
            "jurisdiction": "FL",
            "status": "ACTIVE",
            "formation_date": today - timedelta(days=365),
            "ein_available": True,
            "ein_verified": True,
            "agent": "agent_john_smith",
            "address": "business_1"
        },
        # Established LLC (> 2 years) - Multi-property owner
        {
            "external_id": "L20009999",
            "source_system": "sunbiz",
            "type": "llc",
            "legal_name": "Triple Crown Properties LLC",
            "jurisdiction": "FL",
            "status": "ACTIVE",
            "formation_date": today - timedelta(days=900),
            "ein_available": True,
            "ein_verified": True,
            "agent": "agent_sarah_johnson",
            "address": "business_2"
        },
        # Corporation (Delaware registered)
        {
            "external_id": "C21001111",
            "source_system": "sunbiz",
            "type": "corp",
            "legal_name": "Marion Real Estate Corp",
            "jurisdiction": "DE",
            "status": "ACTIVE",
            "formation_date": today - timedelta(days=1200),
            "ein_available": True,
            "ein_verified": True,
            "agent": "agent_corporate_agents_inc",
            "address": "business_shared_0"
        },
        # Corporation (Texas)
        {
            "external_id": "C19002222",
            "source_system": "sunbiz",
            "type": "corp",
            "legal_name": "Southern Land Development Corp",
            "jurisdiction": "TX",
            "status": "ACTIVE",
            "formation_date": today - timedelta(days=1800),
            "ein_available": True,
            "ein_verified": False,
            "agent": "agent_michael_brown",
            "address": "business_3"
        },
        # Trust
        {
            "external_id": "T20003333",
            "source_system": "marion_pa",
            "type": "trust",
            "legal_name": "Anderson Family Trust",
            "jurisdiction": "FL",
            "status": "ACTIVE",
            "formation_date": today - timedelta(days=2500),
            "ein_available": True,
            "ein_verified": True,
            "agent": "agent_john_smith",
            "address": "business_4"
        },
        # Nonprofit
        {
            "external_id": "N18004444",
            "source_system": "sunbiz",
            "type": "nonprofit",
            "legal_name": "Marion County Agricultural Foundation",
            "jurisdiction": "FL",
            "status": "ACTIVE",
            "formation_date": today - timedelta(days=2000),
            "ein_available": True,
            "ein_verified": True,
            "agent": "agent_sarah_johnson",
            "address": "business_1"
        },
        # Inactive LLC
        {
            "external_id": "L21005555",
            "source_system": "sunbiz",
            "type": "llc",
            "legal_name": "Dormant Holdings LLC",
            "jurisdiction": "FL",
            "status": "INACTIVE",
            "formation_date": today - timedelta(days=600),
            "ein_available": True,
            "ein_verified": False,
            "agent": "agent_corporate_agents_inc",
            "address": "business_shared_2"
        },
        # Dissolved LLC - STATUS CHANGE risk
        {
            "external_id": "L20006666",
            "source_system": "sunbiz",
            "type": "llc",
            "legal_name": "Dissolved Ventures LLC",
            "jurisdiction": "FL",
            "status": "DISSOLVED",
            "formation_date": today - timedelta(days=1100),
            "ein_available": True,
            "ein_verified": True,
            "agent": "agent_michael_brown",
            "address": "business_shared_2"
        },
        # Another entity at shared address (ADDRESS CONCENTRATION)
        {
            "external_id": "L22007777",
            "source_system": "sunbiz",
            "type": "llc",
            "legal_name": "Shared Space LLC",
            "jurisdiction": "FL",
            "status": "ACTIVE",
            "formation_date": today - timedelta(days=200),
            "ein_available": False,
            "ein_verified": False,
            "agent": "agent_corporate_agents_inc",
            "address": "business_shared_0"
        },
    ]
    
    entities = {}
    for entity_data in entities_data:
        entity = Entity(
            external_id=entity_data["external_id"],
            source_system=entity_data["source_system"],
            type=entity_data["type"],
            legal_name=entity_data["legal_name"],
            jurisdiction=entity_data["jurisdiction"],
            status=entity_data["status"],
            formation_date=entity_data["formation_date"],
            ein_available=entity_data["ein_available"],
            ein_verified=entity_data["ein_verified"],
            registered_agent_id=people[entity_data["agent"]].id,
            primary_address_id=addresses[entity_data["address"]].id
        )
        db.add(entity)
        entities[entity_data["legal_name"].replace(" ", "_").lower()] = entity
    
    db.commit()
    logger.info(f"Created {len(entities_data)} entities")
    
    return entities


def create_properties(db, addresses: Dict[str, Address]) -> Dict[str, Property]:
    """Create sample properties in Marion County, FL.
    
    Note: addresses must be committed to the database before calling this function,
    as we reference their IDs for the situs_address_id foreign key.
    """
    logger.info("Creating properties...")
    
    today = date.today()
    
    properties_data = [
        # Residential properties
        {
            "parcel_id": "10234-001-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_0",
            "land_use_code": "0100",  # Single-family residential
            "acreage": Decimal("0.25"),
            "last_sale_date": today - timedelta(days=500),
            "last_sale_price": Decimal("285000.00"),
            "market_value": Decimal("295000.00"),
            "assessed_value": Decimal("275000.00"),
            "homestead_exempt": "Y",
            "tax_year": "2024"
        },
        {
            "parcel_id": "10234-002-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_1",
            "land_use_code": "0100",
            "acreage": Decimal("0.50"),
            "last_sale_date": today - timedelta(days=1200),
            "last_sale_price": Decimal("195000.00"),
            "market_value": Decimal("245000.00"),
            "assessed_value": Decimal("230000.00"),
            "homestead_exempt": "Y",
            "tax_year": "2024"
        },
        {
            "parcel_id": "10234-003-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_2",
            "land_use_code": "0100",
            "acreage": Decimal("0.33"),
            "last_sale_date": today - timedelta(days=90),  # Recent sale - RAPID TURNOVER
            "last_sale_price": Decimal("320000.00"),
            "market_value": Decimal("325000.00"),
            "assessed_value": Decimal("310000.00"),
            "homestead_exempt": "Y",  # Potential HOMESTEAD FRAUD with multi-property owner
            "tax_year": "2024"
        },
        # Agricultural properties
        {
            "parcel_id": "20456-100-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_3",
            "land_use_code": "0200",  # Agricultural
            "acreage": Decimal("25.00"),
            "last_sale_date": today - timedelta(days=800),
            "last_sale_price": Decimal("450000.00"),
            "market_value": Decimal("475000.00"),
            "assessed_value": Decimal("425000.00"),
            "homestead_exempt": "N",
            "tax_year": "2024"
        },
        {
            "parcel_id": "20456-101-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_4",
            "land_use_code": "0200",
            "acreage": Decimal("50.00"),
            "last_sale_date": None,  # No recent sale
            "last_sale_price": None,
            "market_value": Decimal("625000.00"),
            "assessed_value": Decimal("580000.00"),
            "homestead_exempt": "N",
            "tax_year": "2024"
        },
        # Commercial properties
        {
            "parcel_id": "30789-200-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_5",
            "land_use_code": "0400",  # Commercial
            "acreage": Decimal("2.50"),
            "last_sale_date": today - timedelta(days=300),
            "last_sale_price": Decimal("850000.00"),
            "market_value": Decimal("925000.00"),
            "assessed_value": Decimal("875000.00"),
            "homestead_exempt": "N",
            "tax_year": "2024"
        },
        {
            "parcel_id": "30789-201-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_6",
            "land_use_code": "0400",
            "acreage": Decimal("1.75"),
            "last_sale_date": today - timedelta(days=1500),
            "last_sale_price": Decimal("675000.00"),
            "market_value": Decimal("825000.00"),
            "assessed_value": Decimal("780000.00"),
            "homestead_exempt": "N",
            "tax_year": "2023"
        },
        # Investment properties (for multi-property owner)
        {
            "parcel_id": "40123-300-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_7",
            "land_use_code": "0100",
            "acreage": Decimal("0.40"),
            "last_sale_date": today - timedelta(days=600),
            "last_sale_price": Decimal("175000.00"),
            "market_value": Decimal("195000.00"),
            "assessed_value": Decimal("180000.00"),
            "homestead_exempt": "N",
            "tax_year": "2024"
        },
        {
            "parcel_id": "40123-301-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_8",
            "land_use_code": "0100",
            "acreage": Decimal("0.35"),
            "last_sale_date": today - timedelta(days=700),
            "last_sale_price": Decimal("165000.00"),
            "market_value": Decimal("185000.00"),
            "assessed_value": Decimal("175000.00"),
            "homestead_exempt": "N",
            "tax_year": "2024"
        },
        {
            "parcel_id": "40123-302-000",
            "county": "Marion",
            "jurisdiction": "FL",
            "address": "property_9",
            "land_use_code": "0100",
            "acreage": Decimal("0.45"),
            "last_sale_date": today - timedelta(days=650),
            "last_sale_price": Decimal("185000.00"),
            "market_value": Decimal("205000.00"),
            "assessed_value": Decimal("190000.00"),
            "homestead_exempt": "N",
            "tax_year": "2024"
        },
    ]
    
    properties = {}
    for prop_data in properties_data:
        prop = Property(
            parcel_id=prop_data["parcel_id"],
            county=prop_data["county"],
            jurisdiction=prop_data["jurisdiction"],
            situs_address_id=addresses[prop_data["address"]].id,
            appraiser_url=f"https://www.pa.marion.fl.us/display.asp?parcel={prop_data['parcel_id']}",
            land_use_code=prop_data["land_use_code"],
            acreage=prop_data["acreage"],
            last_sale_date=prop_data["last_sale_date"],
            last_sale_price=prop_data["last_sale_price"],
            market_value=prop_data["market_value"],
            assessed_value=prop_data["assessed_value"],
            homestead_exempt=prop_data["homestead_exempt"],
            tax_year=prop_data["tax_year"]
        )
        db.add(prop)
        properties[prop_data["parcel_id"]] = prop
    
    db.commit()
    logger.info(f"Created {len(properties_data)} properties")
    
    return properties


def create_relationships(
    db,
    entities: Dict[str, Entity],
    people: Dict[str, Person],
    addresses: Dict[str, Address],
    properties: Dict[str, Property]
) -> None:
    """Create relationships between entities, people, addresses, and properties.
    
    Note: All referenced objects must be committed to the database before calling this function,
    as we use their IDs to create relationship records.
    """
    logger.info("Creating relationships...")
    
    today = date.today()
    
    relationships_data = [
        # Entity -> Agent relationships (already captured in entity.registered_agent_id, but also in graph)
        {"from_type": "entity", "from": "rapid_property_holdings_llc", "to_type": "person", "to": "agent_corporate_agents_inc", "rel_type": "agent_for", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "sunshine_investments_llc", "to_type": "person", "to": "agent_john_smith", "rel_type": "agent_for", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "triple_crown_properties_llc", "to_type": "person", "to": "agent_sarah_johnson", "rel_type": "agent_for", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "marion_real_estate_corp", "to_type": "person", "to": "agent_corporate_agents_inc", "rel_type": "agent_for", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "southern_land_development_corp", "to_type": "person", "to": "agent_michael_brown", "rel_type": "agent_for", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "anderson_family_trust", "to_type": "person", "to": "agent_john_smith", "rel_type": "agent_for", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "entity", "from": "marion_county_agricultural_foundation", "to_type": "person", "to": "agent_sarah_johnson", "rel_type": "agent_for", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "dormant_holdings_llc", "to_type": "person", "to": "agent_corporate_agents_inc", "rel_type": "agent_for", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "dissolved_ventures_llc", "to_type": "person", "to": "agent_michael_brown", "rel_type": "agent_for", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "shared_space_llc", "to_type": "person", "to": "agent_corporate_agents_inc", "rel_type": "agent_for", "source": "sunbiz", "confidence": 1.0},
        
        # Entity -> Officer relationships
        {"from_type": "entity", "from": "rapid_property_holdings_llc", "to_type": "person", "to": "officer_robert_davis", "rel_type": "officer", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "sunshine_investments_llc", "to_type": "person", "to": "officer_jennifer_wilson", "rel_type": "officer", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "marion_real_estate_corp", "to_type": "person", "to": "officer_david_martinez", "rel_type": "officer", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "southern_land_development_corp", "to_type": "person", "to": "officer_maria_garcia", "rel_type": "officer", "source": "sunbiz", "confidence": 1.0},
        
        # Entity -> Located At -> Address
        {"from_type": "entity", "from": "rapid_property_holdings_llc", "to_type": "address", "to": "business_shared_0", "rel_type": "located_at", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "marion_real_estate_corp", "to_type": "address", "to": "business_shared_0", "rel_type": "located_at", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "dormant_holdings_llc", "to_type": "address", "to": "business_shared_2", "rel_type": "located_at", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "dissolved_ventures_llc", "to_type": "address", "to": "business_shared_2", "rel_type": "located_at", "source": "sunbiz", "confidence": 1.0},
        {"from_type": "entity", "from": "shared_space_llc", "to_type": "address", "to": "business_shared_0", "rel_type": "located_at", "source": "sunbiz", "confidence": 1.0},
        
        # Entity -> Owns -> Property (HIGH PROPERTY VOLUME for Triple Crown)
        {"from_type": "entity", "from": "triple_crown_properties_llc", "to_type": "property", "to": "10234-001-000", "rel_type": "owns", "source": "marion_pa", "confidence": 0.95, "start_date": today - timedelta(days=500)},
        {"from_type": "entity", "from": "triple_crown_properties_llc", "to_type": "property", "to": "40123-300-000", "rel_type": "owns", "source": "marion_pa", "confidence": 0.95, "start_date": today - timedelta(days=600)},
        {"from_type": "entity", "from": "triple_crown_properties_llc", "to_type": "property", "to": "40123-301-000", "rel_type": "owns", "source": "marion_pa", "confidence": 0.95, "start_date": today - timedelta(days=700)},
        {"from_type": "entity", "from": "triple_crown_properties_llc", "to_type": "property", "to": "40123-302-000", "rel_type": "owns", "source": "marion_pa", "confidence": 0.95, "start_date": today - timedelta(days=650)},
        
        # Other entity property ownership
        {"from_type": "entity", "from": "sunshine_investments_llc", "to_type": "property", "to": "10234-002-000", "rel_type": "owns", "source": "marion_pa", "confidence": 0.90, "start_date": today - timedelta(days=1200)},
        {"from_type": "entity", "from": "rapid_property_holdings_llc", "to_type": "property", "to": "10234-003-000", "rel_type": "owns", "source": "marion_pa", "confidence": 0.92, "start_date": today - timedelta(days=90)},
        {"from_type": "entity", "from": "southern_land_development_corp", "to_type": "property", "to": "20456-100-000", "rel_type": "owns", "source": "marion_pa", "confidence": 0.88, "start_date": today - timedelta(days=800)},
        {"from_type": "entity", "from": "anderson_family_trust", "to_type": "property", "to": "20456-101-000", "rel_type": "owns", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "entity", "from": "marion_real_estate_corp", "to_type": "property", "to": "30789-200-000", "rel_type": "owns", "source": "marion_pa", "confidence": 0.93, "start_date": today - timedelta(days=300)},
        {"from_type": "entity", "from": "marion_county_agricultural_foundation", "to_type": "property", "to": "30789-201-000", "rel_type": "owns", "source": "marion_pa", "confidence": 0.85, "start_date": today - timedelta(days=1500)},
        
        # Property -> Located At -> Address
        {"from_type": "property", "from": "10234-001-000", "to_type": "address", "to": "property_0", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "property", "from": "10234-002-000", "to_type": "address", "to": "property_1", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "property", "from": "10234-003-000", "to_type": "address", "to": "property_2", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "property", "from": "20456-100-000", "to_type": "address", "to": "property_3", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "property", "from": "20456-101-000", "to_type": "address", "to": "property_4", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "property", "from": "30789-200-000", "to_type": "address", "to": "property_5", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "property", "from": "30789-201-000", "to_type": "address", "to": "property_6", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "property", "from": "40123-300-000", "to_type": "address", "to": "property_7", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "property", "from": "40123-301-000", "to_type": "address", "to": "property_8", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
        {"from_type": "property", "from": "40123-302-000", "to_type": "address", "to": "property_9", "rel_type": "located_at", "source": "marion_pa", "confidence": 1.0},
    ]
    
    for rel_data in relationships_data:
        # Get the actual objects
        if rel_data["from_type"] == "entity":
            from_id = entities[rel_data["from"]].id
        elif rel_data["from_type"] == "person":
            from_id = people[rel_data["from"]].id
        elif rel_data["from_type"] == "address":
            from_id = addresses[rel_data["from"]].id
        elif rel_data["from_type"] == "property":
            from_id = properties[rel_data["from"]].id
        
        if rel_data["to_type"] == "entity":
            to_id = entities[rel_data["to"]].id
        elif rel_data["to_type"] == "person":
            to_id = people[rel_data["to"]].id
        elif rel_data["to_type"] == "address":
            to_id = addresses[rel_data["to"]].id
        elif rel_data["to_type"] == "property":
            to_id = properties[rel_data["to"]].id
        
        relationship = Relationship(
            from_type=rel_data["from_type"],
            from_id=from_id,
            to_type=rel_data["to_type"],
            to_id=to_id,
            rel_type=rel_data["rel_type"],
            source_system=rel_data["source"],
            start_date=rel_data.get("start_date"),
            end_date=rel_data.get("end_date"),
            confidence=Decimal(str(rel_data["confidence"]))
        )
        db.add(relationship)
    
    db.commit()
    logger.info(f"Created {len(relationships_data)} relationships")


def create_events(db, entities: Dict[str, Entity]) -> None:
    """Create time-series events for entities."""
    logger.info("Creating events...")
    
    today = date.today()
    
    events_data = [
        # Formation events for all entities
        {"entity": "rapid_property_holdings_llc", "type": "FORMATION", "date": today - timedelta(days=45), "source": "sunbiz", "payload": {"filing_type": "Articles of Organization", "filing_number": "L23001234"}},
        {"entity": "sunshine_investments_llc", "type": "FORMATION", "date": today - timedelta(days=365), "source": "sunbiz", "payload": {"filing_type": "Articles of Organization", "filing_number": "L22005678"}},
        {"entity": "triple_crown_properties_llc", "type": "FORMATION", "date": today - timedelta(days=900), "source": "sunbiz", "payload": {"filing_type": "Articles of Organization", "filing_number": "L20009999"}},
        {"entity": "marion_real_estate_corp", "type": "FORMATION", "date": today - timedelta(days=1200), "source": "sunbiz", "payload": {"filing_type": "Articles of Incorporation", "filing_number": "C21001111", "state_of_incorporation": "Delaware"}},
        {"entity": "southern_land_development_corp", "type": "FORMATION", "date": today - timedelta(days=1800), "source": "sunbiz", "payload": {"filing_type": "Articles of Incorporation", "filing_number": "C19002222", "state_of_incorporation": "Texas"}},
        {"entity": "anderson_family_trust", "type": "FORMATION", "date": today - timedelta(days=2500), "source": "marion_pa", "payload": {"trust_type": "Revocable Living Trust", "trustee": "Thomas Anderson"}},
        {"entity": "marion_county_agricultural_foundation", "type": "FORMATION", "date": today - timedelta(days=2000), "source": "sunbiz", "payload": {"filing_type": "Articles of Incorporation - Nonprofit", "filing_number": "N18004444"}},
        {"entity": "dormant_holdings_llc", "type": "FORMATION", "date": today - timedelta(days=600), "source": "sunbiz", "payload": {"filing_type": "Articles of Organization", "filing_number": "L21005555"}},
        {"entity": "dissolved_ventures_llc", "type": "FORMATION", "date": today - timedelta(days=1100), "source": "sunbiz", "payload": {"filing_type": "Articles of Organization", "filing_number": "L20006666"}},
        {"entity": "shared_space_llc", "type": "FORMATION", "date": today - timedelta(days=200), "source": "sunbiz", "payload": {"filing_type": "Articles of Organization", "filing_number": "L22007777"}},
        
        # Officer change events
        {"entity": "rapid_property_holdings_llc", "type": "OFFICER_CHANGE", "date": today - timedelta(days=30), "source": "sunbiz", "payload": {"change_type": "Manager Appointed", "officer_name": "Robert Davis", "title": "Manager"}},
        {"entity": "marion_real_estate_corp", "type": "OFFICER_CHANGE", "date": today - timedelta(days=180), "source": "sunbiz", "payload": {"change_type": "Director Change", "officer_name": "David Martinez", "title": "Director"}},
        
        # Address change events
        {"entity": "sunshine_investments_llc", "type": "ADDRESS_CHANGE", "date": today - timedelta(days=120), "source": "sunbiz", "payload": {"old_address": "555 Old Street, Ocala, FL 34470", "new_address": "456 Commerce Blvd, Ocala, FL 34471"}},
        
        # Deed transfer events (property sales)
        {"entity": "triple_crown_properties_llc", "type": "DEED_TRANSFER", "date": today - timedelta(days=500), "source": "marion_pa", "payload": {"parcel_id": "10234-001-000", "transfer_type": "Warranty Deed", "consideration": "285000"}},
        {"entity": "triple_crown_properties_llc", "type": "DEED_TRANSFER", "date": today - timedelta(days=600), "source": "marion_pa", "payload": {"parcel_id": "40123-300-000", "transfer_type": "Warranty Deed", "consideration": "175000"}},
        {"entity": "triple_crown_properties_llc", "type": "DEED_TRANSFER", "date": today - timedelta(days=700), "source": "marion_pa", "payload": {"parcel_id": "40123-301-000", "transfer_type": "Warranty Deed", "consideration": "165000"}},
        {"entity": "triple_crown_properties_llc", "type": "DEED_TRANSFER", "date": today - timedelta(days=650), "source": "marion_pa", "payload": {"parcel_id": "40123-302-000", "transfer_type": "Warranty Deed", "consideration": "185000"}},
        {"entity": "rapid_property_holdings_llc", "type": "DEED_TRANSFER", "date": today - timedelta(days=90), "source": "marion_pa", "payload": {"parcel_id": "10234-003-000", "transfer_type": "Warranty Deed", "consideration": "320000"}},
        {"entity": "southern_land_development_corp", "type": "DEED_TRANSFER", "date": today - timedelta(days=800), "source": "marion_pa", "payload": {"parcel_id": "20456-100-000", "transfer_type": "Warranty Deed", "consideration": "450000"}},
        
        # Annual report events
        {"entity": "sunshine_investments_llc", "type": "ANNUAL_REPORT", "date": today - timedelta(days=50), "source": "sunbiz", "payload": {"report_year": "2024", "status": "Filed"}},
        {"entity": "triple_crown_properties_llc", "type": "ANNUAL_REPORT", "date": today - timedelta(days=60), "source": "sunbiz", "payload": {"report_year": "2024", "status": "Filed"}},
        
        # Status change event (dissolution)
        {"entity": "dissolved_ventures_llc", "type": "STATUS_CHANGE", "date": today - timedelta(days=100), "source": "sunbiz", "payload": {"old_status": "ACTIVE", "new_status": "DISSOLVED", "reason": "Administrative Dissolution"}},
    ]
    
    for event_data in events_data:
        event = Event(
            entity_id=entities[event_data["entity"]].id,
            event_type=event_data["type"],
            event_date=event_data["date"],
            source_system=event_data["source"],
            payload=event_data["payload"]
        )
        db.add(event)
    
    db.commit()
    logger.info(f"Created {len(events_data)} events")


def verify_data(db) -> None:
    """Run verification queries to validate the data."""
    logger.info("\n" + "="*80)
    logger.info("DATA VERIFICATION")
    logger.info("="*80)
    
    # Count records
    logger.info("\nRecord Counts:")
    logger.info(f"  Entities: {db.query(Entity).count()}")
    logger.info(f"  People: {db.query(Person).count()}")
    logger.info(f"  Addresses: {db.query(Address).count()}")
    logger.info(f"  Properties: {db.query(Property).count()}")
    logger.info(f"  Relationships: {db.query(Relationship).count()}")
    logger.info(f"  Events: {db.query(Event).count()}")
    logger.info(f"  Risk Scores: {db.query(RiskScore).count()}")
    
    # Sample relationships
    logger.info("\nSample Relationships:")
    sample_rels = db.query(Relationship).limit(5).all()
    for rel in sample_rels:
        logger.info(f"  {rel}")
    
    # Entities that should trigger high-risk scores
    logger.info("\nHigh-Risk Patterns Identified:")
    
    # New entities (< 90 days)
    today = date.today()
    new_entities = db.query(Entity).filter(
        Entity.formation_date >= today - timedelta(days=90)
    ).all()
    logger.info(f"  New Entities (< 90 days): {len(new_entities)}")
    for entity in new_entities:
        logger.info(f"    - {entity.legal_name} (formed {entity.formation_date})")
    
    # High property volume entities (3+ properties)
    high_volume_query = db.query(
        Entity.id,
        Entity.legal_name,
        func.count(Relationship.id).label('property_count')
    ).join(
        Relationship,
        (Relationship.from_type == 'entity') & (Relationship.from_id == Entity.id)
    ).filter(
        Relationship.rel_type == 'owns',
        Relationship.to_type == 'property'
    ).group_by(
        Entity.id, Entity.legal_name
    ).having(
        func.count(Relationship.id) >= 3
    ).all()
    
    logger.info(f"  High Property Volume (3+ properties): {len(high_volume_query)}")
    for entity_id, entity_name, count in high_volume_query:
        logger.info(f"    - {entity_name}: {count} properties")
    
    # Address concentration (3+ entities at same address)
    address_concentration = db.query(
        Address.id,
        Address.line1,
        Address.city,
        func.count(Entity.id).label('entity_count')
    ).join(
        Entity,
        Entity.primary_address_id == Address.id
    ).group_by(
        Address.id, Address.line1, Address.city
    ).having(
        func.count(Entity.id) >= 3
    ).all()
    
    logger.info(f"  Address Concentration (3+ entities): {len(address_concentration)}")
    for addr_id, line1, city, count in address_concentration:
        logger.info(f"    - {line1}, {city}: {count} entities")
    
    # Shared agents (4+ entities)
    shared_agents = db.query(
        Person.id,
        Person.full_name,
        func.count(Entity.id).label('entity_count')
    ).join(
        Entity,
        Entity.registered_agent_id == Person.id
    ).group_by(
        Person.id, Person.full_name
    ).having(
        func.count(Entity.id) >= 4
    ).all()
    
    logger.info(f"  Shared Agents (4+ entities): {len(shared_agents)}")
    for person_id, name, count in shared_agents:
        logger.info(f"    - {name}: {count} entities")
    
    # Graph traversal example
    logger.info("\nGraph Traversal Example:")
    triple_crown = db.query(Entity).filter(Entity.legal_name == "Triple Crown Properties LLC").first()
    if triple_crown:
        logger.info(f"  Properties owned by {triple_crown.legal_name}:")
        property_rels = db.query(Relationship).filter(
            Relationship.from_type == 'entity',
            Relationship.from_id == triple_crown.id,
            Relationship.rel_type == 'owns',
            Relationship.to_type == 'property'
        ).all()
        
        for rel in property_rels:
            prop = db.query(Property).filter(Property.id == rel.to_id).first()
            if prop:
                logger.info(f"    - Parcel {prop.parcel_id}: ${prop.market_value} market value")
    
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION COMPLETE")
    logger.info("="*80 + "\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Seed sample data for Chain Of Record")
    parser.add_argument('--clear-all', action='store_true', help='Delete all existing data before seeding')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of records to insert per batch')
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("CHAIN OF RECORD - SAMPLE DATA SEEDING")
    logger.info("="*80)
    
    db = SessionLocal()
    
    try:
        # Clear data if requested
        if args.clear_all:
            clear_all_data(db)
        
        # Create data
        logger.info("\nCreating sample data...")
        people = create_people(db)
        addresses = create_addresses(db)
        entities = create_entities(db, people, addresses)
        properties = create_properties(db, addresses)
        create_relationships(db, entities, people, addresses, properties)
        create_events(db, entities)
        
        logger.info("\nSample data creation complete!")
        
        # Verify data
        verify_data(db)
        
        logger.info("\n✅ SUCCESS: Sample data seeded successfully")
        logger.info("\nNext steps:")
        logger.info("  1. Run risk scoring: python -m app.domain.scoring.score_all")
        logger.info("  2. Query the API: curl http://localhost:8000/api/v1/entities")
        logger.info("  3. Explore the data in your PostgreSQL client")
        
    except Exception as e:
        db.rollback()
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
