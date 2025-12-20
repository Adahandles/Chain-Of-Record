"""add verification tables

Revision ID: 002
Revises: 001
Create Date: 2025-12-20 07:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create verification_requests table
    op.create_table(
        'verification_requests',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('entity_id', sa.BigInteger(), nullable=True),
        sa.Column('person_id', sa.BigInteger(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('personal_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', sa.BigInteger(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['person_id'], ['people.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index(op.f('ix_verification_requests_id'), 'verification_requests', ['id'], unique=False)
    op.create_index(op.f('ix_verification_requests_user_id'), 'verification_requests', ['user_id'], unique=False)
    op.create_index(op.f('ix_verification_requests_entity_id'), 'verification_requests', ['entity_id'], unique=False)
    op.create_index(op.f('ix_verification_requests_person_id'), 'verification_requests', ['person_id'], unique=False)
    op.create_index(op.f('ix_verification_requests_status'), 'verification_requests', ['status'], unique=False)
    op.create_index(op.f('ix_verification_requests_reviewed_by'), 'verification_requests', ['reviewed_by'], unique=False)
    op.create_index('idx_verification_user_status', 'verification_requests', ['user_id', 'status'], unique=False)
    op.create_index('idx_verification_created', 'verification_requests', ['created_at'], unique=False)

    # Create verification_documents table
    op.create_table(
        'verification_documents',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('verification_request_id', sa.BigInteger(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('encrypted', sa.Boolean(), default=True, nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['verification_request_id'], ['verification_requests.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_verification_documents_id'), 'verification_documents', ['id'], unique=False)
    op.create_index(op.f('ix_verification_documents_verification_request_id'), 'verification_documents', ['verification_request_id'], unique=False)
    op.create_index(op.f('ix_verification_documents_document_type'), 'verification_documents', ['document_type'], unique=False)
    op.create_index('idx_verification_doc_verified', 'verification_documents', ['verified', 'document_type'], unique=False)

    # Create verification_liveness table
    op.create_table(
        'verification_liveness',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('verification_request_id', sa.BigInteger(), nullable=False),
        sa.Column('image_path', sa.String(length=500), nullable=False),
        sa.Column('encrypted', sa.Boolean(), default=True, nullable=False),
        sa.Column('liveness_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('passed', sa.Boolean(), default=False, nullable=False),
        sa.Column('checked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['verification_request_id'], ['verification_requests.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_verification_liveness_id'), 'verification_liveness', ['id'], unique=False)
    op.create_index(op.f('ix_verification_liveness_verification_request_id'), 'verification_liveness', ['verification_request_id'], unique=False)
    op.create_index('idx_verification_liveness_passed', 'verification_liveness', ['passed'], unique=False)

    # Add verification status to entities table
    op.add_column('entities', sa.Column('verification_status', sa.String(length=50), nullable=True))
    op.add_column('entities', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('idx_entity_verification_status', 'entities', ['verification_status'], unique=False)

    # Add verification status to people table
    op.add_column('people', sa.Column('verification_status', sa.String(length=50), nullable=True))
    op.add_column('people', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('idx_people_verification_status', 'people', ['verification_status'], unique=False)


def downgrade() -> None:
    # Remove verification status from people table
    op.drop_index('idx_people_verification_status', table_name='people')
    op.drop_column('people', 'verified_at')
    op.drop_column('people', 'verification_status')

    # Remove verification status from entities table
    op.drop_index('idx_entity_verification_status', table_name='entities')
    op.drop_column('entities', 'verified_at')
    op.drop_column('entities', 'verification_status')

    # Drop verification_liveness table
    op.drop_index('idx_verification_liveness_passed', table_name='verification_liveness')
    op.drop_index(op.f('ix_verification_liveness_verification_request_id'), table_name='verification_liveness')
    op.drop_index(op.f('ix_verification_liveness_id'), table_name='verification_liveness')
    op.drop_table('verification_liveness')

    # Drop verification_documents table
    op.drop_index('idx_verification_doc_verified', table_name='verification_documents')
    op.drop_index(op.f('ix_verification_documents_document_type'), table_name='verification_documents')
    op.drop_index(op.f('ix_verification_documents_verification_request_id'), table_name='verification_documents')
    op.drop_index(op.f('ix_verification_documents_id'), table_name='verification_documents')
    op.drop_table('verification_documents')

    # Drop verification_requests table
    op.drop_index('idx_verification_created', table_name='verification_requests')
    op.drop_index('idx_verification_user_status', table_name='verification_requests')
    op.drop_index(op.f('ix_verification_requests_reviewed_by'), table_name='verification_requests')
    op.drop_index(op.f('ix_verification_requests_status'), table_name='verification_requests')
    op.drop_index(op.f('ix_verification_requests_person_id'), table_name='verification_requests')
    op.drop_index(op.f('ix_verification_requests_entity_id'), table_name='verification_requests')
    op.drop_index(op.f('ix_verification_requests_user_id'), table_name='verification_requests')
    op.drop_index(op.f('ix_verification_requests_id'), table_name='verification_requests')
    op.drop_table('verification_requests')
