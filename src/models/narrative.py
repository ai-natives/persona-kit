"""Narrative model for storing human observations and curations."""
import uuid
from datetime import UTC, datetime
from typing import Any, List, Optional, Literal

from sqlalchemy import JSON, DateTime, String, Text, Float, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from .base import Base


class Narrative(Base):
    """Stores human narratives with embeddings for semantic search."""

    __tablename__ = "narratives"

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
    narrative_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of narrative: self_observation or curation",
    )
    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Original narrative text as provided by user",
    )
    curated_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Edited/refined version of the narrative",
    )
    tags: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
        comment="Extracted tags for categorization",
    )
    context: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
        comment="Additional context (time, location, etc.)",
    )
    trait_path: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="JSON path to trait (for curations)",
    )
    curation_action: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Type of curation: correct, expand, clarify",
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Source of narrative: workbench, agent, etc.",
    )
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        Vector(1536),
        nullable=True,
        comment="1536-dimensional embedding vector",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=lambda: datetime.now(UTC),
    )

    __table_args__ = (
        CheckConstraint(
            "narrative_type IN ('self_observation', 'curation')",
            name="narrative_type_check"
        ),
        CheckConstraint(
            "(narrative_type = 'curation' AND trait_path IS NOT NULL AND curation_action IS NOT NULL) OR (narrative_type = 'self_observation')",
            name="curation_fields_check"
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Narrative(id={self.id}, type={self.narrative_type}, person_id={self.person_id})>"


class TraitNarrativeLink(Base):
    """Links narratives to traits they support or contradict."""

    __tablename__ = "trait_narrative_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    narrative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    trait_path: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    link_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type: extracted_from, curates, supports, contradicts",
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Confidence score for the link",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        CheckConstraint(
            "link_type IN ('extracted_from', 'curates', 'supports', 'contradicts')",
            name="link_type_check"
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<TraitNarrativeLink(narrative_id={self.narrative_id}, trait={self.trait_path}, type={self.link_type})>"


class PersonaNarrativeUsage(Base):
    """Tracks which narratives influenced persona generation."""

    __tablename__ = "persona_narrative_usage"

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
    narrative_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    relevance_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="How relevant this narrative was to persona generation",
    )
    usage_context: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
        comment="Context about how narrative was used",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<PersonaNarrativeUsage(persona_id={self.persona_id}, narrative_id={self.narrative_id}, score={self.relevance_score})>"