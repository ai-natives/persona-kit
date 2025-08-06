"""Feedback endpoints."""
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def submit_feedback() -> dict[str, Any]:
    """Submit feedback on a persona."""
    # TODO: Implement in Phase 6
    return {"message": "Feedback endpoint - to be implemented"}
