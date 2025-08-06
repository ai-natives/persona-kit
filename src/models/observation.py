"""Observation model."""
import enum
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ObservationType(str, enum.Enum):
    """Types of observations."""

    WORK_SESSION = "work_session"
    USER_INPUT = "user_input"
    CALENDAR_EVENT = "calendar_event"


class Observation(Base):
    """Raw observation data from various sources."""

    __tablename__ = "observations"

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
    type: Mapped[ObservationType] = mapped_column(
        Enum(ObservationType, name="observation_type", native_enum=False),
        nullable=False,
    )
    content: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )
    meta: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
        name="metadata",  # Use 'metadata' as the column name in the database
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Observation(id={self.id}, type={self.type}, person_id={self.person_id})>"
