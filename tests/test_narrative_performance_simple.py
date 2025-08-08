#!/usr/bin/env python3
"""
Simple performance benchmark for narratives.
Run with: python tests/test_narrative_performance_simple.py
"""
import asyncio
import time
import uuid
import statistics

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models.base import Base
from src.services.narrative_service import NarrativeService
from src.services.embedding_service import EmbeddingService
from src.schemas.narrative import CreateNarrativeRequest, NarrativeSearchRequest


async def benchmark_creation(session: AsyncSession):
    """Benchmark narrative creation."""
    print("\n=== Testing Narrative Creation Performance ===")
    
    embedding_service = EmbeddingService()
    narrative_service = NarrativeService(session, embedding_service)
    person_id = uuid.uuid4()
    
    times = []
    for i in range(10):
        request = CreateNarrativeRequest(
            person_id=person_id,
            raw_text=f"Test narrative {i}: I find that my productivity varies throughout the day",
            tags=["productivity", "test"],
            source="benchmark"
        )
        
        start = time.time()
        await narrative_service.create_self_observation(request)
        elapsed = (time.time() - start) * 1000  # ms
        times.append(elapsed)
        print(f"  Creation {i+1}: {elapsed:.1f}ms")
    
    avg_time = statistics.mean(times)
    print(f"\nAverage: {avg_time:.1f}ms")
    print(f"Target: <200ms")
    print(f"Status: {'✅ PASS' if avg_time < 200 else '❌ FAIL'}")
    
    return avg_time < 200


async def benchmark_search(session: AsyncSession):
    """Benchmark semantic search."""
    print("\n=== Testing Semantic Search Performance ===")
    
    embedding_service = EmbeddingService()
    narrative_service = NarrativeService(session, embedding_service)
    person_id = uuid.uuid4()
    
    # Create test narratives
    print("Creating 100 test narratives...")
    for i in range(100):
        request = CreateNarrativeRequest(
            person_id=person_id,
            raw_text=f"Narrative {i}: " + ["morning productivity", "afternoon focus", "evening creativity"][i % 3],
            tags=["test"],
            source="benchmark"
        )
        await narrative_service.create_self_observation(request)
    
    # Benchmark search
    times = []
    queries = ["When am I productive?", "How is my focus?", "Tell me about creativity"]
    
    for query in queries:
        search_request = NarrativeSearchRequest(
            person_id=person_id,
            query=query,
            limit=5
        )
        
        start = time.time()
        results = await narrative_service.semantic_search(search_request)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"  Search '{query}': {elapsed:.1f}ms ({len(results)} results)")
    
    avg_time = statistics.mean(times)
    print(f"\nAverage: {avg_time:.1f}ms")
    print(f"Target: <500ms")
    print(f"Status: {'✅ PASS' if avg_time < 500 else '❌ FAIL'}")
    
    return avg_time < 500


async def main():
    """Run performance benchmarks."""
    print("PersonaKit Narrative Performance Benchmarks")
    print("=" * 50)
    
    # Create engine
    engine = create_async_engine(settings.database_url, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            creation_pass = await benchmark_creation(session)
            search_pass = await benchmark_search(session)
            
            print("\n" + "=" * 50)
            print("SUMMARY")
            print("=" * 50)
            print(f"Narrative Creation: {'✅ PASS' if creation_pass else '❌ FAIL'}")
            print(f"Semantic Search: {'✅ PASS' if search_pass else '❌ FAIL'}")
            print(f"\nOverall: {'✅ ALL TESTS PASS' if creation_pass and search_pass else '❌ SOME TESTS FAILED'}")
            
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())