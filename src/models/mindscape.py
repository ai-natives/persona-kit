"""Mindscape model."""
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Mindscape(Base):
    """Aggregated traits and patterns for a person."""

    __tablename__ = "mindscapes"

    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    traits: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=lambda: datetime.now(UTC),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Mindscape(person_id={self.person_id}, version={self.version})>"
