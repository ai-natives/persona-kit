"""Mindscape schemas for API requests and responses."""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MindscapeBase(BaseModel):
    """Base mindscape schema."""

    traits: dict[str, Any] = Field(default_factory=dict)


class MindscapeUpdate(MindscapeBase):
    """Schema for updating mindscape traits."""

    pass


class MindscapeResponse(MindscapeBase):
    """Schema for mindscape responses."""

    person_id: uuid.UUID
    version: int
    updated_at: datetime

    class Config:
        from_attributes = True