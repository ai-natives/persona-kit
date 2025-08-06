"""Feedback endpoints."""
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.persona import Persona
from ..repositories.feedback import FeedbackRepository
from ..repositories.persona import PersonaRepository
from ..schemas.feedback import FeedbackCreate, FeedbackResponse
from ..services.feedback_processor import FeedbackProcessor

router = APIRouter()

# In-memory rate limiting store (for simplicity - in production use Redis)
_rate_limit_store: dict[str, list[datetime]] = {}
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = timedelta(days=1)


def check_rate_limit(person_id: uuid.UUID) -> None:
    """Check if person has exceeded rate limit."""
    now = datetime.now(UTC)
    key = str(person_id)
    
    # Clean old entries
    if key in _rate_limit_store:
        _rate_limit_store[key] = [
            ts for ts in _rate_limit_store[key] 
            if now - ts < RATE_LIMIT_WINDOW
        ]
    
    # Check limit
    if key in _rate_limit_store and len(_rate_limit_store[key]) >= RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX} feedback per day."
        )
    
    # Record this request
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []
    _rate_limit_store[key].append(now)


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Submit feedback on a persona."""
    # Check persona exists
    persona_repo = PersonaRepository(session)
    persona = await persona_repo.get(feedback.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Check rate limit
    check_rate_limit(persona.person_id)
    
    # Add context from persona
    feedback_context = feedback.context.copy()
    feedback_context.update({
        "persona_mapper": persona.mapper_id,
        "persona_created_at": persona.created_at.isoformat(),
        "submission_time": datetime.now(UTC).isoformat(),
        "submission_hour": datetime.now(UTC).hour,
    })
    
    # Extract suggestion type if provided
    if "suggestion_id" in feedback.context:
        # Find the suggestion in persona overlay
        for suggestion in persona.overlay.get("suggestions", []):
            if suggestion.get("id") == feedback.context["suggestion_id"]:
                feedback_context["suggestion_type"] = suggestion.get("type")
                feedback_context["suggestion_title"] = suggestion.get("title")
                break
    
    # Create feedback
    feedback_repo = FeedbackRepository(session)
    db_feedback = await feedback_repo.create(
        persona_id=feedback.persona_id,
        rating=feedback.rating,
        helpful=feedback.helpful,
        context=feedback_context,
    )
    
    await session.commit()
    
    # Process feedback
    processor = FeedbackProcessor(session)
    await processor.process_feedback(db_feedback)
    await session.commit()
    
    return db_feedback


@router.get("/analytics")
async def get_feedback_analytics(
    person_id: uuid.UUID | None = None,
    mapper_id: str | None = None,
    days: int = 7,
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get feedback analytics.
    
    Query parameters:
    - person_id: Filter by specific person
    - mapper_id: Filter by specific mapper
    - days: Number of days to look back (default 7)
    """
    if not person_id and not mapper_id:
        raise HTTPException(
            status_code=400,
            detail="Either person_id or mapper_id must be provided"
        )
    
    processor = FeedbackProcessor(session)
    
    if person_id:
        # Get person-specific analytics
        return await processor.get_feedback_summary(person_id, days)
    
    # Get mapper-specific analytics (aggregate across all persons)
    from ..models.persona import Persona
    from sqlalchemy import distinct
    
    # Find all persons who have used this mapper
    stmt = select(distinct(Persona.person_id)).where(
        Persona.mapper_id == mapper_id
    )
    result = await session.execute(stmt)
    person_ids = result.scalars().all()
    
    # Aggregate analytics across all persons
    total_summary = {
        "mapper_id": mapper_id,
        "period_days": days,
        "total_persons": len(person_ids),
        "total_feedback": 0,
        "positive": 0,
        "negative": 0,
        "neutral": 0,
        "by_suggestion_type": {},
    }
    
    for pid in person_ids:
        person_summary = await processor.get_feedback_summary(pid, days)
        total_summary["total_feedback"] += person_summary["total_feedback"]
        total_summary["positive"] += person_summary["positive"]
        total_summary["negative"] += person_summary["negative"]
        total_summary["neutral"] += person_summary["neutral"]
        
        # Merge suggestion type stats
        for stype, stats in person_summary["by_suggestion_type"].items():
            if stype not in total_summary["by_suggestion_type"]:
                total_summary["by_suggestion_type"][stype] = {
                    "positive": 0, "negative": 0, "neutral": 0
                }
            for key, value in stats.items():
                total_summary["by_suggestion_type"][stype][key] += value
    
    # Calculate overall rates
    if total_summary["total_feedback"] > 0:
        total_summary["positive_rate"] = round(
            total_summary["positive"] / total_summary["total_feedback"] * 100, 1
        )
        total_summary["negative_rate"] = round(
            total_summary["negative"] / total_summary["total_feedback"] * 100, 1
        )
    else:
        total_summary["positive_rate"] = 0
        total_summary["negative_rate"] = 0
    
    return total_summary
