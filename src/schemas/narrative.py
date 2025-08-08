"""Pydantic schemas for narrative API requests and responses."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# Request schemas
class CreateNarrativeRequest(BaseModel):
    """Request to create a new narrative (self-observation)."""
    person_id: uuid.UUID
    raw_text: str = Field(..., min_length=1, max_length=10000, description="Raw narrative text")
    tags: Optional[List[str]] = Field(default_factory=list, description="Optional tags")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional context")
    source: Optional[str] = Field(None, description="Source of the narrative (e.g., 'workbench', 'agent')")


class CurationRequest(BaseModel):
    """Request to create a trait curation."""
    person_id: uuid.UUID
    trait_path: str = Field(..., description="JSON path to the trait being curated")
    action: Literal["correct", "expand", "clarify"] = Field(..., description="Type of curation")
    raw_text: str = Field(..., min_length=1, max_length=10000, description="Curation narrative")
    original_value: Any = Field(..., description="Current value of the trait")
    tags: Optional[List[str]] = Field(default_factory=list)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class NarrativeSearchRequest(BaseModel):
    """Request to search narratives semantically."""
    person_id: uuid.UUID
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results to return")
    min_similarity: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity threshold")
    narrative_types: Optional[List[Literal["self_observation", "curation"]]] = Field(None, description="Filter by narrative types")


# Response schemas
class NarrativeResponse(BaseModel):
    """Response containing narrative details."""
    id: uuid.UUID
    person_id: uuid.UUID
    narrative_type: Literal["self_observation", "curation"]
    raw_text: str
    curated_text: Optional[str] = None
    tags: List[str]
    context: Dict[str, Any]
    trait_path: Optional[str] = None
    curation_action: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    source: Optional[str] = None
    embedding_generated: Optional[bool] = Field(None, description="Whether embedding was generated")
    
    class Config:
        from_attributes = True


class CreateNarrativeResponse(BaseModel):
    """Response after creating a narrative."""
    id: uuid.UUID
    message: str = "Narrative created successfully"
    embedding_generated: bool = True


class NarrativeSearchResult(BaseModel):
    """Single search result with similarity score."""
    narrative: NarrativeResponse
    similarity_score: float = Field(..., description="Cosine similarity score (may be negative for very dissimilar texts)")
    excerpt: Optional[str] = Field(None, description="Relevant excerpt from the narrative")


class NarrativeSearchResponse(BaseModel):
    """Response containing search results."""
    query: str
    results: List[NarrativeSearchResult]
    total_found: int
    search_time_ms: float