"""Persona schemas for API requests and responses."""
import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PersonaBase(BaseModel):
    """Base persona schema."""

    mapper_id: str = Field(..., min_length=1, max_length=100)
    core: dict[str, Any] = Field(default_factory=dict)
    overlay: dict[str, Any] = Field(default_factory=dict)


class PersonaCreate(PersonaBase):
    """Schema for creating personas."""

    person_id: uuid.UUID
    expires_at: datetime


class NarrativeContext(BaseModel):
    """Narrative context for persona generation."""
    
    narrative_id: uuid.UUID
    text: str
    relevance_score: float
    narrative_type: str


class PersonaResponse(PersonaBase):
    """Schema for persona responses."""

    id: uuid.UUID
    person_id: uuid.UUID
    expires_at: datetime
    created_at: datetime
    narrative_context: Optional[List[NarrativeContext]] = None
    metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True
