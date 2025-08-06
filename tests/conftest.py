"""Pytest configuration and fixtures."""
import asyncio
import uuid
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.models.base import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Start a PostgreSQL container for the test session."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        postgres.start()
        yield postgres


@pytest_asyncio.fixture
async def test_db(postgres_container: PostgresContainer) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with isolated PostgreSQL."""
    # Get connection URL from the container
    connection_url = postgres_container.get_connection_url()
    # Replace psycopg2 with asyncpg
    async_url = connection_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    
    engine = create_async_engine(
        async_url,
        echo=False,
    )
    
    # Create all tables for this test
    async with engine.begin() as conn:
        # First create the enum types
        await conn.execute(sa.text("""
            DO $$ BEGIN
                CREATE TYPE observation_type AS ENUM ('work_session', 'user_input', 'calendar_event');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        await conn.execute(sa.text("""
            DO $$ BEGIN
                CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'done', 'failed');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Then create tables
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()
    
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Cleanup
    await engine.dispose()


@pytest.fixture
def test_person_id() -> uuid.UUID:
    """Generate a test person ID."""
    return uuid.uuid4()


@pytest.fixture
def test_observation_data(test_person_id: uuid.UUID) -> dict:
    """Generate test observation data."""
    from src.models.observation import ObservationType
    
    return {
        "person_id": test_person_id,
        "type": ObservationType.WORK_SESSION,
        "content": {
            "duration_minutes": 45,
            "activity": "coding",
            "project": "PersonaKit",
        },
        "meta": {"source": "test"},
    }