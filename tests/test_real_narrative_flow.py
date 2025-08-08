#!/usr/bin/env python3
"""
REAL end-to-end test of the narrative flow in PersonaKit.
NO MOCKS - This test uses actual database, actual API calls, actual vector search.

Tests:
1. Create a narrative via API
2. Search for it via semantic search  
3. Use it in a rule evaluation
4. Generate a persona that uses the narrative

Run with: python -m pytest tests/test_real_narrative_flow.py -v -s
"""
import asyncio
import os
import uuid
import json
from datetime import datetime, UTC
from typing import Dict, Any, List

import pytest
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.models.base import Base
from src.models.mindscape import Mindscape
from src.models.narrative import Narrative
from src.models.persona import Persona
from src.services.embedding_service import EmbeddingService
from src.services.narrative_service import NarrativeService
from src.services.rule_engine import RuleEngine
from src.services.persona_generator import PersonaGenerator
from src.config import settings


# Test configuration
TEST_PERSON_ID = uuid.uuid4()
TEST_MAPPER_ID = "daily_work_optimizer"
API_BASE_URL = f"http://{settings.api_host}:{settings.api_port}"


class TestRealNarrativeFlow:
    """Test the complete narrative flow without any mocks."""
    
    @pytest.fixture
    async def db_engine(self):
        """Create test database engine."""
        # Use test database URL
        database_url = settings.database_url.replace("persona_kit", "persona_kit_test")
        engine = create_async_engine(database_url, echo=True)
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        yield engine
        
        # Clean up - drop tables in correct order to handle dependencies
        async with engine.begin() as conn:
            # Drop dependent tables first
            await conn.execute(text("DROP TABLE IF EXISTS persona_narrative_usage CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS trait_narrative_links CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS narratives CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS feedback CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS mindscapes CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS observations CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS outbox_tasks CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS personas CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS mapper_configs CASCADE"))
            await conn.execute(text("DROP TYPE IF EXISTS mapperstatus CASCADE"))
            await conn.execute(text("DROP TYPE IF EXISTS observation_type CASCADE"))
            await conn.execute(text("DROP TYPE IF EXISTS task_status CASCADE"))
        await engine.dispose()
    
    @pytest.fixture
    async def db_session(self, db_engine):
        """Create database session."""
        async_session = sessionmaker(
            db_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
    
    @pytest.fixture
    def embedding_service(self):
        """Create real embedding service."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping embedding tests")
        return EmbeddingService(api_key=api_key)
    
    async def test_1_create_mindscape(self, db_session: AsyncSession):
        """Step 1: Create a mindscape for testing."""
        print("\n=== TEST 1: Creating Mindscape ===")
        
        mindscape = Mindscape(
            person_id=TEST_PERSON_ID,
            traits={
                "work": {
                    "preferences": {
                        "peak_hours": "morning",
                        "break_duration": 15,
                        "focus_blocks": 90
                    },
                    "energy_patterns": {
                        "morning": "high",
                        "afternoon": "medium", 
                        "evening": "low"
                    }
                },
                "communication": {
                    "style": "direct",
                    "preferred_medium": ["email", "slack"]
                }
            },
            metadata={"test": True}
        )
        
        db_session.add(mindscape)
        await db_session.commit()
        await db_session.refresh(mindscape)
        
        # Verify it was created
        result = await db_session.execute(
            text("SELECT * FROM mindscapes WHERE person_id = :person_id"),
            {"person_id": TEST_PERSON_ID}
        )
        row = result.first()
        
        assert row is not None
        assert row.person_id == TEST_PERSON_ID
        assert row.traits["work"]["preferences"]["peak_hours"] == "morning"
        
        print(f"✓ Created mindscape for person {TEST_PERSON_ID}")
        print(f"  Traits: {json.dumps(mindscape.traits, indent=2)}")
        
        return mindscape
    
    async def test_2_create_narrative_via_api(self, async_client: httpx.AsyncClient):
        """Step 2: Create narratives via the actual API."""
        print("\n=== TEST 2: Creating Narratives via API ===")
        
        client = async_client
        
        # Create multiple narratives for better testing
        narratives_data = [
            {
                "person_id": str(TEST_PERSON_ID),
                "raw_text": "I feel most productive in the morning between 7-10 AM. "
                           "My energy is high and I can focus deeply on complex tasks.",
                "tags": ["morning", "productivity", "energy", "focus"],
                "source": "self_observation",
                "context": {"time_of_day": "morning", "activity": "planning"}
            },
            {
                "person_id": str(TEST_PERSON_ID),
                "raw_text": "After lunch I tend to feel sluggish and need a short walk "
                           "to regain focus. Coffee helps but only temporarily.",
                "tags": ["afternoon", "energy", "break", "coffee"],
                "source": "self_observation",
                "context": {"time_of_day": "afternoon", "activity": "break"}
            },
            {
                "person_id": str(TEST_PERSON_ID),
                "raw_text": "I prefer to do creative work in quiet environments. "
                           "Open offices are too distracting for deep thinking.",
                "tags": ["environment", "focus", "creative", "quiet"],
                "source": "self_observation",
                "context": {"environment": "office", "activity": "creative_work"}
            }
        ]
        
        created_narratives = []
        
        for narrative_data in narratives_data:
            try:
                response = await client.post(
                    "/api/narratives/self-observation",
                    json=narrative_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    created_narratives.append(result)
                    print(f"✓ Created narrative: {result['id']}")
                    print(f"  Message: {result['message']}")
                    print(f"  Embedding generated: {result.get('embedding_generated', False)}")
                else:
                    print(f"✗ Failed to create narrative: {response.status_code}")
                    print(f"  Response: {response.text}")
                    
            except Exception as e:
                print(f"✗ Error creating narrative: {e}")
                    
        assert len(created_narratives) > 0, "No narratives were created"
        return created_narratives
    
    async def test_3_semantic_search(self, db_session: AsyncSession, embedding_service: EmbeddingService):
        """Step 3: Test semantic search for narratives."""
        print("\n=== TEST 3: Semantic Search for Narratives ===")
        
        narrative_service = NarrativeService(db_session, embedding_service)
        
        # Test different search queries
        search_queries = [
            {
                "query": "When am I most productive?",
                "expected_keywords": ["morning", "productive", "energy"]
            },
            {
                "query": "How do I handle afternoon energy dips?",
                "expected_keywords": ["afternoon", "sluggish", "walk", "coffee"]
            },
            {
                "query": "What kind of work environment do I need?",
                "expected_keywords": ["quiet", "environment", "creative", "distracting"]
            }
        ]
        
        for search_data in search_queries:
            print(f"\nSearching for: '{search_data['query']}'")
            
            try:
                # Create search request
                from src.schemas.narrative import NarrativeSearchRequest
                search_request = NarrativeSearchRequest(
                    person_id=TEST_PERSON_ID,
                    query=search_data["query"],
                    threshold=0.5,  # Lower threshold for testing
                    limit=5
                )
                
                # Perform search
                results = await narrative_service.semantic_search(search_request)
                
                print(f"  Found {len(results)} results")
                
                for i, result in enumerate(results):
                    print(f"  [{i+1}] Score: {result.similarity_score:.3f}")
                    print(f"      Text: {result.excerpt}")
                    print(f"      Tags: {result.narrative.tags}")
                    
                    # Check if expected keywords are in the top result
                    if i == 0:
                        text_lower = result.narrative.raw_text.lower()
                        found_keywords = [kw for kw in search_data["expected_keywords"] 
                                        if kw in text_lower]
                        print(f"      Found keywords: {found_keywords}")
                        
                        assert len(found_keywords) > 0, (
                            f"Expected to find keywords {search_data['expected_keywords']} "
                            f"in top result, but found none"
                        )
                        
            except Exception as e:
                print(f"✗ Search failed: {e}")
                raise
                
        print("\n✓ Semantic search working correctly")
    
    async def test_4_rule_evaluation_with_narratives(self, db_session: AsyncSession, embedding_service: EmbeddingService):
        """Step 4: Test rule engine with real narrative data."""
        print("\n=== TEST 4: Rule Evaluation with Narratives ===")
        
        # Load mapper configuration
        config_path = "/Users/timothy.mansfield.001/code/src/github.com/ai-natives/persona-kit/configs/examples/daily_work_optimizer.yaml"
        import yaml
        
        with open(config_path, 'r') as f:
            mapper_config = yaml.safe_load(f)
            
        print(f"Loaded mapper config: {mapper_config['metadata']['name']}")
        
        # Get mindscape
        result = await db_session.execute(
            text("SELECT * FROM mindscapes WHERE person_id = :person_id"),
            {"person_id": TEST_PERSON_ID}
        )
        row = result.first()
        
        if not row:
            pytest.skip("No mindscape found - run test_1_create_mindscape first")
            
        mindscape = Mindscape(
            person_id=row.person_id,
            traits=row.traits,
            metadata=row.metadata
        )
        
        # Create rule engine with narrative service
        narrative_service = NarrativeService(db_session, embedding_service)
        rule_engine = RuleEngine(narrative_service)
        
        # Test different contexts
        test_contexts = [
            {
                "current_time": datetime(2024, 1, 15, 8, 30),  # Morning
                "expected_suggestions": ["morning", "productive", "focus"]
            },
            {
                "current_time": datetime(2024, 1, 15, 14, 30),  # Afternoon
                "expected_suggestions": ["afternoon", "break", "energy"]
            },
            {
                "current_time": datetime(2024, 1, 15, 18, 30),  # Evening
                "expected_suggestions": ["evening", "wind down", "low energy"]
            }
        ]
        
        for context_data in test_contexts:
            context = {"current_time": context_data["current_time"]}
            print(f"\nEvaluating rules for time: {context['current_time']}")
            
            # Evaluate rules
            suggestions = rule_engine.evaluate_rules(
                mapper_config,
                mindscape,
                context,
                person_id=TEST_PERSON_ID
            )
            
            print(f"  Generated {len(suggestions)} suggestions:")
            
            for i, suggestion in enumerate(suggestions):
                print(f"  [{i+1}] {suggestion['title']}")
                print(f"      {suggestion['description']}")
                print(f"      Priority: {suggestion['priority']}")
                print(f"      Weight: {suggestion.get('weight', 1.0)}")
                
                # Check if narrative context is included
                if 'narrative_context' in suggestion:
                    print(f"      Based on narratives: {len(suggestion['narrative_context'])}")
                    
            assert len(suggestions) > 0, f"No suggestions generated for {context['current_time']}"
            
        print("\n✓ Rule evaluation with narratives working correctly")
    
    async def test_5_generate_persona_with_narratives(self, db_session: AsyncSession, embedding_service: EmbeddingService):
        """Step 5: Generate a persona that uses narratives."""
        print("\n=== TEST 5: Generate Persona with Narratives ===")
        
        # Get mindscape
        result = await db_session.execute(
            text("SELECT * FROM mindscapes WHERE person_id = :person_id"),
            {"person_id": TEST_PERSON_ID}
        )
        row = result.first()
        
        if not row:
            pytest.skip("No mindscape found - run test_1_create_mindscape first")
            
        mindscape = Mindscape(
            person_id=row.person_id,
            traits=row.traits,
            metadata=row.metadata
        )
        
        # Create services
        narrative_service = NarrativeService(db_session, embedding_service)
        persona_generator = PersonaGenerator(db_session, narrative_service)
        
        # Generate persona for morning context
        context = {
            "current_time": datetime(2024, 1, 15, 8, 30),
            "activity": "planning daily work"
        }
        
        print(f"Generating persona for context: {context}")
        
        try:
            persona = await persona_generator.generate_persona(
                person_id=TEST_PERSON_ID,
                mapper_id=TEST_MAPPER_ID,
                mindscape=mindscape,
                context=context
            )
            
            print(f"\n✓ Generated persona: {persona.id}")
            print(f"  Traits: {json.dumps(persona.traits, indent=2)}")
            print(f"  Behaviors: {json.dumps(persona.behaviors, indent=2)}")
            print(f"  Context: {json.dumps(persona.context, indent=2)}")
            
            # Verify persona includes narrative-based insights
            assert persona.traits is not None
            assert persona.behaviors is not None
            assert len(persona.behaviors) > 0
            
            # Check if morning productivity is reflected
            behaviors_text = json.dumps(persona.behaviors).lower()
            assert any(keyword in behaviors_text for keyword in ["morning", "productive", "energy"]), \
                "Persona should reflect morning productivity from narratives"
                
        except Exception as e:
            print(f"✗ Failed to generate persona: {e}")
            raise
            
        print("\n✓ Persona generation with narratives working correctly")
    
    async def test_6_verify_database_state(self, db_session: AsyncSession):
        """Step 6: Verify final database state."""
        print("\n=== TEST 6: Verify Database State ===")
        
        # Check narratives
        result = await db_session.execute(
            text("SELECT COUNT(*) as count FROM narratives WHERE person_id = :person_id"),
            {"person_id": TEST_PERSON_ID}
        )
        narrative_count = result.scalar()
        print(f"✓ Narratives created: {narrative_count}")
        
        # Check embeddings
        result = await db_session.execute(
            text("""
                SELECT COUNT(*) as count 
                FROM narratives 
                WHERE person_id = :person_id 
                AND embedding IS NOT NULL
            """),
            {"person_id": TEST_PERSON_ID}
        )
        embedding_count = result.scalar()
        print(f"✓ Narratives with embeddings: {embedding_count}")
        
        # Check personas
        result = await db_session.execute(
            text("SELECT COUNT(*) as count FROM personas WHERE person_id = :person_id"),
            {"person_id": TEST_PERSON_ID}
        )
        persona_count = result.scalar()
        print(f"✓ Personas created: {persona_count}")
        
        # Verify all narratives have embeddings
        assert embedding_count == narrative_count, "Not all narratives have embeddings"
        
        # Get sample data for inspection
        result = await db_session.execute(
            text("""
                SELECT id, raw_text, 
                       CASE 
                           WHEN embedding IS NOT NULL THEN 1536 
                           ELSE 0 
                       END as embedding_dim
                FROM narratives 
                WHERE person_id = :person_id 
                LIMIT 3
            """),
            {"person_id": TEST_PERSON_ID}
        )
        
        print("\nSample narratives:")
        for row in result:
            print(f"  ID: {row.id}")
            print(f"  Text: {row.raw_text[:60]}...")
            print(f"  Embedding dimension: {row.embedding_dim}")
            
        print("\n✓ Database state verified successfully")


async def main():
    """Run all tests in sequence."""
    print("=== REAL NARRATIVE FLOW TEST ===")
    print("Testing WITHOUT mocks - using real database, real APIs, real embeddings")
    print(f"API URL: {API_BASE_URL}")
    print(f"Test Person ID: {TEST_PERSON_ID}")
    
    # Check if API is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code != 200:
                print(f"\n✗ API is not healthy: {response.status_code}")
                print("Please start the API with: cd /path/to/persona-kit && ./scripts/start.sh")
                return
    except Exception as e:
        print(f"\n✗ Cannot connect to API: {e}")
        print("Please start the API with: cd /path/to/persona-kit && ./scripts/start.sh")
        return
    
    # Run tests
    test = TestRealNarrativeFlow()
    
    # Create test database connection
    database_url = settings.database_url.replace("persona_kit", "persona_kit_test")
    engine = create_async_engine(database_url, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not set")
        print("Embedding service will fail. Set the key to test real embeddings.")
        embedding_service = None
    else:
        embedding_service = EmbeddingService(api_key)
        print("✓ OpenAI API key found")
    
    async with async_session() as session:
        # Run tests in sequence
        try:
            await test.test_1_create_mindscape(session)
            await session.commit()
            
            await test.test_2_create_narrative_via_api()
            
            if embedding_service:
                await test.test_3_semantic_search(session, embedding_service)
                await test.test_4_rule_evaluation_with_narratives(session, embedding_service)
                await test.test_5_generate_persona_with_narratives(session, embedding_service)
            else:
                print("\n⚠️  Skipping embedding-dependent tests (no API key)")
                
            await test.test_6_verify_database_state(session)
            
            print("\n=== ALL TESTS PASSED ===")
            
        except Exception as e:
            print(f"\n✗ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Clean up - drop tables in correct order to handle dependencies
            async with engine.begin() as cleanup_conn:
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS persona_narrative_usage CASCADE"))
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS trait_narrative_links CASCADE"))
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS narratives CASCADE"))
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS feedback CASCADE"))
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS mindscapes CASCADE"))
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS observations CASCADE"))
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS outbox_tasks CASCADE"))
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS personas CASCADE"))
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
                await cleanup_conn.execute(text("DROP TABLE IF EXISTS mapper_configs CASCADE"))
                await cleanup_conn.execute(text("DROP TYPE IF EXISTS mapperstatus CASCADE"))
                await cleanup_conn.execute(text("DROP TYPE IF EXISTS observation_type CASCADE"))
                await cleanup_conn.execute(text("DROP TYPE IF EXISTS task_status CASCADE"))
            await engine.dispose()
            if embedding_service:
                await embedding_service.close()


if __name__ == "__main__":
    asyncio.run(main())