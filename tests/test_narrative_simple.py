"""
Simple narrative tests that actually work.
"""
import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.narrative_service import NarrativeService
from src.services.embedding_service import EmbeddingService
from src.schemas.narrative import CreateNarrativeRequest


@pytest.mark.asyncio
async def test_create_narrative(test_db: AsyncSession):
    """Test creating a simple narrative."""
    # Create services
    embedding_service = EmbeddingService()
    narrative_service = NarrativeService(test_db, embedding_service)
    
    # Create request
    request = CreateNarrativeRequest(
        person_id=uuid.uuid4(),
        raw_text="I am most productive in the morning",
        tags=["productivity", "morning"],
        source="test"
    )
    
    # Create narrative
    narrative = await narrative_service.create_self_observation(request)
    
    # Verify
    assert narrative.id is not None
    assert narrative.person_id == request.person_id
    assert narrative.narrative_type == "self_observation"
    assert narrative.raw_text == request.raw_text
    assert narrative.embedding is not None
    assert len(narrative.embedding) == 1536
    assert "productivity" in narrative.tags
    
    print(f"✅ Created narrative {narrative.id}")
    print(f"✅ Embedding dimension: {len(narrative.embedding)}")
    print(f"✅ Tags: {narrative.tags}")