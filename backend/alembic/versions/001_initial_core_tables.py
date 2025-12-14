"""initial core tables

Revision ID: 001
Revises: 
Create Date: 2025-12-14 09:27:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create entities table
    op.create_table(
        'entities',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('source_system', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('legal_name', sa.Text(), nullable=False),
        sa.Column('jurisdiction', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('formation_date', sa.Date(), nullable=True),
        sa.Column('ein_available', sa.Boolean(), nullable=True),
        sa.Column('ein_verified', sa.Boolean(), nullable=True),
        sa.Column('registered_agent_id', sa.BigInteger(), nullable=True),
        sa.Column('primary_address_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_entities_id'), 'entities', ['id'], unique=False)
    op.create_index(op.f('ix_entities_external_id'), 'entities', ['external_id'], unique=False)
    op.create_index(op.f('ix_entities_source_system'), 'entities', ['source_system'], unique=False)
    op.create_index(op.f('ix_entities_type'), 'entities', ['type'], unique=False)
    op.create_index(op.f('ix_entities_legal_name'), 'entities', ['legal_name'], unique=False)
    op.create_index(op.f('ix_entities_jurisdiction'), 'entities', ['jurisdiction'], unique=False)
    op.create_index(op.f('ix_entities_status'), 'entities', ['status'], unique=False)
    op.create_index(op.f('ix_entities_registered_agent_id'), 'entities', ['registered_agent_id'], unique=False)
    op.create_index(op.f('ix_entities_primary_address_id'), 'entities', ['primary_address_id'], unique=False)
    op.create_index('idx_entity_source_external', 'entities', ['source_system', 'external_id'], unique=False)
    op.create_index('idx_entity_name_type', 'entities', ['legal_name', 'type'], unique=False)
    op.create_index('idx_entity_jurisdiction_status', 'entities', ['jurisdiction', 'status'], unique=False)

    # Create people table
    op.create_table(
        'people',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('full_name', sa.Text(), nullable=False),
        sa.Column('normalized_name', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_people_id'), 'people', ['id'], unique=False)
    op.create_index(op.f('ix_people_full_name'), 'people', ['full_name'], unique=False)
    op.create_index(op.f('ix_people_normalized_name'), 'people', ['normalized_name'], unique=False)

    # Create addresses table
    op.create_table(
        'addresses',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('line1', sa.Text(), nullable=False),
        sa.Column('line2', sa.Text(), nullable=True),
        sa.Column('city', sa.Text(), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('postal_code', sa.String(length=10), nullable=True),
        sa.Column('county', sa.Text(), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('normalized_hash', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_addresses_id'), 'addresses', ['id'], unique=False)
    op.create_index(op.f('ix_addresses_city'), 'addresses', ['city'], unique=False)
    op.create_index(op.f('ix_addresses_state'), 'addresses', ['state'], unique=False)
    op.create_index(op.f('ix_addresses_postal_code'), 'addresses', ['postal_code'], unique=False)
    op.create_index(op.f('ix_addresses_county'), 'addresses', ['county'], unique=False)
    op.create_index(op.f('ix_addresses_country'), 'addresses', ['country'], unique=False)
    op.create_index(op.f('ix_addresses_normalized_hash'), 'addresses', ['normalized_hash'], unique=True)
    op.create_index('idx_address_city_state', 'addresses', ['city', 'state'], unique=False)
    op.create_index('idx_address_postal_county', 'addresses', ['postal_code', 'county'], unique=False)

    # Create properties table
    op.create_table(
        'properties',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('parcel_id', sa.String(), nullable=False),
        sa.Column('county', sa.String(), nullable=False),
        sa.Column('jurisdiction', sa.String(), nullable=True),
        sa.Column('situs_address_id', sa.BigInteger(), nullable=True),
        sa.Column('appraiser_url', sa.Text(), nullable=True),
        sa.Column('land_use_code', sa.String(), nullable=True),
        sa.Column('acreage', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('last_sale_date', sa.Date(), nullable=True),
        sa.Column('last_sale_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('market_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('assessed_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('homestead_exempt', sa.String(), nullable=True),
        sa.Column('tax_year', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_properties_id'), 'properties', ['id'], unique=False)
    op.create_index(op.f('ix_properties_parcel_id'), 'properties', ['parcel_id'], unique=False)
    op.create_index(op.f('ix_properties_county'), 'properties', ['county'], unique=False)
    op.create_index(op.f('ix_properties_jurisdiction'), 'properties', ['jurisdiction'], unique=False)
    op.create_index(op.f('ix_properties_situs_address_id'), 'properties', ['situs_address_id'], unique=False)
    op.create_index(op.f('ix_properties_land_use_code'), 'properties', ['land_use_code'], unique=False)
    op.create_index('idx_property_county_parcel', 'properties', ['county', 'parcel_id'], unique=False)
    op.create_index('idx_property_land_use', 'properties', ['county', 'land_use_code'], unique=False)
    op.create_index('idx_property_sale_date', 'properties', ['last_sale_date'], unique=False)
    op.create_index('idx_property_sale_price', 'properties', ['last_sale_price'], unique=False)

    # Create relationships table
    op.create_table(
        'relationships',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('from_type', sa.String(), nullable=False),
        sa.Column('from_id', sa.BigInteger(), nullable=False),
        sa.Column('to_type', sa.String(), nullable=False),
        sa.Column('to_id', sa.BigInteger(), nullable=False),
        sa.Column('rel_type', sa.String(), nullable=False),
        sa.Column('source_system', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('confidence', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_relationships_id'), 'relationships', ['id'], unique=False)
    op.create_index(op.f('ix_relationships_from_type'), 'relationships', ['from_type'], unique=False)
    op.create_index(op.f('ix_relationships_from_id'), 'relationships', ['from_id'], unique=False)
    op.create_index(op.f('ix_relationships_to_type'), 'relationships', ['to_type'], unique=False)
    op.create_index(op.f('ix_relationships_to_id'), 'relationships', ['to_id'], unique=False)
    op.create_index(op.f('ix_relationships_rel_type'), 'relationships', ['rel_type'], unique=False)
    op.create_index(op.f('ix_relationships_source_system'), 'relationships', ['source_system'], unique=False)
    op.create_index('idx_relationship_from', 'relationships', ['from_type', 'from_id', 'rel_type'], unique=False)
    op.create_index('idx_relationship_to', 'relationships', ['to_type', 'to_id', 'rel_type'], unique=False)
    op.create_index('idx_relationship_active', 'relationships', ['end_date'], unique=False)
    op.create_index('idx_relationship_source', 'relationships', ['source_system', 'rel_type'], unique=False)

    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('entity_id', sa.BigInteger(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('source_system', sa.String(), nullable=False),
        sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_entity_id'), 'events', ['entity_id'], unique=False)
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_event_date'), 'events', ['event_date'], unique=False)
    op.create_index(op.f('ix_events_source_system'), 'events', ['source_system'], unique=False)
    op.create_index('idx_event_entity_type', 'events', ['entity_id', 'event_type'], unique=False)
    op.create_index('idx_event_date_type', 'events', ['event_date', 'event_type'], unique=False)
    op.create_index('idx_event_source', 'events', ['source_system', 'event_type'], unique=False)

    # Create risk_scores table
    op.create_table(
        'risk_scores',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('entity_id', sa.BigInteger(), nullable=False),
        sa.Column('score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('grade', sa.String(length=1), nullable=False),
        sa.Column('flags', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_scores_id'), 'risk_scores', ['id'], unique=False)
    op.create_index(op.f('ix_risk_scores_entity_id'), 'risk_scores', ['entity_id'], unique=False)
    op.create_index(op.f('ix_risk_scores_grade'), 'risk_scores', ['grade'], unique=False)
    op.create_index(op.f('ix_risk_scores_calculated_at'), 'risk_scores', ['calculated_at'], unique=False)
    op.create_index('idx_risk_score_grade', 'risk_scores', ['grade', 'score'], unique=False)
    op.create_index('idx_risk_score_entity_date', 'risk_scores', ['entity_id', 'calculated_at'], unique=False)


def downgrade() -> None:
    # Drop risk_scores table
    op.drop_index('idx_risk_score_entity_date', table_name='risk_scores')
    op.drop_index('idx_risk_score_grade', table_name='risk_scores')
    op.drop_index(op.f('ix_risk_scores_calculated_at'), table_name='risk_scores')
    op.drop_index(op.f('ix_risk_scores_grade'), table_name='risk_scores')
    op.drop_index(op.f('ix_risk_scores_entity_id'), table_name='risk_scores')
    op.drop_index(op.f('ix_risk_scores_id'), table_name='risk_scores')
    op.drop_table('risk_scores')

    # Drop events table
    op.drop_index('idx_event_source', table_name='events')
    op.drop_index('idx_event_date_type', table_name='events')
    op.drop_index('idx_event_entity_type', table_name='events')
    op.drop_index(op.f('ix_events_source_system'), table_name='events')
    op.drop_index(op.f('ix_events_event_date'), table_name='events')
    op.drop_index(op.f('ix_events_event_type'), table_name='events')
    op.drop_index(op.f('ix_events_entity_id'), table_name='events')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_table('events')

    # Drop relationships table
    op.drop_index('idx_relationship_source', table_name='relationships')
    op.drop_index('idx_relationship_active', table_name='relationships')
    op.drop_index('idx_relationship_to', table_name='relationships')
    op.drop_index('idx_relationship_from', table_name='relationships')
    op.drop_index(op.f('ix_relationships_source_system'), table_name='relationships')
    op.drop_index(op.f('ix_relationships_rel_type'), table_name='relationships')
    op.drop_index(op.f('ix_relationships_to_id'), table_name='relationships')
    op.drop_index(op.f('ix_relationships_to_type'), table_name='relationships')
    op.drop_index(op.f('ix_relationships_from_id'), table_name='relationships')
    op.drop_index(op.f('ix_relationships_from_type'), table_name='relationships')
    op.drop_index(op.f('ix_relationships_id'), table_name='relationships')
    op.drop_table('relationships')

    # Drop properties table
    op.drop_index('idx_property_sale_price', table_name='properties')
    op.drop_index('idx_property_sale_date', table_name='properties')
    op.drop_index('idx_property_land_use', table_name='properties')
    op.drop_index('idx_property_county_parcel', table_name='properties')
    op.drop_index(op.f('ix_properties_land_use_code'), table_name='properties')
    op.drop_index(op.f('ix_properties_situs_address_id'), table_name='properties')
    op.drop_index(op.f('ix_properties_jurisdiction'), table_name='properties')
    op.drop_index(op.f('ix_properties_county'), table_name='properties')
    op.drop_index(op.f('ix_properties_parcel_id'), table_name='properties')
    op.drop_index(op.f('ix_properties_id'), table_name='properties')
    op.drop_table('properties')

    # Drop addresses table
    op.drop_index('idx_address_postal_county', table_name='addresses')
    op.drop_index('idx_address_city_state', table_name='addresses')
    op.drop_index(op.f('ix_addresses_normalized_hash'), table_name='addresses')
    op.drop_index(op.f('ix_addresses_country'), table_name='addresses')
    op.drop_index(op.f('ix_addresses_county'), table_name='addresses')
    op.drop_index(op.f('ix_addresses_postal_code'), table_name='addresses')
    op.drop_index(op.f('ix_addresses_state'), table_name='addresses')
    op.drop_index(op.f('ix_addresses_city'), table_name='addresses')
    op.drop_index(op.f('ix_addresses_id'), table_name='addresses')
    op.drop_table('addresses')

    # Drop people table
    op.drop_index(op.f('ix_people_normalized_name'), table_name='people')
    op.drop_index(op.f('ix_people_full_name'), table_name='people')
    op.drop_index(op.f('ix_people_id'), table_name='people')
    op.drop_table('people')

    # Drop entities table
    op.drop_index('idx_entity_jurisdiction_status', table_name='entities')
    op.drop_index('idx_entity_name_type', table_name='entities')
    op.drop_index('idx_entity_source_external', table_name='entities')
    op.drop_index(op.f('ix_entities_primary_address_id'), table_name='entities')
    op.drop_index(op.f('ix_entities_registered_agent_id'), table_name='entities')
    op.drop_index(op.f('ix_entities_status'), table_name='entities')
    op.drop_index(op.f('ix_entities_jurisdiction'), table_name='entities')
    op.drop_index(op.f('ix_entities_legal_name'), table_name='entities')
    op.drop_index(op.f('ix_entities_type'), table_name='entities')
    op.drop_index(op.f('ix_entities_source_system'), table_name='entities')
    op.drop_index(op.f('ix_entities_external_id'), table_name='entities')
    op.drop_index(op.f('ix_entities_id'), table_name='entities')
    op.drop_table('entities')
