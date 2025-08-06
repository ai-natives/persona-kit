"""Add retry fields to outbox_tasks

Revision ID: 6c614228dc41
Revises: 5fa63bf0a53d
Create Date: 2025-08-06 15:55:27.166901

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '6c614228dc41'
down_revision: str | Sequence[str] | None = '5fa63bf0a53d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add retry-related columns to outbox_tasks."""
    op.add_column('outbox_tasks', sa.Column('attempts', sa.Integer(), server_default='0', nullable=False))
    op.add_column('outbox_tasks', sa.Column('last_error', sa.String(length=500), nullable=True))
    op.add_column('outbox_tasks', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Remove retry-related columns from outbox_tasks."""
    op.drop_column('outbox_tasks', 'completed_at')
    op.drop_column('outbox_tasks', 'last_error')
    op.drop_column('outbox_tasks', 'attempts')