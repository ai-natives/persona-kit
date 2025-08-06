"""Observation schemas for API requests and responses."""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..models.observation import ObservationType


class ObservationBase(BaseModel):
    """Base observation schema."""

    person_id: uuid.UUID
    type: ObservationType
    content: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)


class ObservationCreate(ObservationBase):
    """Schema for creating observations."""

    pass


class ObservationResponse(ObservationBase):
    """Schema for observation responses."""

    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
