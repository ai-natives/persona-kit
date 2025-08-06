"""Persona endpoints."""
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..mappers import DailyWorkOptimizer
from ..repositories import MindscapeRepository, PersonaRepository
from ..schemas.persona import PersonaResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class PersonaGenerateRequest(BaseModel):
    """Request to generate a persona."""
    person_id: uuid.UUID
    mapper_id: str = Field(..., description="Mapper to use (e.g., 'daily_work_optimizer')")
    context: dict[str, Any] = Field(default_factory=dict, description="Optional context data")
    ttl_hours: int | None = Field(None, ge=1, le=168, description="Override TTL (1-168 hours)")


@router.post("/", response_model=PersonaResponse)
async def generate_persona(
    request: PersonaGenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Generate a new persona from current mindscape.

    This endpoint:
    1. Fetches the latest mindscape for the person
    2. Uses the specified mapper to generate a persona
    3. Stores the persona with expiration
    4. Returns the generated persona
    """
    # Get repositories
    mindscape_repo = MindscapeRepository(db)
    persona_repo = PersonaRepository(db)

    # Fetch current mindscape
    mindscape = await mindscape_repo.get_by_person(request.person_id)
    if not mindscape:
        raise HTTPException(
            status_code=404,
            detail=f"No mindscape found for person {request.person_id}",
        )

    # Initialize mapper based on mapper_id
    if request.mapper_id == "daily_work_optimizer":
        mapper = DailyWorkOptimizer()
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown mapper: {request.mapper_id}",
        )

    # Add current time to context if not provided
    if "current_time" not in request.context:
        request.context["current_time"] = datetime.now(UTC)

    try:
        # Generate persona using mapper
        persona = mapper.create_persona(
            person_id=request.person_id,
            mindscape=mindscape,
            context=request.context,
            ttl_hours=request.ttl_hours,
        )

        # Save to database
        saved_persona = await persona_repo.create(
            person_id=persona.person_id,
            mapper_id=persona.mapper_id,
            core=persona.core,
            overlay=persona.overlay,
            expires_at=persona.expires_at,
        )

        logger.info(
            "Generated persona",
            extra={
                "persona_id": str(saved_persona.id),
                "person_id": str(request.person_id),
                "mapper_id": request.mapper_id,
                "expires_at": saved_persona.expires_at.isoformat(),
            },
        )

        return saved_persona

    except ValueError as e:
        # Missing required traits
        logger.warning(
            f"Failed to generate persona: {e}",
            extra={
                "person_id": str(request.person_id),
                "mapper_id": request.mapper_id,
            },
        )
        raise HTTPException(
            status_code=422,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Error generating persona: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate persona",
        ) from e


@router.get("/active")
async def get_active_personas(
    person_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[PersonaResponse]:
    """Get all active (non-expired) personas for a person."""
    persona_repo = PersonaRepository(db)
    personas = await persona_repo.get_active_by_person(person_id)

    return [
        PersonaResponse.model_validate(p)
        for p in personas
    ]


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get a specific persona by ID."""
    persona_repo = PersonaRepository(db)
    persona = await persona_repo.get(str(persona_id))

    if not persona:
        raise HTTPException(
            status_code=404,
            detail=f"Persona {persona_id} not found",
        )

    # Check if expired
    if persona.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=410,  # Gone
            detail="Persona has expired",
        )

    return persona
