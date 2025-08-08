"""
Real tests for the narrative service that actually work.
"""
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.narrative_service import NarrativeService
from src.services.embedding_service import EmbeddingService
from src.schemas.narrative import CreateNarrativeRequest, CurationRequest, NarrativeSearchRequest


class TestNarrativeServiceReal:
    """Test the actual narrative service implementation."""
    
    @pytest.mark.asyncio
    async def test_create_self_observation(self, test_db: AsyncSession):
        """Test creating a self-observation."""
        # Create services
        embedding_service = EmbeddingService()
        narrative_service = NarrativeService(test_db, embedding_service)
        
        # Create request
        request = CreateNarrativeRequest(
            person_id=uuid.uuid4(),
            raw_text="I notice I'm most productive in the morning before 11am",
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
        assert len(narrative.embedding) == 1536  # Embedding dimension
        assert "productivity" in narrative.tags
    
    @pytest.mark.asyncio
    async def test_create_curation(self, test_db: AsyncSession):
        """Test creating a curation."""
        # Create services
        embedding_service = EmbeddingService()
        narrative_service = NarrativeService(test_db, embedding_service)
        
        # Create request
        request = CurationRequest(
            person_id=uuid.uuid4(),
            trait_path="work.peak_hours",
            action="correct",
            raw_text="My peak hours are actually 2-4 PM, not morning",
            original_value="morning",
            tags=["correction"]
        )
        
        # Create curation
        narrative = await narrative_service.create_curation(request)
        
        # Verify
        assert narrative.id is not None
        assert narrative.narrative_type == "curation"
        assert narrative.trait_path == "work.peak_hours"
        assert narrative.curation_action == "correct"
        assert "correction" in narrative.tags  # Our provided tag
    
    @pytest.mark.asyncio
    async def test_semantic_search(self, test_db: AsyncSession):
        """Test semantic search functionality."""
        # Create services
        embedding_service = EmbeddingService()
        narrative_service = NarrativeService(test_db, embedding_service)
        
        person_id = uuid.uuid4()
        
        # Create some narratives
        narratives = [
            ("I'm definitely a morning person - my energy peaks around 8 AM", ["morning", "energy"]),
            ("Afternoon meetings drain my energy significantly", ["afternoon", "meetings"]),
            ("I need complete silence to focus on complex tasks", ["focus", "environment"])
        ]
        
        for text, tags in narratives:
            request = CreateNarrativeRequest(
                person_id=person_id,
                raw_text=text,
                tags=tags,
                source="test"
            )
            await narrative_service.create_self_observation(request)
        
        # Search
        search_request = NarrativeSearchRequest(
            person_id=person_id,
            query="When do I have the most energy?",
            limit=2,
            min_similarity=0.3  # Lower threshold for local embeddings
        )
        
        results = await narrative_service.semantic_search(search_request)
        
        # Verify
        assert len(results) <= 2
        assert len(results) > 0
        
        # First result should be about morning energy
        first_result = results[0]
        assert "morning" in first_result.narrative.raw_text.lower() or "8 am" in first_result.narrative.raw_text.lower()
        assert first_result.similarity_score > 0.3  # Lower threshold for MiniLM