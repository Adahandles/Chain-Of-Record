-- Initial database setup for Chain Of Record
-- This file creates the basic schema structure
-- Production deployments should use Alembic migrations instead

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text matching

-- Core tables (matching our SQLAlchemy models)

-- Entities table
CREATE TABLE IF NOT EXISTS entities (
    id BIGSERIAL PRIMARY KEY,
    external_id VARCHAR,
    source_system VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    legal_name TEXT NOT NULL,
    jurisdiction VARCHAR,
    status VARCHAR,
    formation_date DATE,
    ein_available BOOLEAN,
    ein_verified BOOLEAN,
    registered_agent_id BIGINT,
    primary_address_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- People table
CREATE TABLE IF NOT EXISTS people (
    id BIGSERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    normalized_name TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Addresses table  
CREATE TABLE IF NOT EXISTS addresses (
    id BIGSERIAL PRIMARY KEY,
    line1 TEXT NOT NULL,
    line2 TEXT,
    city TEXT,
    state VARCHAR(2),
    postal_code VARCHAR(10),
    county TEXT,
    country VARCHAR(2) DEFAULT 'US',
    normalized_hash VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Properties table
CREATE TABLE IF NOT EXISTS properties (
    id BIGSERIAL PRIMARY KEY,
    parcel_id VARCHAR NOT NULL,
    county VARCHAR NOT NULL,
    jurisdiction VARCHAR,
    situs_address_id BIGINT,
    appraiser_url TEXT,
    land_use_code VARCHAR,
    acreage NUMERIC(10,4),
    last_sale_date DATE,
    last_sale_price NUMERIC(12,2),
    market_value NUMERIC(12,2),
    assessed_value NUMERIC(12,2),
    homestead_exempt VARCHAR,
    tax_year VARCHAR,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Relationships table (graph edges)
CREATE TABLE IF NOT EXISTS relationships (
    id BIGSERIAL PRIMARY KEY,
    from_type VARCHAR NOT NULL,
    from_id BIGINT NOT NULL,
    to_type VARCHAR NOT NULL,
    to_id BIGINT NOT NULL,
    rel_type VARCHAR NOT NULL,
    source_system VARCHAR NOT NULL,
    start_date DATE,
    end_date DATE,
    confidence NUMERIC(3,2),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Events table (time-series)
CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    entity_id BIGINT NOT NULL,
    event_type VARCHAR NOT NULL,
    event_date DATE NOT NULL,
    source_system VARCHAR NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Risk scores table
CREATE TABLE IF NOT EXISTS risk_scores (
    id BIGSERIAL PRIMARY KEY,
    entity_id BIGINT NOT NULL,
    score NUMERIC(5,2) NOT NULL,
    grade VARCHAR(1) NOT NULL,
    flags JSONB NOT NULL,
    calculated_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for performance

-- Entity indexes
CREATE INDEX IF NOT EXISTS idx_entities_external_id ON entities(external_id);
CREATE INDEX IF NOT EXISTS idx_entities_source_system ON entities(source_system);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_legal_name ON entities USING gin(legal_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_entities_jurisdiction ON entities(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_entities_status ON entities(status);
CREATE INDEX IF NOT EXISTS idx_entities_source_external ON entities(source_system, external_id);

-- People indexes
CREATE INDEX IF NOT EXISTS idx_people_full_name ON people USING gin(full_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_people_normalized_name ON people(normalized_name);

-- Address indexes
CREATE INDEX IF NOT EXISTS idx_addresses_normalized_hash ON addresses(normalized_hash);
CREATE INDEX IF NOT EXISTS idx_addresses_city_state ON addresses(city, state);
CREATE INDEX IF NOT EXISTS idx_addresses_postal_code ON addresses(postal_code);

-- Property indexes
CREATE INDEX IF NOT EXISTS idx_properties_parcel_id ON properties(parcel_id);
CREATE INDEX IF NOT EXISTS idx_properties_county ON properties(county);
CREATE INDEX IF NOT EXISTS idx_properties_county_parcel ON properties(county, parcel_id);
CREATE INDEX IF NOT EXISTS idx_properties_land_use ON properties(county, land_use_code);
CREATE INDEX IF NOT EXISTS idx_properties_sale_date ON properties(last_sale_date);
CREATE INDEX IF NOT EXISTS idx_properties_sale_price ON properties(last_sale_price);

-- Relationship indexes (critical for graph performance)
CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_type, from_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_type, to_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_relationships_active ON relationships(end_date) WHERE end_date IS NULL;
CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_system, rel_type);

-- Event indexes
CREATE INDEX IF NOT EXISTS idx_events_entity_id ON events(entity_id);
CREATE INDEX IF NOT EXISTS idx_events_entity_type ON events(entity_id, event_type);
CREATE INDEX IF NOT EXISTS idx_events_date_type ON events(event_date, event_type);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source_system, event_type);

-- Risk score indexes
CREATE INDEX IF NOT EXISTS idx_risk_scores_entity ON risk_scores(entity_id);
CREATE INDEX IF NOT EXISTS idx_risk_scores_grade ON risk_scores(grade, score);
CREATE INDEX IF NOT EXISTS idx_risk_scores_entity_date ON risk_scores(entity_id, calculated_at);

-- Create foreign key constraints (optional - can add referential integrity)
-- Commented out for flexibility during development
-- ALTER TABLE entities ADD CONSTRAINT fk_entities_agent FOREIGN KEY (registered_agent_id) REFERENCES people(id);
-- ALTER TABLE entities ADD CONSTRAINT fk_entities_address FOREIGN KEY (primary_address_id) REFERENCES addresses(id);
-- ALTER TABLE properties ADD CONSTRAINT fk_properties_address FOREIGN KEY (situs_address_id) REFERENCES addresses(id);
-- ALTER TABLE events ADD CONSTRAINT fk_events_entity FOREIGN KEY (entity_id) REFERENCES entities(id);
-- ALTER TABLE risk_scores ADD CONSTRAINT fk_risk_scores_entity FOREIGN KEY (entity_id) REFERENCES entities(id);

-- Create some utility views for common queries

-- Active entities view
CREATE OR REPLACE VIEW active_entities AS
SELECT *
FROM entities
WHERE status = 'ACTIVE' OR status IS NULL;

-- Recent scores view (latest score per entity)
CREATE OR REPLACE VIEW latest_risk_scores AS
SELECT DISTINCT ON (entity_id) 
    entity_id,
    score,
    grade,
    flags,
    calculated_at
FROM risk_scores
ORDER BY entity_id, calculated_at DESC;

-- High risk entities view
CREATE OR REPLACE VIEW high_risk_entities AS
SELECT e.*, rs.score, rs.grade, rs.flags
FROM entities e
JOIN latest_risk_scores rs ON e.id = rs.entity_id
WHERE rs.score > 60;  -- Adjust threshold as needed

-- Create initial admin user table (for future authentication)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Insert default admin user (password: admin123)
-- Hash generated with passlib bcrypt
INSERT INTO users (email, hashed_password, full_name, is_superuser) 
VALUES (
    'admin@chainofrecord.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LmEMsGnJqq9.K1.vK',
    'System Administrator', 
    true
) ON CONFLICT (email) DO NOTHING;

-- Log the setup
DO $$
BEGIN
    RAISE NOTICE 'Chain Of Record database initialized successfully';
    RAISE NOTICE 'Tables created: entities, people, addresses, properties, relationships, events, risk_scores, users';
    RAISE NOTICE 'Default admin user: admin@chainofrecord.com / admin123';
END$$;