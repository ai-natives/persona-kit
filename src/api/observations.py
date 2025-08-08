"""Observation endpoints."""
import logging
from datetime import UTC, datetime, timedelta
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.observation import ObservationType
from ..repositories import ObservationRepository, OutboxTaskRepository
from ..schemas.observation import ObservationCreate, ObservationResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ObservationResponse)
async def create_observation(
    observation_data: ObservationCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new observation and queue for processing.

    This endpoint:
    1. Validates the observation data
    2. Stores it in the database
    3. Queues it for async processing
    4. Returns immediately (< 200ms target)
    """
    # Validate observation type (basic validation)
    if observation_data.type not in [ObservationType.WORK_SESSION, ObservationType.USER_INPUT]:
        # We're focusing on these two types in v0.1
        logger.warning(
            f"Unsupported observation type: {observation_data.type}",
            extra={"person_id": str(observation_data.person_id)},
        )

    # Validate timestamp if present (not too far in future)
    if timestamp := observation_data.content.get("timestamp"):
        try:
            # Parse timestamp
            if isinstance(timestamp, str):
                obs_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                obs_time = timestamp

            # Check not too far in future (1 hour tolerance)
            if obs_time > datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1):
                raise HTTPException(
                    status_code=400,
                    detail="Observation timestamp cannot be more than 1 hour in the future",
                )
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid timestamp format: {e}")

    try:
        # Create observation
        observation_repo = ObservationRepository(db)
        observation = await observation_repo.create(
            person_id=observation_data.person_id,
            type=observation_data.type,
            content=observation_data.content,
            meta=observation_data.meta,
        )

        # Queue for processing
        outbox_repo = OutboxTaskRepository(db)
        await outbox_repo.enqueue(
            task_type="process_observation",
            payload={"observation_id": str(observation.id)},
        )

        logger.info(
            "Observation created and queued",
            extra={
                "observation_id": str(observation.id),
                "person_id": str(observation.person_id),
                "type": observation.type,
            },
        )

        return observation

    except Exception as e:
        logger.error(f"Failed to create observation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create observation",
        ) from e


@router.get("/", response_model=List[ObservationResponse])
async def list_observations(
    person_id: Optional[UUID] = Query(None, description="Filter by person ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of observations to return"),
    offset: int = Query(0, ge=0, description="Number of observations to skip"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    List observations with optional filtering.
    
    This endpoint returns recent observations, ordered by created_at descending.
    """
    try:
        observation_repo = ObservationRepository(db)
        
        # For now, we'll use a simple query
        # In a real implementation, this would be a proper repository method
        from sqlalchemy import select, desc
        from ..models.observation import Observation
        
        query = select(Observation).order_by(desc(Observation.created_at))
        
        if person_id:
            query = query.filter(Observation.person_id == person_id)
            
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        observations = result.scalars().all()
        
        return observations
        
    except Exception as e:
        logger.error(f"Failed to list observations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to list observations",
        ) from e
