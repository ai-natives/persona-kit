"""Pytest configuration and fixtures."""
import asyncio
import uuid
from typing import AsyncGenerator, Generator

import httpx
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
    with PostgresContainer("pgvector/pgvector:pg16") as postgres:
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
        
        # Create pgvector extension
        await conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
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
    
    # Drop all tables after test in correct order to handle dependencies
    async with engine.begin() as conn:
        # Drop dependent tables first
        await conn.execute(sa.text("DROP TABLE IF EXISTS persona_narrative_usage CASCADE"))
        await conn.execute(sa.text("DROP TABLE IF EXISTS trait_narrative_links CASCADE"))
        await conn.execute(sa.text("DROP TABLE IF EXISTS narratives CASCADE"))
        await conn.execute(sa.text("DROP TABLE IF EXISTS feedback CASCADE"))
        await conn.execute(sa.text("DROP TABLE IF EXISTS mindscapes CASCADE"))
        await conn.execute(sa.text("DROP TABLE IF EXISTS observations CASCADE"))
        await conn.execute(sa.text("DROP TABLE IF EXISTS outbox_tasks CASCADE"))
        await conn.execute(sa.text("DROP TABLE IF EXISTS personas CASCADE"))
        await conn.execute(sa.text("DROP TABLE IF EXISTS users CASCADE"))
        await conn.execute(sa.text("DROP TABLE IF EXISTS mapper_configs CASCADE"))
        await conn.execute(sa.text("DROP TYPE IF EXISTS mapperstatus CASCADE"))
        await conn.execute(sa.text("DROP TYPE IF EXISTS observation_type CASCADE"))
        await conn.execute(sa.text("DROP TYPE IF EXISTS task_status CASCADE"))
    
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


@pytest_asyncio.fixture
async def async_client(test_db: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async test client for API testing."""
    from src.main import app
    from src.database import get_db
    
    # Override the database dependency to use test database
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
        
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client_concurrent() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async test client for concurrent API testing.
    
    This fixture creates a new database session for each request,
    allowing concurrent requests without session conflicts.
    """
    from src.main import app
    from src.database import async_session_maker, get_db
    
    # Create a new session for each request
    async def override_get_db():
        async with async_session_maker() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
        
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_client(test_db: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Alias for async_client for backwards compatibility."""
    from src.main import app
    from src.database import get_db
    
    # Override the database dependency to use test database
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
        
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_auth_headers() -> dict:
    """Auth headers no longer needed - returning empty dict for compatibility."""
    return {}


@pytest.fixture
def auth_headers() -> dict:
    """Auth headers no longer needed - returning empty dict for compatibility."""
    return {}