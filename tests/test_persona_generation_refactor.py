"""Test the refactored persona generation endpoint."""
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from src.api.personas import (
    _fetch_mindscape,
    _prepare_context,
    _track_narrative_usage,
    _build_persona_response,
    generate_persona,
    PersonaGenerateRequest
)
from src.models.mindscape import Mindscape
from src.models.persona import Persona
from src.schemas.persona import PersonaResponse, NarrativeContext


@pytest.mark.asyncio
async def test_fetch_mindscape_success():
    """Test successful mindscape fetch."""
    # Mock data
    person_id = uuid.uuid4()
    mindscape = Mock(spec=Mindscape)
    
    # Mock repository
    db = AsyncMock()
    with patch('src.api.personas.MindscapeRepository') as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_person.return_value = mindscape
        mock_repo_class.return_value = mock_repo
        
        result = await _fetch_mindscape(db, person_id)
        
        assert result == mindscape
        mock_repo.get_by_person.assert_called_once_with(person_id)


@pytest.mark.asyncio
async def test_fetch_mindscape_not_found():
    """Test mindscape not found raises 404."""
    person_id = uuid.uuid4()
    
    # Mock repository
    db = AsyncMock()
    with patch('src.api.personas.MindscapeRepository') as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_person.return_value = None
        mock_repo_class.return_value = mock_repo
        
        with pytest.raises(HTTPException) as exc_info:
            await _fetch_mindscape(db, person_id)
        
        assert exc_info.value.status_code == 404
        assert f"No mindscape found for person {person_id}" in str(exc_info.value.detail)


def test_prepare_context_adds_current_time():
    """Test context preparation adds current time if missing."""
    context = {"some": "data"}
    result = _prepare_context(context)
    
    assert "current_time" in result
    assert isinstance(result["current_time"], datetime)
    assert result["some"] == "data"


def test_prepare_context_preserves_existing_time():
    """Test context preparation preserves existing current_time."""
    existing_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    context = {"current_time": existing_time, "other": "value"}
    
    result = _prepare_context(context)
    
    assert result["current_time"] == existing_time
    assert result["other"] == "value"


@pytest.mark.asyncio
async def test_track_narrative_usage_no_narratives():
    """Test tracking with no narrative usage."""
    db = AsyncMock()
    persona = Mock(spec=Persona)
    saved_persona = Mock(spec=Persona, id=uuid.uuid4())
    
    # No narrative usage
    persona._narrative_usage = []
    
    result = await _track_narrative_usage(db, persona, saved_persona)
    
    assert result == []
    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_track_narrative_usage_with_narratives():
    """Test tracking with narrative usage."""
    # Use Mock for sync method, not AsyncMock
    db = Mock()
    db.add = Mock()  # add is a sync method
    persona = Mock(spec=Persona)
    saved_persona = Mock(spec=Persona, id=uuid.uuid4())
    
    # Mock narrative usage
    narrative_id = uuid.uuid4()
    persona._narrative_usage = [{
        'id': str(narrative_id),
        'text': 'Test narrative',
        'score': 0.85,
        'type': 'self_observation',
        'rule_id': 'rule_123',
        'query': 'productivity'
    }]
    
    result = await _track_narrative_usage(db, persona, saved_persona)
    
    assert len(result) == 1
    assert isinstance(result[0], NarrativeContext)
    assert result[0].narrative_id == narrative_id
    assert result[0].text == 'Test narrative'
    assert result[0].relevance_score == 0.85
    assert result[0].narrative_type == 'self_observation'
    
    # Verify PersonaNarrativeUsage was added
    db.add.assert_called_once()


def test_build_persona_response():
    """Test building persona response with narrative context."""
    # Create a dict that mimics a Persona object for Pydantic validation
    saved_persona = Mock(
        spec=Persona,
        id=uuid.uuid4(),
        person_id=uuid.uuid4(),
        mapper_id="test_mapper",
        mapper_config_id=uuid.uuid4(),
        mapper_version="1.0",
        core={"traits": {}},
        overlay={"suggestions": []},
        expires_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        meta={"some": "metadata"}
    )
    # Make the mock return proper values when accessed
    saved_persona.metadata = None  # This will be overridden by meta
    
    narrative_contexts = [
        NarrativeContext(
            narrative_id=uuid.uuid4(),
            text="Test narrative",
            relevance_score=0.9,
            narrative_type="self_observation"
        )
    ]
    
    result = _build_persona_response(saved_persona, narrative_contexts)
    
    assert isinstance(result, PersonaResponse)
    assert result.narrative_context == narrative_contexts
    assert result.metadata == {"some": "metadata"}


@pytest.mark.asyncio
async def test_generate_persona_integration():
    """Test the full generate_persona flow with mocks."""
    # Setup test data
    person_id = uuid.uuid4()
    mapper_id = "test_mapper"
    
    request = PersonaGenerateRequest(
        person_id=person_id,
        mapper_id=mapper_id,
        context={},
        ttl_hours=24
    )
    
    db = AsyncMock()
    
    # Mock mindscape
    mindscape = Mock(spec=Mindscape)
    
    # Mock generated persona
    generated_persona = Mock(
        spec=Persona,
        person_id=person_id,
        mapper_id=mapper_id,
        mapper_config_id=uuid.uuid4(),
        mapper_version="1.0",
        core={"traits": {}},
        overlay={"suggestions": []},
        expires_at=datetime.now(UTC),
        meta={"test": "meta"},
        _narrative_usage=[]
    )
    
    # Mock saved persona
    saved_persona = Mock(
        spec=Persona,
        id=uuid.uuid4(),
        person_id=person_id,
        mapper_id=mapper_id,
        mapper_config_id=generated_persona.mapper_config_id,
        mapper_version="1.0",
        core={"traits": {}},
        overlay={"suggestions": []},
        expires_at=generated_persona.expires_at,
        created_at=datetime.now(UTC),
        meta={"test": "meta"}
    )
    saved_persona.metadata = None  # Will be overridden by meta
    
    with patch('src.api.personas._fetch_mindscape') as mock_fetch, \
         patch('src.api.personas._create_persona_generator') as mock_create_gen, \
         patch('src.api.personas.PersonaRepository') as mock_repo_class:
        
        # Setup mocks
        mock_fetch.return_value = mindscape
        
        mock_generator = AsyncMock()
        mock_generator.generate_persona.return_value = generated_persona
        mock_create_gen.return_value = mock_generator
        
        mock_repo = AsyncMock()
        mock_repo.create.return_value = saved_persona
        mock_repo_class.return_value = mock_repo
        
        # Call the endpoint (no auth required)
        result = await generate_persona(request, db)
        
        # Verify result
        assert isinstance(result, PersonaResponse)
        assert result.metadata == {"test": "meta"}
        
        # Verify calls
        mock_fetch.assert_called_once_with(db, person_id)
        mock_generator.generate_persona.assert_called_once()
        mock_repo.create.assert_called_once()