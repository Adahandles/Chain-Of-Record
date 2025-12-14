#!/usr/bin/env python3
"""
Advanced Data Seeding Script for Chain Of Record

This script adds realistic test entities with varied characteristics:
- Acme Holdings LLC (TX-LLC-001, Grade A, low risk ~25)
- Summit Real Estate Corporation (TX-CORP-002, Grade B, medium risk ~42)
- Riverside Property Management LLC (TX-LLC-003, Grade D, high risk ~68)

Each entity includes:
- Unique address
- Registered agent (person)
- Commercial property with realistic acreage and market values
- Ownership relationship
- Risk score with appropriate flags

Usage:
    python scripts/seed_data.py

Environment Variables:
    DATABASE_URL - PostgreSQL connection string (default: postgresql://chain:chain@localhost:5432/chain)
"""

import sys
import os
import logging
import random
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get database URL from environment or use default."""
    return os.getenv('DATABASE_URL', 'postgresql://chain:chain@localhost:5432/chain')


def seed_entity_with_data(conn, entity_data: Dict[str, Any]) -> None:
    """
    Seed a complete entity with all related data.
    
    Args:
        conn: SQLAlchemy connection
        entity_data: Dictionary containing all entity information
    """
    entity_name = entity_data['legal_name']
    logger.info(f"\n{'='*60}")
    logger.info(f"Creating entity: {entity_name}")
    logger.info(f"{'='*60}")
    
    # 1. Create address for entity
    logger.info(f"  → Creating address: {entity_data['address']['line1']}")
    
    # Check if address already exists
    result = conn.execute(text("""
        SELECT id FROM addresses WHERE line1 = :line1 AND city = :city AND state = :state
    """), {
        'line1': entity_data['address']['line1'],
        'city': entity_data['address']['city'],
        'state': entity_data['address']['state']
    })
    existing = result.fetchone()
    
    if existing:
        address_id = existing[0]
        logger.info(f"     Address already exists with ID: {address_id}")
    else:
        conn.execute(text("""
            INSERT INTO addresses (line1, line2, city, state, postal_code, county, country, normalized_hash)
            VALUES (:line1, :line2, :city, :state, :postal_code, :county, 'US', :normalized_hash)
        """), entity_data['address'])
        
        # Get address ID
        result = conn.execute(text("""
            SELECT id FROM addresses WHERE line1 = :line1 AND city = :city AND state = :state
        """), {
            'line1': entity_data['address']['line1'],
            'city': entity_data['address']['city'],
            'state': entity_data['address']['state']
        })
        address_id = result.fetchone()[0]
        logger.info(f"     Address ID: {address_id}")
    
    # 2. Create registered agent
    logger.info(f"  → Creating registered agent: {entity_data['agent']['full_name']}")
    
    # Check if person already exists
    result = conn.execute(text("""
        SELECT id FROM people WHERE full_name = :full_name
    """), {'full_name': entity_data['agent']['full_name']})
    existing = result.fetchone()
    
    if existing:
        person_id = existing[0]
        logger.info(f"     Agent already exists with ID: {person_id}")
    else:
        conn.execute(text("""
            INSERT INTO people (full_name, normalized_name)
            VALUES (:full_name, :normalized_name)
        """), entity_data['agent'])
        
        # Get person ID
        result = conn.execute(text("""
            SELECT id FROM people WHERE full_name = :full_name
        """), {'full_name': entity_data['agent']['full_name']})
        person_id = result.fetchone()[0]
        logger.info(f"     Agent ID: {person_id}")
    
    # 3. Create entity
    logger.info(f"  → Creating entity: {entity_name}")
    
    # Check if entity already exists
    result = conn.execute(text("""
        SELECT id FROM entities WHERE external_id = :external_id
    """), {'external_id': entity_data['external_id']})
    existing = result.fetchone()
    
    if existing:
        entity_id = existing[0]
        logger.info(f"     Entity already exists with ID: {entity_id}")
    else:
        entity_params = {
            'external_id': entity_data['external_id'],
            'source_system': entity_data['source_system'],
            'type': entity_data['type'],
            'legal_name': entity_name,
            'jurisdiction': entity_data['jurisdiction'],
            'status': entity_data['status'],
            'formation_date': entity_data['formation_date'],
            'ein_available': entity_data['ein_available'],
            'ein_verified': entity_data['ein_verified'],
            'agent_id': person_id,
            'address_id': address_id
        }
        
        conn.execute(text("""
            INSERT INTO entities (
                external_id, source_system, type, legal_name, jurisdiction, status,
                formation_date, ein_available, ein_verified, registered_agent_id, primary_address_id
            )
            VALUES (
                :external_id, :source_system, :type, :legal_name, :jurisdiction, :status,
                :formation_date, :ein_available, :ein_verified, :agent_id, :address_id
            )
        """), entity_params)
        
        # Get entity ID
        result = conn.execute(text("""
            SELECT id FROM entities WHERE external_id = :external_id
        """), {'external_id': entity_data['external_id']})
        entity_id = result.fetchone()[0]
        logger.info(f"     Entity ID: {entity_id}")
    
    # 4. Create property situs address
    logger.info(f"  → Creating property address: {entity_data['property_address']['line1']}")
    
    # Check if property address already exists
    result = conn.execute(text("""
        SELECT id FROM addresses WHERE line1 = :line1 AND city = :city AND state = :state
    """), {
        'line1': entity_data['property_address']['line1'],
        'city': entity_data['property_address']['city'],
        'state': entity_data['property_address']['state']
    })
    existing = result.fetchone()
    
    if existing:
        property_address_id = existing[0]
        logger.info(f"     Property address already exists with ID: {property_address_id}")
    else:
        conn.execute(text("""
            INSERT INTO addresses (line1, city, state, postal_code, county, country, normalized_hash)
            VALUES (:line1, :city, :state, :postal_code, :county, 'US', :normalized_hash)
        """), entity_data['property_address'])
        
        # Get property address ID
        result = conn.execute(text("""
            SELECT id FROM addresses WHERE line1 = :line1 AND city = :city AND state = :state
        """), {
            'line1': entity_data['property_address']['line1'],
            'city': entity_data['property_address']['city'],
            'state': entity_data['property_address']['state']
        })
        property_address_id = result.fetchone()[0]
        logger.info(f"     Property Address ID: {property_address_id}")
    
    # 5. Create property
    logger.info(f"  → Creating property: {entity_data['property']['parcel_id']}")
    
    # Check if property already exists
    result = conn.execute(text("""
        SELECT id FROM properties WHERE parcel_id = :parcel_id
    """), {'parcel_id': entity_data['property']['parcel_id']})
    existing = result.fetchone()
    
    if existing:
        property_id = existing[0]
        logger.info(f"     Property already exists with ID: {property_id}")
    else:
        property_params = {
            'parcel_id': entity_data['property']['parcel_id'],
            'county': entity_data['property']['county'],
            'jurisdiction': entity_data['property']['jurisdiction'],
            'situs_address_id': property_address_id,
            'land_use_code': entity_data['property']['land_use_code'],
            'acreage': entity_data['property']['acreage'],
            'last_sale_date': entity_data['property'].get('last_sale_date'),
            'last_sale_price': entity_data['property'].get('last_sale_price'),
            'market_value': entity_data['property']['market_value'],
            'assessed_value': entity_data['property']['assessed_value'],
            'homestead_exempt': entity_data['property']['homestead_exempt'],
            'tax_year': entity_data['property']['tax_year']
        }
        
        conn.execute(text("""
            INSERT INTO properties (
                parcel_id, county, jurisdiction, situs_address_id, land_use_code,
                acreage, last_sale_date, last_sale_price, market_value, assessed_value,
                homestead_exempt, tax_year
            )
            VALUES (
                :parcel_id, :county, :jurisdiction, :situs_address_id, :land_use_code,
                :acreage, :last_sale_date, :last_sale_price, :market_value, :assessed_value,
                :homestead_exempt, :tax_year
            )
        """), property_params)
        
        # Get property ID
        result = conn.execute(text("""
            SELECT id FROM properties WHERE parcel_id = :parcel_id
        """), {'parcel_id': entity_data['property']['parcel_id']})
        property_id = result.fetchone()[0]
        logger.info(f"     Property ID: {property_id}")
    
    logger.info(f"     Acreage: {entity_data['property']['acreage']}, Market Value: ${entity_data['property']['market_value']:,.2f}")
    
    # 6. Create ownership relationship
    logger.info(f"  → Creating ownership relationship")
    
    # Check if relationship already exists
    result = conn.execute(text("""
        SELECT id FROM relationships 
        WHERE from_type = 'entity' AND from_id = :entity_id 
        AND to_type = 'property' AND to_id = :property_id 
        AND rel_type = 'owns'
    """), {'entity_id': entity_id, 'property_id': property_id})
    existing = result.fetchone()
    
    if not existing:
        conn.execute(text("""
            INSERT INTO relationships (
                from_type, from_id, to_type, to_id, rel_type, source_system, 
                start_date, confidence
            )
            VALUES (
                'entity', :entity_id, 'property', :property_id, 'owns', :source_system,
                :start_date, :confidence
            )
        """), {
            'entity_id': entity_id,
            'property_id': property_id,
            'source_system': entity_data['source_system'],
            'start_date': entity_data['property'].get('last_sale_date'),
            'confidence': 0.95
        })
        logger.info(f"     Relationship created")
    else:
        logger.info(f"     Relationship already exists")
    
    # 7. Create formation event
    logger.info(f"  → Creating formation event")
    
    # Check if event already exists
    result = conn.execute(text("""
        SELECT id FROM events 
        WHERE entity_id = :entity_id 
        AND event_type = 'FORMATION' 
        AND event_date = :formation_date
    """), {'entity_id': entity_id, 'formation_date': entity_data['formation_date']})
    existing = result.fetchone()
    
    if not existing:
        conn.execute(text("""
            INSERT INTO events (
                entity_id, event_type, event_date, source_system, payload
            )
            VALUES (
                :entity_id, 'FORMATION', :formation_date, :source_system, :payload
            )
        """), {
            'entity_id': entity_id,
            'formation_date': entity_data['formation_date'],
            'source_system': entity_data['source_system'],
            'payload': entity_data['formation_event_payload']
        })
        logger.info(f"     Formation event created")
    else:
        logger.info(f"     Formation event already exists")
    
    # 8. Create risk score
    logger.info(f"  → Creating risk score: Grade {entity_data['risk_score']['grade']}, Score {entity_data['risk_score']['score']}")
    
    # Check if risk score already exists for this entity (we'll create a new one each time to track history)
    # But for idempotency, we'll check if one was created very recently (within last minute)
    result = conn.execute(text("""
        SELECT id FROM risk_scores 
        WHERE entity_id = :entity_id 
        AND calculated_at > NOW() - INTERVAL '1 minute'
        LIMIT 1
    """), {'entity_id': entity_id})
    existing = result.fetchone()
    
    if not existing:
        conn.execute(text("""
            INSERT INTO risk_scores (
                entity_id, score, grade, flags
            )
            VALUES (
                :entity_id, :score, :grade, CAST(:flags AS jsonb)
            )
        """), {
            'entity_id': entity_id,
            'score': entity_data['risk_score']['score'],
            'grade': entity_data['risk_score']['grade'],
            'flags': entity_data['risk_score']['flags']
        })
        logger.info(f"     Risk Score created with flags: {entity_data['risk_score']['flags']}")
    else:
        logger.info(f"     Risk Score already exists (created recently)")
    
    logger.info(f"\n✓ Successfully created {entity_name}")


def generate_entity_data() -> list[Dict[str, Any]]:
    """Generate data for 3 realistic entities with varied characteristics."""
    today = date.today()
    
    entities = [
        # 1. Acme Holdings LLC - Grade A, low risk (~25)
        {
            'external_id': 'TX-LLC-001',
            'source_system': 'tx_sos',
            'type': 'llc',
            'legal_name': 'Acme Holdings LLC',
            'jurisdiction': 'TX',
            'status': 'ACTIVE',
            'formation_date': today - timedelta(days=1825),  # ~5 years old
            'ein_available': True,
            'ein_verified': True,
            'address': {
                'line1': '789 Enterprise Boulevard',
                'line2': 'Suite 500',
                'city': 'Austin',
                'state': 'TX',
                'postal_code': '78701',
                'county': 'Travis',
                'normalized_hash': 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6'
            },
            'agent': {
                'full_name': 'Sarah Mitchell',
                'normalized_name': 'SARAH MITCHELL'
            },
            'property_address': {
                'line1': '1000 Commerce Street',
                'city': 'Austin',
                'state': 'TX',
                'postal_code': '78703',
                'county': 'Travis',
                'normalized_hash': 'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1'
            },
            'property': {
                'parcel_id': 'TRAVIS-COM-001',
                'county': 'Travis',
                'jurisdiction': 'TX',
                'land_use_code': '0400',  # Commercial
                'acreage': Decimal('2.50'),
                'last_sale_date': today - timedelta(days=1460),  # ~4 years ago
                'last_sale_price': Decimal('750000.00'),
                'market_value': Decimal('950000.00'),
                'assessed_value': Decimal('890000.00'),
                'homestead_exempt': 'N',
                'tax_year': '2024'
            },
            'formation_event_payload': '{"filing_type": "Certificate of Formation", "filing_number": "TX-LLC-001"}',
            'risk_score': {
                'score': Decimal('24.5'),
                'grade': 'A',
                'flags': '["established_entity", "verified_ein", "stable_ownership"]'
            }
        },
        
        # 2. Summit Real Estate Corporation - Grade B, medium risk (~42)
        {
            'external_id': 'TX-CORP-002',
            'source_system': 'tx_sos',
            'type': 'corp',
            'legal_name': 'Summit Real Estate Corporation',
            'jurisdiction': 'TX',
            'status': 'ACTIVE',
            'formation_date': today - timedelta(days=912),  # ~2.5 years old
            'ein_available': True,
            'ein_verified': False,  # Not verified - adds some risk
            'address': {
                'line1': '1500 Summit Drive',
                'line2': None,
                'city': 'Austin',
                'state': 'TX',
                'postal_code': '78704',
                'county': 'Travis',
                'normalized_hash': 'c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2'
            },
            'agent': {
                'full_name': 'David Chen',
                'normalized_name': 'DAVID CHEN'
            },
            'property_address': {
                'line1': '2500 Riverside Parkway',
                'city': 'Austin',
                'state': 'TX',
                'postal_code': '78741',
                'county': 'Travis',
                'normalized_hash': 'd4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2c3'
            },
            'property': {
                'parcel_id': 'TRAVIS-COM-002',
                'county': 'Travis',
                'jurisdiction': 'TX',
                'land_use_code': '0400',  # Commercial
                'acreage': Decimal('3.75'),
                'last_sale_date': today - timedelta(days=245),  # Recent acquisition
                'last_sale_price': Decimal('1250000.00'),
                'market_value': Decimal('1320000.00'),
                'assessed_value': Decimal('1280000.00'),
                'homestead_exempt': 'N',
                'tax_year': '2024'
            },
            'formation_event_payload': '{"filing_type": "Certificate of Incorporation", "filing_number": "TX-CORP-002"}',
            'risk_score': {
                'score': Decimal('42.0'),
                'grade': 'B',
                'flags': '["ein_not_verified", "recent_property_purchase", "moderate_entity_age"]'
            }
        },
        
        # 3. Riverside Property Management LLC - Grade D, high risk (~68)
        {
            'external_id': 'TX-LLC-003',
            'source_system': 'tx_sos',
            'type': 'llc',
            'legal_name': 'Riverside Property Management LLC',
            'jurisdiction': 'TX',
            'status': 'ACTIVE',
            'formation_date': today - timedelta(days=45),  # Very new - high risk
            'ein_available': False,  # No EIN - high risk
            'ein_verified': False,
            'address': {
                'line1': '888 Startup Lane',
                'line2': 'Unit B',
                'city': 'Austin',
                'state': 'TX',
                'postal_code': '78705',
                'county': 'Travis',
                'normalized_hash': 'e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2c3d4'
            },
            'agent': {
                'full_name': 'QuickStart Registered Agents LLC',
                'normalized_name': 'QUICKSTART REGISTERED AGENTS LLC'
            },
            'property_address': {
                'line1': '3300 Investment Boulevard',
                'city': 'Austin',
                'state': 'TX',
                'postal_code': '78744',
                'county': 'Travis',
                'normalized_hash': 'f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2c3d4e5'
            },
            'property': {
                'parcel_id': 'TRAVIS-COM-003',
                'county': 'Travis',
                'jurisdiction': 'TX',
                'land_use_code': '0400',  # Commercial
                'acreage': Decimal('5.25'),
                'last_sale_date': today - timedelta(days=30),  # Very recent - rapid turnover risk
                'last_sale_price': Decimal('1850000.00'),
                'market_value': Decimal('1900000.00'),
                'assessed_value': Decimal('1775000.00'),
                'homestead_exempt': 'N',
                'tax_year': '2024'
            },
            'formation_event_payload': '{"filing_type": "Certificate of Formation", "filing_number": "TX-LLC-003"}',
            'risk_score': {
                'score': Decimal('68.5'),
                'grade': 'D',
                'flags': '["new_entity", "no_ein", "rapid_property_acquisition", "high_value_property"]'
            }
        }
    ]
    
    return entities


def verify_seeded_data(engine) -> None:
    """Verify the seeded data."""
    logger.info("\n" + "="*80)
    logger.info("DATA VERIFICATION")
    logger.info("="*80)
    
    with engine.connect() as conn:
        # Count new entities
        result = conn.execute(text("""
            SELECT COUNT(*) FROM entities 
            WHERE external_id IN ('TX-LLC-001', 'TX-CORP-002', 'TX-LLC-003')
        """))
        entity_count = result.fetchone()[0]
        logger.info(f"\nNew entities created: {entity_count}")
        
        # Show entity details
        result = conn.execute(text("""
            SELECT id, legal_name, type, status, formation_date
            FROM entities
            WHERE external_id IN ('TX-LLC-001', 'TX-CORP-002', 'TX-LLC-003')
            ORDER BY id
        """))
        
        logger.info("\nEntity Details:")
        for row in result:
            logger.info(f"  ID {row[0]}: {row[1]} ({row[2].upper()}) - {row[3]} - Formed: {row[4]}")
        
        # Show risk scores
        result = conn.execute(text("""
            SELECT e.legal_name, rs.score, rs.grade, rs.flags
            FROM risk_scores rs
            JOIN entities e ON rs.entity_id = e.id
            WHERE e.external_id IN ('TX-LLC-001', 'TX-CORP-002', 'TX-LLC-003')
            ORDER BY rs.score
        """))
        
        logger.info("\nRisk Scores:")
        for row in result:
            logger.info(f"  {row[0]}: Grade {row[2]} (Score: {row[1]})")
            logger.info(f"    Flags: {row[3]}")
        
        # Show properties
        result = conn.execute(text("""
            SELECT e.legal_name, p.parcel_id, p.acreage, p.market_value
            FROM properties p
            JOIN relationships r ON r.to_id = p.id AND r.to_type = 'property'
            JOIN entities e ON r.from_id = e.id AND r.from_type = 'entity'
            WHERE e.external_id IN ('TX-LLC-001', 'TX-CORP-002', 'TX-LLC-003')
            ORDER BY e.legal_name
        """))
        
        logger.info("\nProperty Ownership:")
        for row in result:
            logger.info(f"  {row[0]}: Parcel {row[1]} ({row[2]} acres, ${row[3]:,.2f} market value)")
    
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION COMPLETE")
    logger.info("="*80)


def main():
    """Main execution function."""
    logger.info("="*80)
    logger.info("CHAIN OF RECORD - ADVANCED DATA SEEDING")
    logger.info("="*80)
    
    # Get database URL
    database_url = get_database_url()
    logger.info(f"\nConnecting to database...")
    
    # Create engine
    try:
        engine = create_engine(database_url, future=True)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")
        
    except SQLAlchemyError as e:
        logger.error(f"\n❌ ERROR: Failed to connect to database")
        logger.error(f"Error: {e}")
        logger.error("\nPlease ensure:")
        logger.error("  1. PostgreSQL is running")
        logger.error("  2. DATABASE_URL environment variable is set correctly")
        logger.error("  3. Database schema is initialized (run scripts/init_db.py first)")
        sys.exit(1)
    
    try:
        # Generate entity data
        entities_data = generate_entity_data()
        
        # Seed each entity
        with engine.begin() as conn:
            for entity_data in entities_data:
                seed_entity_with_data(conn, entity_data)
        
        logger.info("\n" + "="*80)
        logger.info("All entities seeded successfully!")
        logger.info("="*80)
        
        # Verify the seeded data
        verify_seeded_data(engine)
        
        logger.info("\n✅ SUCCESS: Advanced data seeding complete!")
        logger.info("\nNext steps:")
        logger.info("  1. Start the API server: uvicorn app.main:app --reload")
        logger.info("  2. Test the endpoints:")
        logger.info("     - GET http://localhost:8000/api/v1/entities")
        logger.info("     - GET http://localhost:8000/api/v1/scores/entity/2")
        logger.info("     - GET http://localhost:8000/api/v1/properties")
        logger.info("  3. Explore high-risk entities: GET http://localhost:8000/api/v1/entities?grade=D")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
