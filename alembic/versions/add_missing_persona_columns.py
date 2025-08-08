"""Add missing persona columns

Revision ID: add_missing_persona_columns
Revises: fix_task_status_enum
Create Date: 2025-01-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_missing_persona_columns'
down_revision: Union[str, None] = 'fix_task_status_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to personas table."""
    # Add mapper_config_id
    op.add_column('personas', 
        sa.Column('mapper_config_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Add mapper_version
    op.add_column('personas',
        sa.Column('mapper_version', sa.Integer(), nullable=True)
    )
    
    # Add metadata column
    op.add_column('personas',
        sa.Column('metadata', sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=True)
    )


def downgrade() -> None:
    """Remove added columns."""
    op.drop_column('personas', 'metadata')
    op.drop_column('personas', 'mapper_version')
    op.drop_column('personas', 'mapper_config_id')