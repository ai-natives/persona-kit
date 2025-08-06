"""Initial schema with type checks

Revision ID: 5fa63bf0a53d
Revises:
Create Date: 2025-08-06 14:09:13.605117

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5fa63bf0a53d'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial schema."""
    # Create custom types if they don't exist
    conn = op.get_bind()

    # Check if observation_type exists
    result = conn.execute(sa.text(
        "SELECT 1 FROM pg_type WHERE typname = 'observation_type'"
    ))
    if not result.fetchone():
        conn.execute(sa.text(
            "CREATE TYPE observation_type AS ENUM ('work_session', 'user_input', 'calendar_event')"
        ))

    # Check if task_status exists
    result = conn.execute(sa.text(
        "SELECT 1 FROM pg_type WHERE typname = 'task_status'"
    ))
    if not result.fetchone():
        conn.execute(sa.text(
            "CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'done', 'failed')"
        ))

    # Create tables
    op.create_table('observations',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('person_id', sa.UUID(), nullable=False),
        sa.Column('type', postgresql.ENUM('work_session', 'user_input', 'calendar_event', name='observation_type', create_type=False), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('mindscapes',
        sa.Column('person_id', sa.UUID(), nullable=False),
        sa.Column('traits', sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('person_id')
    )

    op.create_table('personas',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('person_id', sa.UUID(), nullable=False),
        sa.Column('mapper_id', sa.String(100), nullable=False),
        sa.Column('core', sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('overlay', sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('feedback',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('persona_id', sa.UUID(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('helpful', sa.Boolean(), nullable=True),
        sa.Column('context', sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('outbox_tasks',
        sa.Column('task_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'in_progress', 'done', 'failed', name='task_status', create_type=False), server_default=sa.text("'pending'"), nullable=False),
        sa.Column('run_after', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('task_id')
    )

    # Create indexes (including custom ones from our plan)
    op.create_index('idx_observations_person_created', 'observations', ['person_id', 'created_at'], unique=False)
    op.create_index('idx_mindscapes_person', 'mindscapes', ['person_id'], unique=False)
    op.create_index('idx_personas_expires', 'personas', ['expires_at'], unique=False)
    op.create_index('idx_personas_person_id', 'personas', ['person_id'], unique=False)
    op.create_index('idx_feedback_persona', 'feedback', ['persona_id', 'created_at'], unique=False)
    op.create_index('idx_outbox_status', 'outbox_tasks', ['status', 'run_after'], unique=False)


def downgrade() -> None:
    """Drop schema."""
    # Drop indexes
    op.drop_index('idx_outbox_status', table_name='outbox_tasks')
    op.drop_index('idx_feedback_persona', table_name='feedback')
    op.drop_index('idx_personas_person_id', table_name='personas')
    op.drop_index('idx_personas_expires', table_name='personas')
    op.drop_index('idx_mindscapes_person', table_name='mindscapes')
    op.drop_index('idx_observations_person_created', table_name='observations')

    # Drop tables
    op.drop_table('outbox_tasks')
    op.drop_table('feedback')
    op.drop_table('personas')
    op.drop_table('mindscapes')
    op.drop_table('observations')

    # Drop types
    conn = op.get_bind()
    conn.execute(sa.text("DROP TYPE IF EXISTS task_status"))
    conn.execute(sa.text("DROP TYPE IF EXISTS observation_type"))
