"""Observation endpoints."""
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_observation() -> dict[str, Any]:
    """Create a new observation."""
    # TODO: Implement in Phase 3
    return {"message": "Observation endpoint - to be implemented"}
