"""Tests for repository classes."""
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.observation import ObservationType
from src.repositories import (
    FeedbackRepository,
    MindscapeRepository,
    ObservationRepository,
    PersonaRepository,
)


@pytest.mark.asyncio
async def test_observation_repository_create(
    test_db: AsyncSession, test_observation_data: dict
):
    """Test creating an observation."""
    repo = ObservationRepository(test_db)
    
    observation = await repo.create(**test_observation_data)
    
    assert observation.id is not None
    assert observation.person_id == test_observation_data["person_id"]
    assert observation.type == ObservationType.WORK_SESSION
    assert observation.content == test_observation_data["content"]


@pytest.mark.asyncio
async def test_observation_repository_get_by_person(
    test_db: AsyncSession, test_person_id: uuid.UUID
):
    """Test getting observations by person."""
    repo = ObservationRepository(test_db)
    
    # Create multiple observations
    for i in range(3):
        await repo.create(
            person_id=test_person_id,
            type=ObservationType.WORK_SESSION,
            content={"session": i},
            meta={},
        )
    
    # Get observations
    observations = await repo.get_by_person(test_person_id)
    
    assert len(observations) == 3
    assert all(obs.person_id == test_person_id for obs in observations)


@pytest.mark.asyncio
async def test_mindscape_repository_upsert(
    test_db: AsyncSession, test_person_id: uuid.UUID
):
    """Test upserting a mindscape."""
    repo = MindscapeRepository(test_db)
    
    # Create new mindscape
    traits = {"focus_time": "morning", "productivity_style": "deep_work"}
    mindscape = await repo.upsert(test_person_id, traits)
    
    assert mindscape is not None
    assert mindscape.person_id == test_person_id
    assert mindscape.traits == traits
    assert mindscape.version == 1
    
    # Update existing mindscape
    updated_traits = {"focus_time": "afternoon", "productivity_style": "deep_work"}
    updated = await repo.upsert(test_person_id, updated_traits)
    
    assert updated is not None
    assert updated.version == 2
    assert updated.traits == updated_traits


@pytest.mark.asyncio
async def test_persona_repository_ttl(
    test_db: AsyncSession, test_person_id: uuid.UUID
):
    """Test persona TTL functionality."""
    repo = PersonaRepository(test_db)
    
    # Create expired persona
    expired = await repo.create(
        person_id=test_person_id,
        mapper_id="daily_optimizer",
        core={"type": "optimizer"},
        overlay={"focus": "productivity"},
        expires_at=datetime.now(UTC) - timedelta(hours=1),
    )
    
    # Create active persona
    active = await repo.create(
        person_id=test_person_id,
        mapper_id="daily_optimizer",
        core={"type": "optimizer"},
        overlay={"focus": "balance"},
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    
    # Get active personas
    active_personas = await repo.get_active(test_person_id)
    
    assert len(active_personas) == 1
    assert active_personas[0].id == active.id
    
    # Delete expired
    deleted_count = await repo.delete_expired()
    assert deleted_count == 1


@pytest.mark.asyncio
async def test_feedback_repository_stats(
    test_db: AsyncSession, test_person_id: uuid.UUID
):
    """Test feedback statistics."""
    # First create a persona
    persona_repo = PersonaRepository(test_db)
    persona = await persona_repo.create(
        person_id=test_person_id,
        mapper_id="test_mapper",
        core={},
        overlay={},
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    
    # Create feedback
    feedback_repo = FeedbackRepository(test_db)
    
    # Add some ratings
    await feedback_repo.create(persona_id=persona.id, rating=5, helpful=True)
    await feedback_repo.create(persona_id=persona.id, rating=4, helpful=True)
    await feedback_repo.create(persona_id=persona.id, rating=2, helpful=False)
    await feedback_repo.create(persona_id=persona.id, helpful=False)  # No rating
    
    # Get stats
    stats = await feedback_repo.get_feedback_stats(persona.id)
    
    assert stats["average_rating"] == pytest.approx(3.67, rel=0.01)
    assert stats["helpful_percentage"] == 50.0
    assert stats["total_feedback"] == 4
    
    # Count negative feedback
    negative_count = await feedback_repo.count_negative_feedback(persona.id)
    assert negative_count == 2  # rating=2 and helpful=False