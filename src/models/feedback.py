"""Feedback model."""
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Feedback(Base):
    """User feedback on persona suggestions."""

    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    helpful: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )
    context: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    rule_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    mapper_version: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Feedback(id={self.id}, persona_id={self.persona_id}, helpful={self.helpful})>"
