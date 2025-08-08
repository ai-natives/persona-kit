"""Tests for the embedding service."""
import pytest
import numpy as np
from src.services.embedding_service import EmbeddingService


@pytest.mark.asyncio
async def test_embedding_service_initialization():
    """Test that embedding service initializes correctly."""
    service = EmbeddingService()
    assert service.model_name == "all-MiniLM-L6-v2"
    assert service.dimension == 384  # Expected for this model
    assert service.target_dimension == 1536


@pytest.mark.asyncio
async def test_embed_single_text():
    """Test embedding a single text."""
    service = EmbeddingService()
    
    text = "This is a test narrative about productivity"
    embedding = await service.embed_text(text)
    
    # Check dimensions
    assert len(embedding) == 1536
    assert isinstance(embedding, list)
    assert all(isinstance(x, float) for x in embedding)
    
    # Check normalization (should be unit vector)
    norm = np.linalg.norm(embedding)
    assert abs(norm - 1.0) < 0.01  # Allow small floating point error


@pytest.mark.asyncio
async def test_embed_empty_text():
    """Test that empty text raises an error."""
    service = EmbeddingService()
    
    with pytest.raises(ValueError, match="Text cannot be empty"):
        await service.embed_text("")
    
    with pytest.raises(ValueError, match="Text cannot be empty"):
        await service.embed_text("   ")


@pytest.mark.asyncio
async def test_embed_multiple_texts():
    """Test batch embedding."""
    service = EmbeddingService()
    
    texts = [
        "First narrative about morning productivity",
        "Second narrative about focus time",
        "Third narrative about energy levels"
    ]
    
    embeddings = await service.embed_texts(texts)
    
    assert len(embeddings) == 3
    for embedding in embeddings:
        assert len(embedding) == 1536
        assert isinstance(embedding, list)
        
        # Check normalization
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 0.01


@pytest.mark.asyncio
async def test_embed_texts_with_empty():
    """Test batch embedding with some empty texts."""
    service = EmbeddingService()
    
    texts = [
        "Valid text",
        "",  # Empty
        "Another valid text",
        "   ",  # Whitespace only
    ]
    
    embeddings = await service.embed_texts(texts)
    
    assert len(embeddings) == 4
    # Empty texts should still get embeddings (zero vectors)
    for i, embedding in enumerate(embeddings):
        assert len(embedding) == 1536
        
        if i in [1, 3]:  # Empty text indices
            # Should be normalized zero vector (or very small)
            assert np.linalg.norm(embedding) < 0.1


@pytest.mark.asyncio
async def test_embedding_similarity():
    """Test that similar texts produce similar embeddings."""
    service = EmbeddingService()
    
    text1 = "I work best in the morning with coffee"
    text2 = "Morning time with coffee is when I'm most productive"
    text3 = "I prefer working late at night"
    
    emb1 = np.array(await service.embed_text(text1))
    emb2 = np.array(await service.embed_text(text2))
    emb3 = np.array(await service.embed_text(text3))
    
    # Cosine similarity
    sim_12 = np.dot(emb1, emb2)  # Already normalized
    sim_13 = np.dot(emb1, emb3)
    
    # Similar texts should have higher similarity
    assert sim_12 > sim_13
    assert sim_12 > 0.5  # Reasonably similar
    assert sim_13 < 0.8  # Not too similar


@pytest.mark.asyncio
async def test_dimension_adaptation():
    """Test that dimension adaptation preserves relationships."""
    service = EmbeddingService()
    
    # Get two similar texts
    texts = [
        "I focus best in quiet environments",
        "Quiet spaces help me concentrate better"
    ]
    
    embeddings = await service.embed_texts(texts)
    emb1 = np.array(embeddings[0])
    emb2 = np.array(embeddings[1])
    
    # Check that cycling didn't destroy similarity
    similarity = np.dot(emb1, emb2)
    assert similarity > 0.5  # Should still be reasonably similar
    
    # Check that the pattern repeats correctly (for 384 -> 1536)
    # Every 384th element should match the original pattern
    assert abs(emb1[0] - emb1[384]) < 0.01
    assert abs(emb1[1] - emb1[385]) < 0.01