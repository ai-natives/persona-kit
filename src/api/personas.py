"""Persona endpoints."""
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def generate_persona() -> dict[str, Any]:
    """Generate a new persona."""
    # TODO: Implement in Phase 4
    return {"message": "Persona endpoint - to be implemented"}
