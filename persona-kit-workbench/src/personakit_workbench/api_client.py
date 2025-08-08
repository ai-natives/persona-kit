"""PersonaKit API client."""
import os
from typing import Any
from uuid import UUID

import httpx


class PersonaKitClient:
    """Client for interacting with PersonaKit API."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize client with API base URL."""
        self.base_url = base_url or os.getenv(
            "PERSONAKIT_API_URL", "http://localhost:8042"
        )
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def health_check(self) -> dict[str, Any]:
        """Check API health."""
        response = await self.client.get("/health/")
        response.raise_for_status()
        return response.json()

    async def create_observation(
        self,
        person_id: str | UUID,
        observation_type: str,
        content: dict[str, Any],
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new observation."""
        data = {
            "person_id": str(person_id),
            "type": observation_type,
            "content": content,
            "meta": meta or {},
        }
        response = await self.client.post("/observations", json=data)
        response.raise_for_status()
        return response.json()

    async def generate_persona(
        self,
        person_id: str | UUID,
        mapper_id: str = "daily_work_optimizer",
        context: dict[str, Any] | None = None,
        ttl_hours: int | None = None,
    ) -> dict[str, Any]:
        """Generate a persona from current mindscape."""
        data = {
            "person_id": str(person_id),
            "mapper_id": mapper_id,
            "context": context or {},
        }
        if ttl_hours is not None:
            data["ttl_hours"] = ttl_hours

        response = await self.client.post("/personas", json=data)
        response.raise_for_status()
        return response.json()

    async def get_active_personas(self, person_id: str | UUID) -> list[dict[str, Any]]:
        """Get all active personas for a person."""
        params = {"person_id": str(person_id)}
        response = await self.client.get("/personas/active", params=params)
        response.raise_for_status()
        return response.json()

    async def create_feedback(
        self,
        persona_id: str | UUID,
        rating: int | None = None,
        helpful: bool | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create feedback for a persona."""
        data = {
            "persona_id": str(persona_id),
            "context": context or {},
        }
        if rating is not None:
            data["rating"] = rating
        if helpful is not None:
            data["helpful"] = helpful

        response = await self.client.post("/feedback", json=data)
        response.raise_for_status()
        return response.json()

    async def create_self_observation(
        self,
        person_id: str | UUID,
        text: str,
        tags: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a self-observation narrative."""
        data = {
            "person_id": str(person_id),
            "raw_text": text,
            "tags": tags or [],
            "context": context or {},
        }
        response = await self.client.post("/api/narratives/self-observation", json=data)
        response.raise_for_status()
        return response.json()

    async def create_curation(
        self,
        person_id: str | UUID,
        trait_path: str,
        text: str,
        tags: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a trait curation narrative."""
        data = {
            "person_id": str(person_id),
            "trait_path": trait_path,
            "raw_text": text,
            "action": "expand",  # Default action
            "original_value": context.get("original_value", ""),  # Will need to be provided
            "tags": tags or [],
            "context": context or {},
        }
        response = await self.client.post("/api/narratives/curate", json=data)
        response.raise_for_status()
        return response.json()

    async def search_narratives(
        self,
        person_id: str | UUID,
        query: str,
        narrative_type: str | None = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
    ) -> dict[str, Any]:
        """Search narratives semantically."""
        data = {
            "person_id": str(person_id),
            "query": query,
            "limit": limit,
            "threshold": similarity_threshold,
        }
        if narrative_type:
            data["narrative_type"] = narrative_type
        
        response = await self.client.post("/api/narratives/search", json=data)
        response.raise_for_status()
        return response.json()

    async def get_person_narratives(
        self,
        person_id: str | UUID,
        narrative_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get narratives for a person."""
        params = {
            "limit": limit,
            "offset": offset,
        }
        if narrative_type:
            params["narrative_type"] = narrative_type
        
        response = await self.client.get(
            f"/api/narratives/person/{person_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def __aenter__(self) -> "PersonaKitClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()