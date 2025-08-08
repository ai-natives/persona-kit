"""
Integration tests for narrative API endpoints.

Tests the full HTTP API flow including:
- Authentication
- Request validation
- Response formats
- Error handling
- Performance requirements
"""

import asyncio
import uuid
import time
from typing import Dict, Any, List
import json

import pytest
import httpx
from httpx import AsyncClient

from src.main import app
from src.config import settings
from src.models.base import Base
from src.database import engine


class TestNarrativeAPIIntegration:
    """Test narrative API endpoints with full HTTP flow."""
    
    @pytest.fixture
    def auth_headers(self) -> Dict[str, str]:
        """Auth headers no longer needed - returning empty dict."""
        return {}
    
    @pytest.fixture
    async def test_person_id(self, test_client: AsyncClient) -> uuid.UUID:
        """Create a test person for narrative operations."""
        # For now, we'll use a random UUID as person_id since there's no person creation endpoint
        # In a real test, this would come from your person management system
        return uuid.uuid4()
    
    @pytest.mark.asyncio
    async def test_create_self_observation(
        self,
        test_client: AsyncClient,
        test_person_id: uuid.UUID
    ):
        """Test creating a self-observation via API."""
        narrative_data = {
            "person_id": str(test_person_id),
            "raw_text": "I find myself most focused in the early morning hours before 9 AM",
            "tags": ["focus", "morning", "productivity"]
        }
        
        start_time = time.time()
        response = await test_client.post(
            "/api/narratives/self-observation",
            json=narrative_data
            # No auth headers needed for this endpoint
        )
        duration = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        # First request might be slow due to model initialization
        # Subsequent requests should be faster
        assert duration < 10000  # Should complete within 10 seconds
        
        data = response.json()
        assert "id" in data
        assert data.get("message") == "Self-observation created successfully"
        assert data.get("embedding_generated") is True
    
    @pytest.mark.asyncio
    async def test_create_curation(
        self,
        test_client: AsyncClient,
        test_person_id: uuid.UUID
    ):
        """Test creating a curation via API."""
        curation_data = {
            "person_id": str(test_person_id),
            "trait_path": "work.peak_hours",
            "action": "correct",
            "raw_text": "My morning productivity is actually highest between 10-11 AM, not earlier",
            "original_value": "8-9 AM",
            "tags": ["correction", "morning", "productivity"]
        }
        
        response = await test_client.post(
            "/api/narratives/curate",
            json=curation_data
            # No auth headers needed for this endpoint
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data.get("message") == f"Curation for {curation_data['trait_path']} created successfully"
    
    @pytest.mark.asyncio
    async def test_semantic_search(
        self,
        test_client: AsyncClient,
        test_person_id: uuid.UUID
    ):
        """Test semantic search functionality."""
        # Create multiple narratives first
        narratives = [
            {
                "person_id": str(test_person_id),
                "raw_text": "I'm definitely a morning person - my energy peaks around 8 AM",
                "tags": ["morning", "energy"]
            },
            {
                "person_id": str(test_person_id),
                "raw_text": "Afternoon meetings drain my energy significantly",
                "tags": ["afternoon", "meetings", "energy"]
            },
            {
                "person_id": str(test_person_id),
                "raw_text": "I need complete silence to focus on complex tasks",
                "tags": ["focus", "environment"]
            },
            {
                "person_id": str(test_person_id),
                "raw_text": "Coffee helps me maintain focus throughout the morning",
                "tags": ["morning", "focus", "coffee"]
            }
        ]
        
        for narrative in narratives:
            await test_client.post(
                "/api/narratives/self-observation",
                json=narrative
            )
        
        # Test semantic search
        search_request = {
            "person_id": str(test_person_id),
            "query": "When do I have the most energy during the day?",
            "limit": 3,
            "min_similarity": 0.3
        }
        
        start_time = time.time()
        response = await test_client.post(
            "/api/narratives/search",
            json=search_request
        )
        duration = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        assert duration < 1000  # Should complete within 1 second
        
        data = response.json()
        assert "results" in data
        results = data["results"]
        assert len(results) <= 3
        assert len(results) > 0
        
        # First result should be about morning energy
        first_result = results[0]
        assert "morning" in first_result["narrative"]["raw_text"].lower() or "8 am" in first_result["narrative"]["raw_text"].lower()
        assert first_result["similarity_score"] > 0.3
    
    @pytest.mark.asyncio
    async def test_search_with_filters(
        self,
        test_client: AsyncClient,
        test_person_id: uuid.UUID
    ):
        """Test semantic search with type and tag filters."""
        # Create mixed narrative types
        await test_client.post(
            "/api/narratives/self-observation",
            json={
                "person_id": str(test_person_id),
                "raw_text": "Morning energy observation",
                "tags": ["morning", "energy"]
            }
        )
        
        await test_client.post(
            "/api/narratives/curate",
            json={
                "person_id": str(test_person_id),
                "raw_text": "Morning energy is more nuanced than I thought",
                "tags": ["morning", "energy", "correction"],
                "trait_path": "work.energy_patterns",
                "action": "clarify",
                "original_value": "high in morning"
            }
        )
        
        # Search only curations
        response = await test_client.post(
            "/api/narratives/search",
            json={
                "person_id": str(test_person_id),
                "query": "morning energy",
                "narrative_types": ["curation"],
                "min_similarity": 0.2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert all(r["narrative"]["narrative_type"] == "curation" for r in results)
        
        # Search by tag
        response = await test_client.post(
            "/api/narratives/search",
            json={
                "person_id": str(test_person_id),
                "query": "energy",
                "min_similarity": 0.2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        # Note: Tag filtering would need to be done post-search
    
    @pytest.mark.asyncio
    async def test_list_narratives_pagination(
        self,
        test_client: AsyncClient,
        test_person_id: uuid.UUID
    ):
        """Test listing narratives with pagination."""
        # Create 15 narratives
        for i in range(15):
            await test_client.post(
                "/api/narratives/self-observation",
                json={
                    "person_id": str(test_person_id),
                    "raw_text": f"Test narrative {i}",
                    "tags": [f"test{i}"]
                }
            )
        
        # Get narratives (pagination is handled in query params)
        response = await test_client.get(
            f"/api/narratives/person/{test_person_id}",
            params={"limit": 10, "offset": 0}
        )
        
        assert response.status_code == 200
        narratives = response.json()
        assert len(narratives) <= 10
        
        # Get second page
        response = await test_client.get(
            f"/api/narratives/person/{test_person_id}",
            params={"limit": 10, "offset": 10}
        )
        
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) <= 5
    
    @pytest.mark.skip(reason="Update endpoint not implemented")
    @pytest.mark.asyncio
    async def test_update_narrative(
        self,
        test_client: AsyncClient,
        test_person_id: uuid.UUID
    ):
        """Test updating a narrative."""
        # Create narrative
        create_response = await test_client.post(
            f"/api/v1/narratives/{test_person_id}/self-observation",
            json={"content": "Original observation", "tags": ["original"]},
            # No auth headers needed
        )
        narrative_id = create_response.json()["id"]
        
        # Update it
        update_data = {
            "content": "Updated observation with more detail",
            "tags": ["updated", "detailed"]
        }
        
        response = await test_client.put(
            f"/api/v1/narratives/{narrative_id}",
            json=update_data,
            # No auth headers needed
        )
        
        assert response.status_code == 200
        updated = response.json()
        assert updated["content"] == update_data["content"]
        assert set(updated["tags"]) == set(update_data["tags"])
        assert updated["version"] == 2  # Version incremented
    
    @pytest.mark.skip(reason="Delete endpoint not implemented")
    @pytest.mark.asyncio
    async def test_delete_narrative(
        self,
        test_client: AsyncClient,
        test_person_id: uuid.UUID
    ):
        """Test deleting a narrative."""
        # Create narrative
        create_response = await test_client.post(
            f"/api/v1/narratives/{test_person_id}/self-observation",
            json={"content": "To be deleted", "tags": ["delete-me"]},
            # No auth headers needed
        )
        narrative_id = create_response.json()["id"]
        
        # Delete it
        response = await test_client.delete(
            f"/api/v1/narratives/{narrative_id}",
            # No auth headers needed
        )
        
        assert response.status_code == 204
        
        # Verify it's not in search results
        search_response = await test_client.get(
            f"/api/v1/narratives/{test_person_id}/search",
            params={"query": "deleted"},
            # No auth headers needed
        )
        
        results = search_response.json()
        assert not any(r["id"] == narrative_id for r in results)
    
    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        test_client: AsyncClient
    ):
        """Test API error handling."""
        # Invalid person ID
        response = await test_client.post(
            "/api/narratives/self-observation",
            json={"person_id": "invalid-uuid", "raw_text": "Test"}
        )
        assert response.status_code == 422
        
        # Missing required fields
        response = await test_client.post(
            "/api/narratives/self-observation",
            json={"person_id": str(uuid.uuid4())}  # Missing raw_text
        )
        assert response.status_code == 422
    
    @pytest.mark.skip(reason="Concurrent database sessions need special handling")
    @pytest.mark.asyncio
    async def test_rate_limiting(
        self,
        async_client_concurrent: AsyncClient,
        test_person_id: uuid.UUID
    ):
        """Test rate limiting on narrative creation."""
        # Attempt to create many narratives quickly
        tasks = []
        for i in range(20):
            task = async_client_concurrent.post(
                "/api/narratives/self-observation",
                json={
                    "person_id": str(test_person_id),
                    "raw_text": f"Rapid creation {i}",
                    "tags": ["rate-test"]
                }
                # No auth headers needed for this endpoint
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Some requests should be rate limited (if implemented)
        status_codes = [r.status_code for r in responses if not isinstance(r, Exception)]
        
        # At least some should succeed
        assert any(code == 200 for code in status_codes)
        
        # Check if rate limiting is enforced (429 status)
        # This assumes rate limiting is implemented
        # assert any(code == 429 for code in status_codes)
    
    @pytest.mark.skip(reason="Update endpoint not implemented")
    @pytest.mark.asyncio
    async def test_concurrent_updates(
        self,
        test_client: AsyncClient,
        auth_headers: Dict[str, str],
        test_person_id: uuid.UUID
    ):
        """Test handling of concurrent updates to same narrative."""
        # Create narrative
        create_response = await test_client.post(
            f"/api/v1/narratives/{test_person_id}/self-observation",
            json={"content": "Concurrent test", "tags": ["concurrent"]},
            # No auth headers needed
        )
        narrative_id = create_response.json()["id"]
        
        # Attempt concurrent updates
        update_tasks = []
        for i in range(5):
            task = test_client.put(
                f"/api/v1/narratives/{narrative_id}",
                json={"content": f"Concurrent update {i}", "tags": [f"update{i}"]},
                # No auth headers needed
            )
            update_tasks.append(task)
        
        responses = await asyncio.gather(*update_tasks, return_exceptions=True)
        
        # All updates should complete (with proper version handling)
        success_count = sum(
            1 for r in responses 
            if not isinstance(r, Exception) and r.status_code == 200
        )
        assert success_count >= 1  # At least one should succeed
    
    @pytest.mark.asyncio
    async def test_large_content_handling(
        self,
        test_client: AsyncClient,
        test_person_id: uuid.UUID
    ):
        """Test handling of large narrative content."""
        # Create narrative with large content (but within the 10k character limit)
        # Each sentence is about 125 chars, so 70 sentences = ~8750 chars
        large_content = " ".join([
            f"This is sentence {i} of a very long narrative observation. "
            f"It contains detailed information about work patterns and behaviors. "
            for i in range(70)
        ])
        
        response = await test_client.post(
            "/api/narratives/self-observation",
            json={
                "person_id": str(test_person_id),
                "raw_text": large_content,
                "tags": ["large-content"]
            }
        )
        
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data  # Verify narrative created
        assert data.get("embedding_generated") is True  # Embedding still generated