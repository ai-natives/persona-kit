"""Persona endpoints."""
import logging
import os
import uuid
from datetime import UTC, datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.narrative import PersonaNarrativeUsage
from ..models.mindscape import Mindscape
from ..models.persona import Persona
from ..repositories import MindscapeRepository, PersonaRepository
from ..schemas.persona import PersonaResponse, NarrativeContext
from ..services.persona_generator import PersonaGenerator
from ..services.narrative_service import NarrativeService

router = APIRouter()
logger = logging.getLogger(__name__)


class PersonaGenerateRequest(BaseModel):
    """Request to generate a persona."""
    person_id: uuid.UUID
    mapper_id: str = Field(..., description="Mapper to use (e.g., 'daily_work_optimizer')")
    context: dict[str, Any] = Field(default_factory=dict, description="Optional context data")
    ttl_hours: int | None = Field(None, ge=1, le=168, description="Override TTL (1-168 hours)")


# Helper functions for persona generation
async def _fetch_mindscape(
    db: AsyncSession,
    person_id: uuid.UUID
) -> Mindscape:
    """Fetch mindscape for a person, raising 404 if not found."""
    mindscape_repo = MindscapeRepository(db)
    mindscape = await mindscape_repo.get_by_person(person_id)
    
    if not mindscape:
        raise HTTPException(
            status_code=404,
            detail=f"No mindscape found for person {person_id}",
        )
    
    return mindscape


async def _create_persona_generator(db: AsyncSession) -> PersonaGenerator:
    """Create and configure persona generator with required services."""
    from ..services.embedding_service import EmbeddingService
    
    # Use local embeddings - no API key needed
    embedding_service = EmbeddingService()
    narrative_service = NarrativeService(db, embedding_service)
    return PersonaGenerator(db, narrative_service)


def _prepare_context(context: dict[str, Any]) -> dict[str, Any]:
    """Prepare context with defaults like current time."""
    if "current_time" not in context:
        context["current_time"] = datetime.now(UTC)
    return context


async def _save_persona_to_db(
    persona_repo: PersonaRepository,
    persona: Persona
) -> Persona:
    """Save generated persona to database."""
    return await persona_repo.create(
        person_id=persona.person_id,
        mapper_id=persona.mapper_id,
        mapper_config_id=persona.mapper_config_id,
        mapper_version=persona.mapper_version,
        core=persona.core,
        overlay=persona.overlay,
        expires_at=persona.expires_at,
        metadata=persona.meta,
    )


async def _track_narrative_usage(
    db: AsyncSession,
    persona: Persona,
    saved_persona: Persona
) -> List[NarrativeContext]:
    """Track which narratives were used in persona generation."""
    narrative_contexts = []
    
    if not hasattr(persona, '_narrative_usage') or not persona._narrative_usage:
        return narrative_contexts
    
    try:
        for narrative in persona._narrative_usage:
            narrative_context = await _process_single_narrative_usage(
                db, narrative, saved_persona.id
            )
            if narrative_context:
                narrative_contexts.append(narrative_context)
        
        # Note: PersonaNarrativeUsage records will be committed with the session
        
    except Exception as e:
        logger.warning(
            f"Failed to track narrative usage: {e}",
            extra={
                "persona_id": str(saved_persona.id),
                "error": str(e)
            }
        )
        # Continue without narrative tracking rather than failing the request
    
    return narrative_contexts


async def _process_single_narrative_usage(
    db: AsyncSession,
    narrative: dict,
    persona_id: uuid.UUID
) -> Optional[NarrativeContext]:
    """Process and track usage of a single narrative."""
    narrative_id_str = narrative.get('id')
    if not narrative_id_str:
        logger.warning("Narrative missing ID, skipping usage tracking")
        return None
    
    # Create usage tracking record
    usage = PersonaNarrativeUsage(
        persona_id=persona_id,
        narrative_id=uuid.UUID(narrative_id_str),
        relevance_score=narrative.get('score', 0.0),
        usage_context={
            'rule_id': narrative.get('rule_id'),
            'query': narrative.get('query'),
        }
    )
    db.add(usage)
    
    # Return context for response
    return NarrativeContext(
        narrative_id=usage.narrative_id,
        text=narrative.get('text', ''),
        relevance_score=narrative.get('score', 0.0),
        narrative_type=narrative.get('type', 'unknown')
    )


def _build_persona_response(
    saved_persona: Persona,
    narrative_contexts: List[NarrativeContext]
) -> PersonaResponse:
    """Build the final persona response with narrative context."""
    # Convert the persona to dict and fix the metadata field name
    persona_dict = {
        "id": saved_persona.id,
        "person_id": saved_persona.person_id,
        "mapper_id": saved_persona.mapper_id,
        "mapper_config_id": saved_persona.mapper_config_id,
        "mapper_version": saved_persona.mapper_version,
        "core": saved_persona.core,
        "overlay": saved_persona.overlay,
        "metadata": saved_persona.meta,  # Map meta -> metadata
        "expires_at": saved_persona.expires_at,
        "created_at": saved_persona.created_at,
        "narrative_context": narrative_contexts,
    }
    return PersonaResponse(**persona_dict)


def _log_persona_generation(
    saved_persona: Persona,
    request: PersonaGenerateRequest,
    narrative_count: int
) -> None:
    """Log successful persona generation."""
    logger.info(
        "Generated persona",
        extra={
            "persona_id": str(saved_persona.id),
            "person_id": str(request.person_id),
            "mapper_id": request.mapper_id,
            "expires_at": saved_persona.expires_at.isoformat(),
            "narrative_count": narrative_count,
        },
    )


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
    try:
        # Step 1: Fetch required data
        mindscape = await _fetch_mindscape(db, request.person_id)
        
        # Step 2: Prepare context and services
        request.context = _prepare_context(request.context)
        generator = await _create_persona_generator(db)
        
        # Step 3: Generate the persona
        persona = await _generate_persona_core(
            generator, request, mindscape
        )
        
        # Step 4: Save to database
        persona_repo = PersonaRepository(db)
        saved_persona = await _save_persona_to_db(persona_repo, persona)
        
        # Step 5: Track narrative usage
        narrative_contexts = await _track_narrative_usage(
            db, persona, saved_persona
        )
        
        # Step 6: Log and return response
        _log_persona_generation(saved_persona, request, len(narrative_contexts))
        return _build_persona_response(saved_persona, narrative_contexts)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Missing required traits
        _handle_validation_error(e, request)
    except Exception as e:
        # Unexpected errors
        _handle_unexpected_error(e)


async def _generate_persona_core(
    generator: PersonaGenerator,
    request: PersonaGenerateRequest,
    mindscape: Mindscape
) -> Persona:
    """Generate persona using the configured mapper."""
    return await generator.generate_persona(
        person_id=request.person_id,
        mapper_id=request.mapper_id,
        mindscape=mindscape,
        context=request.context,
        ttl_hours=request.ttl_hours,
    )


def _handle_validation_error(
    error: ValueError,
    request: PersonaGenerateRequest
) -> None:
    """Handle validation errors with proper logging and response."""
    logger.warning(
        f"Failed to generate persona: {error}",
        extra={
            "person_id": str(request.person_id),
            "mapper_id": request.mapper_id,
        },
    )
    raise HTTPException(
        status_code=422,
        detail=str(error),
    ) from error


def _handle_unexpected_error(error: Exception) -> None:
    """Handle unexpected errors with proper logging."""
    logger.error(f"Error generating persona: {error}", exc_info=True)
    raise HTTPException(
        status_code=500,
        detail="Failed to generate persona",
    ) from error


@router.get("/", response_model=List[PersonaResponse])
async def list_personas(
    person_id: Optional[uuid.UUID] = Query(None, description="Filter by person ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of personas to return"),
    offset: int = Query(0, ge=0, description="Number of personas to skip"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    List personas with optional filtering.
    
    This endpoint returns recent personas, ordered by created_at descending.
    """
    try:
        persona_repo = PersonaRepository(db)
        
        # Use a simple query for now
        from sqlalchemy import select, desc
        
        query = select(Persona).order_by(desc(Persona.created_at))
        
        if person_id:
            query = query.filter(Persona.person_id == person_id)
            
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        personas = result.scalars().all()
        
        # Convert to response format
        responses = []
        for persona in personas:
            # Get narratives used (if any)
            narrative_contexts = []
            if hasattr(persona, 'narrative_usages'):
                for usage in persona.narrative_usages:
                    narrative_contexts.append(NarrativeContext(
                        narrative_id=usage.narrative_id,
                        relevance_score=usage.relevance_score,
                        usage_notes=usage.usage_notes or ""
                    ))
            
            responses.append(PersonaResponse(
                id=persona.id,
                person_id=persona.person_id,
                mapper_id=persona.mapper_id,
                core=persona.core,
                overlay=persona.overlay,
                expires_at=persona.expires_at,
                created_at=persona.created_at,
                metadata=persona.meta,
                narrative_context=narrative_contexts
            ))
        
        return responses
        
    except Exception as e:
        logger.error(f"Failed to list personas: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to list personas",
        ) from e


@router.get("/active")
async def get_active_personas(
    person_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[PersonaResponse]:
    """Get all active (non-expired) personas for a person."""
    persona_repo = PersonaRepository(db)
    personas = await persona_repo.get_active_by_person(person_id)

    responses = []
    for p in personas:
        # Convert the persona to dict and fix the metadata field name
        persona_dict = {
            "id": p.id,
            "person_id": p.person_id,
            "mapper_id": p.mapper_id,
            "mapper_config_id": p.mapper_config_id,
            "mapper_version": p.mapper_version,
            "core": p.core,
            "overlay": p.overlay,
            "metadata": p.meta,  # Map meta -> metadata
            "expires_at": p.expires_at,
            "created_at": p.created_at,
        }
        responses.append(PersonaResponse(**persona_dict))
    return responses


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

    # Convert to response with proper metadata mapping
    persona_dict = {
        "id": persona.id,
        "person_id": persona.person_id,
        "mapper_id": persona.mapper_id,
        "mapper_config_id": persona.mapper_config_id,
        "mapper_version": persona.mapper_version,
        "core": persona.core,
        "overlay": persona.overlay,
        "metadata": persona.meta,  # Map meta -> metadata
        "expires_at": persona.expires_at,
        "created_at": persona.created_at,
    }
    return PersonaResponse(**persona_dict)
