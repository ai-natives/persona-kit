"""Feedback schemas for API requests and responses."""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FeedbackBase(BaseModel):
    """Base feedback schema."""

    rating: int | None = Field(None, ge=1, le=5)
    helpful: bool | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class FeedbackCreate(FeedbackBase):
    """Schema for creating feedback."""

    persona_id: uuid.UUID


class FeedbackResponse(FeedbackBase):
    """Schema for feedback responses."""

    id: uuid.UUID
    persona_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True