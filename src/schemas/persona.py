"""Persona schemas for API requests and responses."""
import uuid
from datetime import datetime
from typing import Any

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


class PersonaResponse(PersonaBase):
    """Schema for persona responses."""

    id: uuid.UUID
    person_id: uuid.UUID
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
