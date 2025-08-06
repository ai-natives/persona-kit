"""Tests for persona mappers."""
import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from src.mappers import DailyWorkOptimizer
from src.models import Base
from src.models.mindscape import Mindscape
from src.repositories import MindscapeRepository, PersonaRepository


@pytest.fixture(scope="module")
def postgres_container():
    """Create a PostgreSQL test container."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        postgres.with_env("POSTGRES_PASSWORD", "test")
        yield postgres


@pytest.fixture
async def async_db_session(postgres_container):
    """Create an async database session for testing."""
    # Get container connection URL
    connection_url = postgres_container.get_connection_url()
    # Convert to async URL - need to handle psycopg2 -> asyncpg
    if "psycopg2" in connection_url:
        async_url = connection_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    else:
        async_url = connection_url.replace("postgresql://", "postgresql+asyncpg://")

    # Create async engine
    engine = create_async_engine(async_url)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Provide session
    async with async_session_factory() as session:
        yield session

    # Cleanup
    await engine.dispose()


@pytest.mark.asyncio
async def test_daily_work_optimizer_required_traits():
    """Test that DailyWorkOptimizer declares required traits."""
    mapper = DailyWorkOptimizer()
    required = mapper.get_required_traits()

    assert "work.energy_patterns" in required
    assert "work.focus_duration" in required
    assert "productivity.peak_hours" in required
    assert "work.task_switching_cost" in required
    assert "current_state.energy_level" in required
    assert len(required) == 5


@pytest.mark.asyncio
async def test_persona_generation_missing_traits(async_db_session):
    """Test persona generation fails with missing traits."""
    mapper = DailyWorkOptimizer()
    person_id = uuid.uuid4()

    # Create mindscape with incomplete traits
    mindscape = Mindscape(
        person_id=person_id,
        traits={"work.energy_patterns": {"value": []}},  # Missing other required traits
        version=1,
    )

    # Should raise ValueError for missing traits
    with pytest.raises(ValueError, match="Missing required traits"):
        mapper.create_persona(person_id, mindscape)


@pytest.mark.asyncio
async def test_persona_generation_success(async_db_session):
    """Test successful persona generation with all required traits."""
    mapper = DailyWorkOptimizer()
    person_id = uuid.uuid4()

    # Create mindscape with all required traits
    mindscape = Mindscape(
        person_id=person_id,
        traits={
            "work.energy_patterns": {
                "value": {
                    "high_energy_slots": ["09:00-11:00", "14:00-16:00"],
                    "low_energy_slots": ["13:00-14:00"],
                },
                "confidence": 0.8,
            },
            "work.focus_duration": {
                "value": {"p50": 60, "p90": 90, "recent_trend": "stable"},
                "confidence": 0.9,
            },
            "productivity.peak_hours": {
                "value": ["09:00-11:00"],
                "confidence": 0.7,
            },
            "work.task_switching_cost": {
                "value": "high",
                "confidence": 0.8,
            },
            "current_state.energy_level": {
                "value": "high",
                "confidence": 1.0,
            },
        },
        version=1,
    )

    # Generate persona
    persona = mapper.create_persona(person_id, mindscape)

    assert persona.person_id == person_id
    assert persona.mapper_id == "daily_work_optimizer"
    assert persona.core is not None
    assert persona.overlay is not None
    assert persona.expires_at > datetime.now(UTC)


@pytest.mark.asyncio
async def test_time_context_handling(async_db_session):
    """Test that mapper handles time-of-day context correctly."""
    mapper = DailyWorkOptimizer()
    person_id = uuid.uuid4()

    # Create mindscape
    mindscape = Mindscape(
        person_id=person_id,
        traits={
            "work.energy_patterns": {
                "value": {
                    "high_energy_slots": ["09:00-11:00", "14:00-16:00"],
                    "low_energy_slots": ["13:00-14:00"],
                },
            },
            "work.focus_duration": {"value": {"p50": 60, "p90": 90}},
            "productivity.peak_hours": {"value": ["09:00-11:00"]},
            "work.task_switching_cost": {"value": "medium"},
            "current_state.energy_level": {"value": "medium"},
        },
        version=1,
    )

    # Test morning context (high energy time)
    morning_context = {
        "current_time": datetime.now(UTC).replace(hour=10, minute=0)
    }
    morning_persona = mapper.create_persona(
        person_id, mindscape, context=morning_context
    )

    assert morning_persona.overlay["current_state"]["energy_level"] == "high"
    assert morning_persona.overlay["current_state"]["is_peak_time"] is True

    # Test afternoon low energy time
    afternoon_context = {
        "current_time": datetime.now(UTC).replace(hour=13, minute=30)
    }
    afternoon_persona = mapper.create_persona(
        person_id, mindscape, context=afternoon_context
    )

    assert afternoon_persona.overlay["current_state"]["energy_level"] == "low"
    assert afternoon_persona.overlay["current_state"]["is_peak_time"] is False


@pytest.mark.asyncio
async def test_suggestion_generation(async_db_session):
    """Test that suggestions are generated based on context."""
    mapper = DailyWorkOptimizer()
    person_id = uuid.uuid4()

    mindscape = Mindscape(
        person_id=person_id,
        traits={
            "work.energy_patterns": {
                "value": {
                    "high_energy_slots": ["09:00-11:00"],
                    "low_energy_slots": ["13:00-14:00"],
                },
            },
            "work.focus_duration": {"value": {"p50": 60, "p90": 90}},
            "productivity.peak_hours": {"value": ["09:00-11:00"]},
            "work.task_switching_cost": {"value": "high"},
            "current_state.energy_level": {"value": "high"},
        },
        version=1,
    )

    # High energy context
    high_energy_context = {
        "current_time": datetime.now(UTC).replace(hour=10, minute=0)
    }
    persona = mapper.create_persona(person_id, mindscape, context=high_energy_context)

    suggestions = persona.overlay["suggestions"]
    assert len(suggestions) > 0

    # Should have deep work suggestion during high energy
    deep_work_suggestions = [s for s in suggestions if s["type"] == "task_recommendation"]
    assert len(deep_work_suggestions) > 0
    assert "Deep Work" in deep_work_suggestions[0]["title"]


@pytest.mark.asyncio
async def test_meeting_buffer_calculation(async_db_session):
    """Test meeting buffer time is calculated based on task switching cost."""
    mapper = DailyWorkOptimizer()
    person_id = uuid.uuid4()

    # High task switching cost
    high_cost_mindscape = Mindscape(
        person_id=person_id,
        traits={
            "work.energy_patterns": {"value": {}},
            "work.focus_duration": {"value": {"p50": 60, "p90": 90}},
            "productivity.peak_hours": {"value": []},
            "work.task_switching_cost": {"value": "high"},
            "current_state.energy_level": {"value": "medium"},
        },
        version=1,
    )

    high_cost_persona = mapper.create_persona(person_id, high_cost_mindscape)
    assert high_cost_persona.core["preferences"]["meeting_buffer_time"] == 30

    # Low task switching cost
    low_cost_mindscape = Mindscape(
        person_id=person_id,
        traits={
            "work.energy_patterns": {"value": {}},
            "work.focus_duration": {"value": {"p50": 60, "p90": 90}},
            "productivity.peak_hours": {"value": []},
            "work.task_switching_cost": {"value": "low"},
            "current_state.energy_level": {"value": "medium"},
        },
        version=1,
    )

    low_cost_persona = mapper.create_persona(person_id, low_cost_mindscape)
    assert low_cost_persona.core["preferences"]["meeting_buffer_time"] == 5


@pytest.mark.asyncio
async def test_ttl_override(async_db_session):
    """Test TTL can be overridden when creating persona."""
    mapper = DailyWorkOptimizer()
    person_id = uuid.uuid4()

    mindscape = Mindscape(
        person_id=person_id,
        traits={
            "work.energy_patterns": {"value": {}},
            "work.focus_duration": {"value": {"p50": 60, "p90": 90}},
            "productivity.peak_hours": {"value": []},
            "work.task_switching_cost": {"value": "medium"},
            "current_state.energy_level": {"value": "medium"},
        },
        version=1,
    )

    # Default TTL (24 hours)
    default_persona = mapper.create_persona(person_id, mindscape)
    default_expiry = default_persona.expires_at

    # Custom TTL (48 hours)
    custom_persona = mapper.create_persona(person_id, mindscape, ttl_hours=48)
    custom_expiry = custom_persona.expires_at

    # Check custom TTL is longer
    time_diff = (custom_expiry - default_expiry).total_seconds() / 3600
    assert 23 < time_diff < 25  # Approximately 24 hours difference


@pytest.mark.asyncio
async def test_persona_api_integration(async_db_session):
    """Test full integration with persona API."""
    # Create repositories
    mindscape_repo = MindscapeRepository(async_db_session)
    persona_repo = PersonaRepository(async_db_session)

    person_id = uuid.uuid4()

    # Create mindscape with traits
    traits = {
        "work.energy_patterns": {
            "value": {
                "high_energy_slots": ["09:00-11:00"],
                "low_energy_slots": [],
            },
            "confidence": 0.8,
        },
        "work.focus_duration": {
            "value": {"p50": 75, "p90": 120, "recent_trend": "increasing"},
            "confidence": 0.9,
        },
        "productivity.peak_hours": {
            "value": ["09:00-11:00", "14:00-16:00"],
            "confidence": 0.7,
        },
        "work.task_switching_cost": {
            "value": "medium",
            "confidence": 0.8,
        },
        "current_state.energy_level": {
            "value": "high",
            "confidence": 1.0,
        },
    }

    mindscape = await mindscape_repo.upsert(person_id, traits)

    # Generate persona using mapper
    mapper = DailyWorkOptimizer()
    context = {"current_time": datetime.now(UTC).replace(hour=10)}

    persona = mapper.create_persona(
        person_id=person_id,
        mindscape=mindscape,
        context=context,
    )

    # Save persona
    saved_persona = await persona_repo.create(
        person_id=persona.person_id,
        mapper_id=persona.mapper_id,
        core=persona.core,
        overlay=persona.overlay,
        expires_at=persona.expires_at,
    )

    # Verify saved correctly
    assert saved_persona.id is not None
    assert saved_persona.mapper_id == "daily_work_optimizer"
    assert saved_persona.core["work_style"]["focus_blocks"]["default"] == 75
    assert saved_persona.overlay["current_state"]["energy_level"] == "high"

    # Check persona is active
    active_personas = await persona_repo.get_active(person_id)
    assert len(active_personas) == 1
    assert active_personas[0].id == saved_persona.id
