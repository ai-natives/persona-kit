"""Embedding service for generating text embeddings locally."""
import logging
from typing import List, Optional, Tuple
import asyncio
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using local sentence-transformers."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the embedding service with a local model.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                       Defaults to 'all-MiniLM-L6-v2' which is fast and good quality.
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        
        # Use a small, fast model by default
        # all-MiniLM-L6-v2: 384 dims, 80MB, very fast
        # For better quality: all-mpnet-base-v2 (768 dims, 420MB)
        self.model_name = model_name or "all-MiniLM-L6-v2"
        
        logger.info(f"Loading local embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # For compatibility with existing code expecting 1536 dims
        # We'll pad or truncate as needed
        self.target_dimension = 1536
        
        # Validate that we can handle the dimension difference
        if self.dimension > self.target_dimension:
            logger.warning(
                f"Model dimension ({self.dimension}) exceeds target ({self.target_dimension}). "
                "Embeddings will be truncated, which may affect quality."
            )
        
        logger.info(f"Model loaded. Native dimension: {self.dimension}, target: {self.target_dimension}")
        
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Normalize embedding to unit length for cosine similarity.
        
        Args:
            embedding: Input embedding vector
            
        Returns:
            Normalized embedding vector
        """
        norm = np.linalg.norm(embedding)
        if norm > 0:
            return embedding / norm
        else:
            logger.warning("Zero-norm embedding encountered, returning as-is")
            return embedding
    
    def _validate_embedding(self, embedding: np.ndarray) -> Tuple[bool, str]:
        """Validate embedding vector.
        
        Args:
            embedding: Embedding to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(embedding, np.ndarray):
            return False, "Embedding must be a numpy array"
        
        if embedding.ndim != 1:
            return False, f"Embedding must be 1D, got {embedding.ndim}D"
        
        if len(embedding) == 0:
            return False, "Embedding cannot be empty"
        
        if not np.isfinite(embedding).all():
            return False, "Embedding contains NaN or infinite values"
        
        return True, ""
    
    def _adapt_dimension(self, embedding: np.ndarray) -> List[float]:
        """Adapt embedding to target dimension using a better strategy than zero-padding.
        
        For smaller embeddings, we use a projection matrix approach or repeat patterns
        to preserve more semantic information than simple zero-padding.
        
        Args:
            embedding: Input embedding (already normalized)
            
        Returns:
            List of floats with target dimension
        """
        current_dim = len(embedding)
        
        if current_dim == self.target_dimension:
            return embedding.tolist()
        
        elif current_dim < self.target_dimension:
            # Instead of zero-padding, use a more sophisticated approach
            # Option 1: Cycle the embedding to fill the space
            # This preserves the relative relationships better than zeros
            result = np.zeros(self.target_dimension)
            
            # Fill by cycling through the original embedding
            for i in range(self.target_dimension):
                result[i] = embedding[i % current_dim]
            
            # Re-normalize after expansion
            result = self._normalize_embedding(result)
            
            logger.debug(f"Expanded embedding from {current_dim} to {self.target_dimension} dims using cycling")
            return result.tolist()
        
        else:
            # Truncate - take the first N dimensions
            # Most models have the most important information in early dimensions
            truncated = embedding[:self.target_dimension]
            
            # Re-normalize after truncation
            truncated = self._normalize_embedding(truncated)
            
            logger.debug(f"Truncated embedding from {current_dim} to {self.target_dimension} dims")
            return truncated.tolist()
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector (1536 dimensions)
            
        Raises:
            Exception: If embedding generation fails
        """
        try:
            # Validate input
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self.model.encode,
                text
            )
            
            # Ensure it's a numpy array
            embedding = np.array(embedding)
            
            # Validate the embedding
            is_valid, error_msg = self._validate_embedding(embedding)
            if not is_valid:
                raise ValueError(f"Invalid embedding generated: {error_msg}")
            
            # Normalize the embedding for cosine similarity
            embedding = self._normalize_embedding(embedding)
            
            # Adapt to target dimension
            result = self._adapt_dimension(embedding)
            
            logger.debug(f"Generated embedding for text of length {len(text)}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
            
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (1536 dimensions each)
            
        Raises:
            Exception: If embedding generation fails
        """
        if not texts:
            return []
            
        try:
            # Validate inputs
            valid_texts = []
            for i, text in enumerate(texts):
                if not text or not text.strip():
                    logger.warning(f"Skipping empty text at index {i}")
                    valid_texts.append("")  # Placeholder to maintain indices
                else:
                    valid_texts.append(text)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self.model.encode,
                [t for t in valid_texts if t]  # Only encode non-empty texts
            )
            
            # Process results
            results = []
            embedding_idx = 0
            
            for text in valid_texts:
                if not text:
                    # For empty texts, create a zero embedding
                    zero_embedding = np.zeros(self.dimension)
                    zero_embedding = self._normalize_embedding(zero_embedding)
                    results.append(self._adapt_dimension(zero_embedding))
                else:
                    # Process the actual embedding
                    embedding = np.array(embeddings[embedding_idx])
                    embedding_idx += 1
                    
                    # Validate
                    is_valid, error_msg = self._validate_embedding(embedding)
                    if not is_valid:
                        logger.error(f"Invalid embedding for text: {error_msg}")
                        # Create a fallback embedding
                        embedding = np.zeros(self.dimension)
                    
                    # Normalize and adapt
                    embedding = self._normalize_embedding(embedding)
                    results.append(self._adapt_dimension(embedding))
            
            logger.debug(f"Generated embeddings for {len(texts)} texts")
            return results
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
            
    async def close(self):
        """No cleanup needed for local models."""
        pass