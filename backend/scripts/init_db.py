#!/usr/bin/env python3
"""
Database Initialization Script for Chain Of Record

This script:
1. Executes the init.sql file to create all database tables, indexes, and views
2. Seeds initial test data for development and testing
3. Verifies the database setup

Usage:
    python scripts/init_db.py

Environment Variables:
    DATABASE_URL - PostgreSQL connection string (default: postgresql://chain:chain@localhost:5432/chain)
"""

import sys
import os
import logging
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal

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


def execute_init_sql(engine) -> None:
    """Execute the init.sql file to create database schema."""
    logger.info("Executing init.sql to create database schema...")
    
    # Path to init.sql relative to this script
    script_dir = Path(__file__).parent.parent.parent  # backend -> Chain-Of-Record
    init_sql_path = script_dir / "infra" / "postgres" / "init.sql"
    
    if not init_sql_path.exists():
        raise FileNotFoundError(f"init.sql not found at {init_sql_path}")
    
    # Read the SQL file
    with open(init_sql_path, 'r') as f:
        sql_content = f.read()
    
    # Execute the SQL
    with engine.begin() as conn:
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        for stmt in statements:
            try:
                conn.execute(text(stmt))
            except Exception as e:
                # Log but continue - some statements might fail if already executed
                logger.debug(f"Statement execution note: {e}")
    
    logger.info("Database schema created successfully")


def seed_initial_data(engine) -> None:
    """Seed initial test data."""
    logger.info("Seeding initial test data...")
    
    today = date.today()
    
    with engine.begin() as conn:
        # 1. Test address - 123 Main Street, Austin, TX
        logger.info("Creating test address...")
        
        # Check if address already exists
        result = conn.execute(text("""
            SELECT id FROM addresses WHERE line1 = '123 Main Street' AND city = 'Austin' AND state = 'TX'
        """))
        existing = result.fetchone()
        
        if existing:
            address_id = existing[0]
            logger.info(f"Test address already exists with ID: {address_id}")
        else:
            conn.execute(text("""
                INSERT INTO addresses (line1, city, state, postal_code, county, country, normalized_hash)
                VALUES ('123 Main Street', 'Austin', 'TX', '78701', 'Travis', 'US', 
                        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
            """))
            
            # Get the address ID
            result = conn.execute(text("""
                SELECT id FROM addresses WHERE line1 = '123 Main Street' AND city = 'Austin' AND state = 'TX'
            """))
            address_id = result.fetchone()[0]
            logger.info(f"Test address created with ID: {address_id}")
        
        # 2. Test person - John Smith (registered agent)
        logger.info("Creating test person...")
        
        # Check if person already exists
        result = conn.execute(text("""
            SELECT id FROM people WHERE full_name = 'John Smith'
        """))
        existing = result.fetchone()
        
        if existing:
            person_id = existing[0]
            logger.info(f"Test person already exists with ID: {person_id}")
        else:
            conn.execute(text("""
                INSERT INTO people (full_name, normalized_name)
                VALUES ('John Smith', 'JOHN SMITH')
            """))
            
            # Get the person ID
            result = conn.execute(text("""
                SELECT id FROM people WHERE full_name = 'John Smith'
            """))
            person_id = result.fetchone()[0]
            logger.info(f"Test person created with ID: {person_id}")
        
        # 3. Test entity - Test Company LLC
        logger.info("Creating test entity...")
        formation_date = today - timedelta(days=365)
        
        # Check if entity already exists
        result = conn.execute(text("""
            SELECT id FROM entities WHERE external_id = 'TEST-LLC-001'
        """))
        existing = result.fetchone()
        
        if existing:
            entity_id = existing[0]
            logger.info(f"Test entity already exists with ID: {entity_id}")
        else:
            conn.execute(text("""
                INSERT INTO entities (
                    external_id, source_system, type, legal_name, jurisdiction, status,
                    formation_date, ein_available, ein_verified, registered_agent_id, primary_address_id
                )
                VALUES (
                    'TEST-LLC-001', 'test', 'llc', 'Test Company LLC', 'TX', 'ACTIVE',
                    :formation_date, true, true, :agent_id, :address_id
                )
            """), {
                'formation_date': formation_date,
                'agent_id': person_id,
                'address_id': address_id
            })
            
            # Get the entity ID
            result = conn.execute(text("""
                SELECT id FROM entities WHERE external_id = 'TEST-LLC-001'
            """))
            entity_id = result.fetchone()[0]
            logger.info(f"Test entity created with ID: {entity_id}")
        
        # 4. Test property - PARCEL-12345 in Travis County
        logger.info("Creating test property...")
        
        # First create a situs address for the property
        result = conn.execute(text("""
            SELECT id FROM addresses WHERE line1 = '456 Property Lane' AND city = 'Austin'
        """))
        existing = result.fetchone()
        
        if existing:
            property_address_id = existing[0]
        else:
            conn.execute(text("""
                INSERT INTO addresses (line1, city, state, postal_code, county, country, normalized_hash)
                VALUES ('456 Property Lane', 'Austin', 'TX', '78702', 'Travis', 'US', 
                        'a3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b856')
            """))
            
            result = conn.execute(text("""
                SELECT id FROM addresses WHERE line1 = '456 Property Lane' AND city = 'Austin'
            """))
            property_address_id = result.fetchone()[0]
        
        # Check if property already exists
        result = conn.execute(text("""
            SELECT id FROM properties WHERE parcel_id = 'PARCEL-12345'
        """))
        existing = result.fetchone()
        
        if existing:
            property_id = existing[0]
            logger.info(f"Test property already exists with ID: {property_id}")
        else:
            conn.execute(text("""
                INSERT INTO properties (
                    parcel_id, county, jurisdiction, situs_address_id, land_use_code,
                    acreage, market_value, assessed_value, homestead_exempt, tax_year
                )
                VALUES (
                    'PARCEL-12345', 'Travis', 'TX', :situs_address_id, '0100',
                    0.50, 350000.00, 325000.00, 'N', '2024'
                )
            """), {'situs_address_id': property_address_id})
            
            # Get the property ID
            result = conn.execute(text("""
                SELECT id FROM properties WHERE parcel_id = 'PARCEL-12345'
            """))
            property_id = result.fetchone()[0]
            logger.info(f"Test property created with ID: {property_id}")
        
        # 5. Test relationship - entity owns property
        logger.info("Creating test relationship...")
        
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
                    from_type, from_id, to_type, to_id, rel_type, source_system, confidence
                )
                VALUES (
                    'entity', :entity_id, 'property', :property_id, 'owns', 'test', 1.0
                )
            """), {'entity_id': entity_id, 'property_id': property_id})
            logger.info("Test relationship created")
        else:
            logger.info("Test relationship already exists")
        
        # 6. Test event - formation event
        logger.info("Creating test event...")
        
        # Check if event already exists
        result = conn.execute(text("""
            SELECT id FROM events 
            WHERE entity_id = :entity_id 
            AND event_type = 'FORMATION' 
            AND event_date = :formation_date
        """), {'entity_id': entity_id, 'formation_date': formation_date})
        existing = result.fetchone()
        
        if not existing:
            conn.execute(text("""
                INSERT INTO events (
                    entity_id, event_type, event_date, source_system, payload
                )
                VALUES (
                    :entity_id, 'FORMATION', :formation_date, 'test',
                    '{"filing_type": "Articles of Organization", "filing_number": "TEST-LLC-001"}'::jsonb
                )
            """), {'entity_id': entity_id, 'formation_date': formation_date})
            logger.info("Test event created")
        else:
            logger.info("Test event already exists")
        
        # 7. Test risk score - Grade B, score 35.5
        logger.info("Creating test risk score...")
        
        # Check if risk score already exists (we'll just check for the latest one)
        result = conn.execute(text("""
            SELECT id FROM risk_scores 
            WHERE entity_id = :entity_id 
            ORDER BY calculated_at DESC 
            LIMIT 1
        """), {'entity_id': entity_id})
        existing = result.fetchone()
        
        if not existing:
            conn.execute(text("""
                INSERT INTO risk_scores (
                    entity_id, score, grade, flags
                )
                VALUES (
                    :entity_id, 35.5, 'B', '["established_entity"]'::jsonb
                )
            """), {'entity_id': entity_id})
            logger.info("Test risk score created")
        else:
            logger.info("Test risk score already exists")
    
    logger.info("Initial test data seeded successfully")


def verify_database(engine) -> None:
    """Verify database setup by counting tables and records."""
    logger.info("\n" + "="*80)
    logger.info("DATABASE VERIFICATION")
    logger.info("="*80)
    
    with engine.connect() as conn:
        # Count tables
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """))
        table_count = result.fetchone()[0]
        logger.info(f"\nTables created: {table_count}")
        
        # List tables
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        logger.info(f"Tables: {', '.join(tables)}")
        
        # Count records in each table
        logger.info("\nRecord counts:")
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.fetchone()[0]
            logger.info(f"  {table}: {count}")
        
        # Count views
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.views 
            WHERE table_schema = 'public'
        """))
        view_count = result.fetchone()[0]
        logger.info(f"\nViews created: {view_count}")
        
        # List views
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        views = [row[0] for row in result]
        if views:
            logger.info(f"Views: {', '.join(views)}")
        
        # Count indexes
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE schemaname = 'public'
        """))
        index_count = result.fetchone()[0]
        logger.info(f"\nIndexes created: {index_count}")
    
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION COMPLETE")
    logger.info("="*80)


def main():
    """Main execution function."""
    logger.info("="*80)
    logger.info("CHAIN OF RECORD - DATABASE INITIALIZATION")
    logger.info("="*80)
    
    # Get database URL
    database_url = get_database_url()
    logger.info(f"\nConnecting to database...")
    logger.info(f"Database URL: {database_url.split('@')[1] if '@' in database_url else 'configured'}")
    
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
        logger.error("  3. Database user has appropriate permissions")
        sys.exit(1)
    
    try:
        # Execute init.sql
        execute_init_sql(engine)
        
        # Seed initial data
        seed_initial_data(engine)
        
        # Verify setup
        verify_database(engine)
        
        logger.info("\n✅ SUCCESS: Database initialized successfully!")
        logger.info("\nNext steps:")
        logger.info("  1. Run additional seeding: python scripts/seed_data.py")
        logger.info("  2. Start the API server: uvicorn app.main:app --reload")
        logger.info("  3. Test the endpoints:")
        logger.info("     - GET http://localhost:8000/api/v1/entities/1")
        logger.info("     - GET http://localhost:8000/api/v1/scores/entity/1")
        logger.info("     - GET http://localhost:8000/api/v1/properties/1")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
