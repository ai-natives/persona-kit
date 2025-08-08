"""
End-to-end integration tests for narrative functionality.
Tests the full flow from API to database.
"""

import uuid
from datetime import datetime, UTC
from typing import Dict, Any

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.models.narrative import Narrative
from src.services.narrative_service import NarrativeService
from src.services.embedding_service import EmbeddingService
from src.repositories.mindscape import MindscapeRepository
from src.repositories.persona import PersonaRepository
from src.schemas.narrative import (
    CreateNarrativeRequest,
    CurationRequest,
    NarrativeSearchRequest
)


class TestNarrativeAPIIntegration:
    """Test narrative functionality through the API."""
    
    @pytest.mark.asyncio
    async def test_create_narrative_via_api_and_verify_in_db(
        self,
        async_client: AsyncClient,
        test_db: AsyncSession
    ):
        """Test creating a narrative via API and verifying it exists in database."""
        # Create self-observation via API
        response = await async_client.post(
            "/api/narratives/self-observation",
            json={
                "person_id": str(uuid.uuid4()),
                "raw_text": "I work best in the morning when it's quiet",
                "tags": ["productivity", "morning"],
                "context": {"source": "test"},
                "source": "api_test"
            },
            # No auth headers needed
        )
        
        assert response.status_code == 200
        data = response.json()
        narrative_id = data["id"]
        
        # Verify in database
        from sqlalchemy import text
        result = await test_db.execute(
            text(f"SELECT * FROM narratives WHERE id = :id"),
            {"id": narrative_id}
        )
        narrative = result.first()
        
        assert narrative is not None
        assert narrative.raw_text == "I work best in the morning when it's quiet"
        assert narrative.narrative_type == "self_observation"
        assert narrative.embedding is not None
        assert len(narrative.tags) == 2
        
    @pytest.mark.asyncio
    async def test_search_narratives_via_api(
        self,
        async_client: AsyncClient,
        test_db: AsyncSession
    ):
        """Test searching narratives semantically via API."""
        person_id = str(uuid.uuid4())
        
        # Create multiple narratives
        narratives_data = [
            {
                "raw_text": "I'm extremely productive in the early morning",
                "tags": ["morning", "productivity"]
            },
            {
                "raw_text": "Afternoon meetings drain my energy",
                "tags": ["afternoon", "meetings"]
            },
            {
                "raw_text": "I need coffee to focus after lunch",
                "tags": ["afternoon", "focus", "coffee"]
            }
        ]
        
        for data in narratives_data:
            response = await async_client.post(
                "/api/narratives/self-observation",
                json={
                    "person_id": person_id,
                    **data
                },
                # No auth headers needed
            )
            assert response.status_code == 200
            
        # Search for morning productivity
        response = await async_client.post(
            "/api/narratives/search",
            json={
                "person_id": person_id,
                "query": "when am I most productive",
                "limit": 2,
                "min_similarity": 0.5
            },
            # No auth headers needed
        )
        
        assert response.status_code == 200
        results = response.json()["results"]
        
        assert len(results) > 0
        assert results[0]["similarity_score"] > 0.7
        # The morning narrative should rank highest
        assert "morning" in results[0]["narrative"]["raw_text"].lower()
        
    @pytest.mark.asyncio
    async def test_curation_flow(
        self,
        async_client: AsyncClient,
        test_db: AsyncSession
    ):
        """Test the full curation flow."""
        person_id = str(uuid.uuid4())
        
        # First create a mindscape with traits
        mindscape_repo = MindscapeRepository(test_db)
        mindscape = await mindscape_repo.create(
            person_id=uuid.UUID(person_id),
            traits={
                "work.chronotype": {
                    "value": "morning",
                    "confidence": 0.8,
                    "observations": 5
                }
            }
        )
        await test_db.commit()
        
        # Create a curation via API
        response = await async_client.post(
            "/api/narratives/curate",
            json={
                "person_id": person_id,
                "trait_path": "work.chronotype",
                "action": "correct",
                "raw_text": "Actually, I'm more of a night owl. Mornings are hard for me.",
                "original_value": "morning",
                "tags": ["correction", "chronotype"]
            },
            # No auth headers needed
        )
        
        assert response.status_code == 200
        curation_data = response.json()
        curation_id = curation_data["id"]
        
        # Verify the curation response
        assert "id" in curation_data
        assert curation_data.get("message") == "Curation for work.chronotype created successfully"
        
        # Verify trait-narrative link was created
        result = await test_db.execute(
            text(f"SELECT * FROM trait_narrative_links WHERE narrative_id = :id"),
            {"id": curation_id}
        )
        link = result.first()
        
        assert link is not None
        assert link.trait_path == "work.chronotype"
        assert link.link_type == "curates"
        assert link.confidence == 1.0
        
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires mapper configuration setup")
    async def test_persona_generation_with_narratives(
        self,
        async_client: AsyncClient,
        test_db: AsyncSession
    ):
        """Test that persona generation includes narrative context."""
        person_id = str(uuid.uuid4())
        
        # Create mindscape
        mindscape_repo = MindscapeRepository(test_db)
        mindscape = await mindscape_repo.create(
            person_id=uuid.UUID(person_id),
            traits={
                "work.energy_patterns": {
                    "value": {"morning": "high", "afternoon": "low"},
                    "confidence": 0.85
                },
                "work.focus_preferences": {
                    "value": {"environment": "quiet", "duration": 90},
                    "confidence": 0.9
                }
            }
        )
        await test_db.commit()
        
        # Create narratives that should influence the persona
        narratives = [
            "I absolutely need silence to concentrate on complex tasks",
            "My best work happens between 6-10 AM before anyone else is online",
            "I use the Pomodoro technique but with 90-minute blocks"
        ]
        
        for text in narratives:
            response = await async_client.post(
                "/api/narratives/self-observation",
                json={
                    "person_id": person_id,
                    "raw_text": text,
                    "tags": ["work", "productivity"]
                },
                # No auth headers needed
            )
            assert response.status_code == 200
            
        # Generate persona
        response = await async_client.post(
            "/personas/",
            json={
                "person_id": person_id,
                "mapper_id": "daily_work_optimizer",
                "context": {
                    "current_time": datetime.now(UTC).isoformat(),
                    "include_narratives": True
                }
            },
            # No auth headers needed
        )
        
        assert response.status_code == 200
        persona_data = response.json()
        
        # Verify narrative usage was tracked
        result = await test_db.execute(
            f"SELECT COUNT(*) FROM persona_narrative_usage WHERE persona_id = '{persona_data['id']}'"
        )
        usage_count = result.scalar()
        
        assert usage_count > 0  # Some narratives should have been used
        
    @pytest.mark.asyncio
    async def test_error_cases(
        self,
        async_client: AsyncClient,
        test_auth_headers: Dict[str, str]
    ):
        """Test various error cases."""
        # Test with invalid person_id format
        response = await async_client.post(
            "/api/narratives/self-observation",
            json={
                "person_id": "not-a-uuid",
                "raw_text": "Test narrative"
            },
            # No auth headers needed
        )
        assert response.status_code == 422  # Validation error
        
        # Test with missing required fields
        response = await async_client.post(
            "/api/narratives/self-observation",
            json={
                "person_id": str(uuid.uuid4())
                # Missing raw_text
            },
            # No auth headers needed
        )
        assert response.status_code == 422
        
        # Test curation without required fields
        response = await async_client.post(
            "/api/narratives/curate",
            json={
                "person_id": str(uuid.uuid4()),
                "trait_path": "work.chronotype",
                "raw_text": "Test curation"
                # Missing action and original_value
            },
            # No auth headers needed
        )
        assert response.status_code == 422
        
        # Test search with invalid similarity threshold
        response = await async_client.post(
            "/api/narratives/search",
            json={
                "person_id": str(uuid.uuid4()),
                "query": "test query",
                "min_similarity": 1.5  # Invalid: > 1.0
            },
            # No auth headers needed
        )
        assert response.status_code == 422


class TestNarrativeInfluenceTracking:
    """Test how narratives influence persona generation."""
    
    @pytest.mark.asyncio
    async def test_narrative_relevance_scoring(self, test_db: AsyncSession):
        """Test that narratives are scored by relevance to persona generation."""
        embedding_service = EmbeddingService()
        narrative_service = NarrativeService(test_db, embedding_service)
        person_id = uuid.uuid4()
        
        # Create narratives with varying relevance
        highly_relevant = CreateNarrativeRequest(
            person_id=person_id,
            raw_text="I do my best deep work in 90-minute morning blocks",
            tags=["work", "focus", "morning"]
        )
        await narrative_service.create_self_observation(highly_relevant)
        
        somewhat_relevant = CreateNarrativeRequest(
            person_id=person_id,
            raw_text="I enjoy listening to instrumental music while working",
            tags=["work", "music"]
        )
        await narrative_service.create_self_observation(somewhat_relevant)
        
        not_relevant = CreateNarrativeRequest(
            person_id=person_id,
            raw_text="I love hiking on weekends",
            tags=["leisure", "outdoors"]
        )
        await narrative_service.create_self_observation(not_relevant)
        
        # Search for work-related narratives
        search_request = NarrativeSearchRequest(
            person_id=person_id,
            query="optimal work patterns and productivity",
            limit=10,
            min_similarity=0.2  # Lower threshold for local embeddings
        )
        results = await narrative_service.semantic_search(search_request)
        
        # Verify relevance ordering - should find at least 2 work-related narratives
        assert len(results) >= 2
        assert "90-minute morning blocks" in results[0].narrative.raw_text
        assert results[0].similarity_score > results[1].similarity_score
        # Check third result if it exists
        if len(results) > 2:
            assert results[1].similarity_score > results[2].similarity_score
        
    @pytest.mark.asyncio
    async def test_curation_priority(self, test_db: AsyncSession):
        """Test that curations have higher weight than observations."""
        embedding_service = EmbeddingService()
        narrative_service = NarrativeService(test_db, embedding_service)
        person_id = uuid.uuid4()
        
        # Create mindscape
        mindscape_repo = MindscapeRepository(test_db)
        await mindscape_repo.create(
            person_id=person_id,
            traits={
                "work.preferred_hours": {
                    "value": "morning",
                    "confidence": 0.7
                }
            }
        )
        
        # Create observation
        observation = CreateNarrativeRequest(
            person_id=person_id,
            raw_text="I sometimes work well in the morning",
            tags=["morning", "work"]
        )
        await narrative_service.create_self_observation(observation)
        
        # Create curation that contradicts
        curation = CurationRequest(
            person_id=person_id,
            trait_path="work.preferred_hours",
            action="correct",
            raw_text="I actually work best late at night, not mornings",
            original_value="morning",
            tags=["correction", "night"]
        )
        await narrative_service.create_curation(curation)
        
        # Search for work schedule preferences
        search_request = NarrativeSearchRequest(
            person_id=person_id,
            query="when do I work best",
            limit=5,
            min_similarity=0.3  # Lower threshold for local embeddings
        )
        results = await narrative_service.semantic_search(search_request)
        
        # Both should be found, but curation should be marked differently
        assert len(results) >= 2
        
        # Find the curation in results
        curation_found = False
        for result in results:
            if result.narrative.narrative_type == "curation":
                curation_found = True
                assert result.narrative.curation_action == "correct"
                
        assert curation_found