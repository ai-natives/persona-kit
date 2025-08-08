"""fix_outbox_tasks_schema_final

Revision ID: 4060dc39aa98
Revises: add_missing_persona_columns
Create Date: 2025-08-07 22:50:30.881140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4060dc39aa98'
down_revision: Union[str, Sequence[str], None] = 'add_missing_persona_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # First check if columns already exist before adding them
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'outbox_tasks'
    """))
    existing_columns = {row[0] for row in result}
    
    # Convert status from enum to varchar if it's still an enum
    if 'status' in existing_columns:
        # Check if it's an enum
        result = conn.execute(sa.text("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'outbox_tasks' AND column_name = 'status'
        """))
        data_type = result.scalar()
        
        if data_type == 'USER-DEFINED':
            # It's an enum, convert to varchar
            # Create temporary column
            op.add_column('outbox_tasks', 
                sa.Column('status_new', sa.String(20), nullable=True)
            )
            
            # Copy data
            op.execute("UPDATE outbox_tasks SET status_new = status::text")
            
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
    
    # Add missing columns if they don't exist
    if 'attempts' not in existing_columns:
        op.add_column('outbox_tasks',
            sa.Column('attempts', sa.Integer(), nullable=False, server_default=sa.text('0'))
        )
    
    if 'last_error' not in existing_columns:
        op.add_column('outbox_tasks',
            sa.Column('last_error', sa.String(500), nullable=True)
        )
    
    if 'completed_at' not in existing_columns:
        op.add_column('outbox_tasks',
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove added columns
    op.drop_column('outbox_tasks', 'completed_at')
    op.drop_column('outbox_tasks', 'last_error')
    op.drop_column('outbox_tasks', 'attempts')
    
    # Convert status back to enum
    op.execute("""
        CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'done', 'failed')
    """)
    
    op.add_column('outbox_tasks',
        sa.Column('status_enum', 
                  sa.Enum('pending', 'in_progress', 'done', 'failed', 
                          name='task_status', create_type=False),
                  nullable=True)
    )
    
    op.execute("""
        UPDATE outbox_tasks 
        SET status_enum = status::task_status
    """)
    
    op.alter_column('outbox_tasks', 'status_enum', nullable=False)
    op.drop_column('outbox_tasks', 'status')
    op.alter_column('outbox_tasks', 'status_enum', new_column_name='status')
