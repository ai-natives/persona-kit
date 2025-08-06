"""Persona model."""
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Persona(Base):
    """Generated persona with TTL support."""

    __tablename__ = "personas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    mapper_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    core: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    overlay: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Persona(id={self.id}, mapper_id={self.mapper_id}, expires_at={self.expires_at})>"
