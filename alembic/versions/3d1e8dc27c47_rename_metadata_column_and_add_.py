"""rename_metadata_column_and_add_narratives

Revision ID: 3d1e8dc27c47
Revises: 6c614228dc41
Create Date: 2025-08-07 09:01:29.571971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '3d1e8dc27c47'
down_revision: Union[str, Sequence[str], None] = '6c614228dc41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension
    op.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    
    # Create narratives table
    op.create_table(
        'narratives',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('narrative_type', sa.String(50), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('curated_text', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=False, server_default=text("'[]'::jsonb")),
        sa.Column('context', postgresql.JSONB(), nullable=False, server_default=text("'{}'::jsonb")),
        sa.Column('trait_path', sa.String(255), nullable=True),
        sa.Column('curation_action', sa.String(50), nullable=True),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('embedding', postgresql.ARRAY(sa.Float, dimensions=1), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("narrative_type IN ('self_observation', 'curation')", name='narrative_type_check'),
        sa.CheckConstraint("(narrative_type = 'curation' AND trait_path IS NOT NULL AND curation_action IS NOT NULL) OR (narrative_type = 'self_observation')", name='curation_fields_check')
    )
    
    # Create index on person_id and created_at for efficient queries
    op.create_index('idx_narratives_person_created', 'narratives', ['person_id', 'created_at'])
    
    # Create GIN indexes on JSONB fields for efficient querying
    op.create_index('idx_narratives_tags', 'narratives', ['tags'], postgresql_using='gin')
    op.create_index('idx_narratives_context', 'narratives', ['context'], postgresql_using='gin')
    
    # Note: We'll create the HNSW index for vector similarity search after we convert to proper vector type
    # For now, using ARRAY type for compatibility
    
    # Create trait_narrative_links table
    op.create_table(
        'trait_narrative_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('narrative_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trait_path', sa.String(255), nullable=False),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('link_type', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['narrative_id'], ['narratives.id'], ondelete='CASCADE'),
        sa.CheckConstraint("link_type IN ('extracted_from', 'curates', 'supports', 'contradicts')", name='link_type_check')
    )
    
    # Create indexes for trait_narrative_links
    op.create_index('idx_trait_links_narrative', 'trait_narrative_links', ['narrative_id'])
    op.create_index('idx_trait_links_person_trait', 'trait_narrative_links', ['person_id', 'trait_path'])
    
    # Create persona_narrative_usage table to track which narratives influenced persona generation
    op.create_table(
        'persona_narrative_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('persona_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('narrative_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('usage_context', postgresql.JSONB(), nullable=False, server_default=text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['narrative_id'], ['narratives.id'], ondelete='CASCADE')
    )
    
    # Create indexes for persona_narrative_usage
    op.create_index('idx_persona_usage_persona', 'persona_narrative_usage', ['persona_id'])
    op.create_index('idx_persona_usage_narrative', 'persona_narrative_usage', ['narrative_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('persona_narrative_usage')
    op.drop_table('trait_narrative_links')
    op.drop_table('narratives')
    
    # Note: We don't drop the pgvector extension as it might be used by other tables