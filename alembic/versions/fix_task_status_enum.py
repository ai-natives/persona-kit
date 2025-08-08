"""fix task status enum issue

Revision ID: fix_task_status_enum
Revises: e53c88db94b1
Create Date: 2025-01-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fix_task_status_enum'
down_revision: Union[str, None] = 'e53c88db94b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert task_status from enum to varchar to fix AsyncPG issues."""
    # First, create a temporary column
    op.add_column('outbox_tasks', 
        sa.Column('status_new', sa.String(20), nullable=True)
    )
    
    # Copy data from enum to string
    op.execute("""
        UPDATE outbox_tasks 
        SET status_new = status::text
    """)
    
    # Make it not nullable
    op.alter_column('outbox_tasks', 'status_new', nullable=False)
    
    # Drop the old column
    op.drop_column('outbox_tasks', 'status')
    
    # Rename the new column
    op.alter_column('outbox_tasks', 'status_new', new_column_name='status')
    
    # Re-create the index
    op.create_index('ix_outbox_tasks_status', 'outbox_tasks', ['status'])
    
    # Drop the enum type
    op.execute('DROP TYPE IF EXISTS task_status')


def downgrade() -> None:
    """Revert back to enum type."""
    # Create enum type
    op.execute("""
        CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'done', 'failed')
    """)
    
    # Create temporary column with enum type
    op.add_column('outbox_tasks',
        sa.Column('status_enum', 
                  postgresql.ENUM('pending', 'in_progress', 'done', 'failed', 
                                  name='task_status', create_type=False),
                  nullable=True)
    )
    
    # Copy data
    op.execute("""
        UPDATE outbox_tasks 
        SET status_enum = status::task_status
    """)
    
    # Make it not nullable
    op.alter_column('outbox_tasks', 'status_enum', nullable=False)
    
    # Drop the string column
    op.drop_column('outbox_tasks', 'status')
    
    # Rename back
    op.alter_column('outbox_tasks', 'status_enum', new_column_name='status')