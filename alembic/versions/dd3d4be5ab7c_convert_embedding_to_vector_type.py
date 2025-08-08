"""convert_embedding_to_vector_type

Revision ID: dd3d4be5ab7c
Revises: 3d1e8dc27c47
Create Date: 2025-08-07 12:07:09.015382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'dd3d4be5ab7c'
down_revision: Union[str, Sequence[str], None] = '3d1e8dc27c47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert embedding column from ARRAY to vector type and add HNSW index."""
    # First, we need to convert existing array data to vector format
    # Since the column might have data, we'll do this carefully
    
    # Add a temporary vector column
    op.add_column('narratives', sa.Column('embedding_vector', Vector(1536), nullable=True))
    
    # Convert existing array data to vector (if any exists)
    op.execute("""
        UPDATE narratives 
        SET embedding_vector = embedding::vector(1536)
        WHERE embedding IS NOT NULL
    """)
    
    # Drop the old column
    op.drop_column('narratives', 'embedding')
    
    # Rename the new column
    op.alter_column('narratives', 'embedding_vector', new_column_name='embedding')
    
    # Create HNSW index for fast similarity search
    op.execute("""
        CREATE INDEX idx_narratives_embedding_hnsw
        ON narratives 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
    
    # Also create an index on person_id + narrative_type for filtered searches
    op.create_index(
        'idx_narratives_person_type',
        'narratives',
        ['person_id', 'narrative_type'],
        unique=False
    )


def downgrade() -> None:
    """Convert back to array type."""
    # Drop the HNSW index
    op.drop_index('idx_narratives_embedding_hnsw', table_name='narratives')
    op.drop_index('idx_narratives_person_type', table_name='narratives')
    
    # Add temporary array column
    op.add_column('narratives', sa.Column('embedding_array', sa.ARRAY(sa.Float), nullable=True))
    
    # Convert vector back to array
    op.execute("""
        UPDATE narratives 
        SET embedding_array = ARRAY(SELECT unnest(embedding::float[]))
        WHERE embedding IS NOT NULL
    """)
    
    # Drop vector column
    op.drop_column('narratives', 'embedding')
    
    # Rename array column back
    op.alter_column('narratives', 'embedding_array', new_column_name='embedding')
