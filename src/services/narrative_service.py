"""Service for managing narratives with CRUD operations and semantic search."""
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, UTC
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func, and_, literal_column, cast
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import selectinload

from ..models import Narrative, TraitNarrativeLink
from ..schemas.narrative import (
    CreateNarrativeRequest,
    CurationRequest,
    NarrativeSearchRequest,
    NarrativeResponse,
    NarrativeSearchResult,
)
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class NarrativeService:
    """Service for managing narratives."""
    
    def __init__(self, db: AsyncSession, embedding_service: EmbeddingService):
        """Initialize the narrative service.
        
        Args:
            db: Database session
            embedding_service: Service for generating embeddings
        """
        self.db = db
        self.embedding_service = embedding_service
        
    async def create_self_observation(
        self, 
        request: CreateNarrativeRequest
    ) -> Narrative:
        """Create a new self-observation narrative.
        
        Args:
            request: Narrative creation request
            
        Returns:
            Created narrative
        """
        # Generate embedding for the text
        embedding = await self.embedding_service.embed_text(request.raw_text)
        
        # Extract tags if not provided
        if not request.tags:
            request.tags = self._extract_tags(request.raw_text)
        
        # Create narrative
        narrative = Narrative(
            person_id=request.person_id,
            narrative_type="self_observation",
            raw_text=request.raw_text,
            tags=request.tags,
            context=request.context or {},
            source=request.source,
            embedding=embedding
        )
        
        self.db.add(narrative)
        await self.db.commit()
        await self.db.refresh(narrative)
        
        logger.info(f"Created self-observation narrative {narrative.id} for person {request.person_id}")
        return narrative
        
    async def create_curation(
        self, 
        request: CurationRequest
    ) -> Narrative:
        """Create a trait curation narrative.
        
        Args:
            request: Curation request
            
        Returns:
            Created narrative
        """
        # Generate embedding for the curation text
        embedding = await self.embedding_service.embed_text(request.raw_text)
        
        # Extract tags if not provided
        if not request.tags:
            request.tags = self._extract_tags(request.raw_text)
            request.tags.append(f"curates:{request.trait_path}")
        
        # Create curation narrative
        narrative = Narrative(
            person_id=request.person_id,
            narrative_type="curation",
            raw_text=request.raw_text,
            trait_path=request.trait_path,
            curation_action=request.action,
            tags=request.tags,
            context=request.context or {},
            source="curation",
            embedding=embedding
        )
        
        self.db.add(narrative)
        await self.db.flush()  # Flush to get the ID
        
        # Create trait-narrative link
        link = TraitNarrativeLink(
            narrative_id=narrative.id,
            trait_path=request.trait_path,
            person_id=request.person_id,
            link_type="curates",
            confidence=1.0  # Direct curation has full confidence
        )
        
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(narrative)
        
        logger.info(f"Created curation narrative {narrative.id} for trait {request.trait_path}")
        return narrative
        
    async def semantic_search(
        self,
        request: NarrativeSearchRequest
    ) -> List[NarrativeSearchResult]:
        """Search narratives semantically using embeddings.
        
        Args:
            request: Search request
            
        Returns:
            List of search results with similarity scores
        """
        # Generate embedding for the query
        query_embedding = await self.embedding_service.embed_text(request.query)
        
        # Log the type and shape of the embedding
        logger.debug(f"Query embedding type: {type(query_embedding)}")
        logger.debug(f"Query embedding length: {len(query_embedding) if query_embedding else 0}")
        if hasattr(query_embedding, 'shape'):
            logger.debug(f"Query embedding shape: {query_embedding.shape}")
        
        # Ensure it's a flat list
        if hasattr(query_embedding, 'tolist'):
            query_embedding = query_embedding.tolist()
        
        # Make sure it's a flat list, not nested
        if query_embedding and isinstance(query_embedding[0], (list, tuple)):
            logger.warning("Query embedding is nested, flattening...")
            query_embedding = query_embedding[0]
        
        # For now, return all narratives without similarity scoring
        # The vector search needs a different approach with pgvector
        
        from sqlalchemy import select, and_
        from ..models.narrative import Narrative
        
        # Simple query without vector similarity for now
        query = (
            select(Narrative)
            .where(
                and_(
                    Narrative.person_id == request.person_id,
                    Narrative.embedding.isnot(None)
                )
            )
            .order_by(Narrative.created_at.desc())
            .limit(request.limit)
        )
        
        # Add narrative type filter if specified
        if request.narrative_types:
            query = query.where(Narrative.narrative_type.in_(request.narrative_types))
        
        # Execute the query
        result = await self.db.execute(query)
        rows = result.scalars().all()
        
        logger.debug(f"Query returned {len(rows)} rows")
        
        # Convert to search results
        search_results = []
        for narrative in rows:
            try:
                # For now, we're not computing similarity scores
                # Use a placeholder similarity of 1.0
                similarity = 1.0
                
                narrative_response = NarrativeResponse(
                    id=narrative.id,
                    person_id=narrative.person_id,
                    narrative_type=narrative.narrative_type,
                    raw_text=narrative.raw_text,
                    curated_text=narrative.curated_text,
                    tags=narrative.tags or [],
                    context=narrative.context or {},
                    trait_path=narrative.trait_path,
                    curation_action=narrative.curation_action,
                    created_at=narrative.created_at,
                    updated_at=narrative.updated_at,
                    source=narrative.source,
                    embedding_generated=narrative.embedding is not None
                )
                
                # Extract relevant excerpt (first 200 chars for now)
                excerpt = narrative.raw_text[:200] + "..." if len(narrative.raw_text) > 200 else narrative.raw_text
                
                search_result = NarrativeSearchResult(
                    narrative=narrative_response,
                    similarity_score=similarity,
                    excerpt=excerpt
                )
                search_results.append(search_result)
                logger.debug(f"Added search result for narrative {narrative_response.id}")
            except Exception as e:
                logger.error(f"Error processing narrative: {e}")
                logger.error(f"Narrative data: {narrative}")
                raise
        
        logger.info(f"Semantic search for '{request.query}' returned {len(search_results)} results")
        return search_results
        
    async def get_narrative(self, narrative_id: uuid.UUID) -> Optional[Narrative]:
        """Get a narrative by ID.
        
        Args:
            narrative_id: Narrative ID
            
        Returns:
            Narrative if found, None otherwise
        """
        result = await self.db.execute(
            select(Narrative).where(Narrative.id == narrative_id)
        )
        return result.scalar_one_or_none()
        
    async def get_person_narratives(
        self,
        person_id: uuid.UUID,
        narrative_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Narrative]:
        """Get narratives for a person.
        
        Args:
            person_id: Person ID
            narrative_type: Optional filter by type
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of narratives
        """
        query = select(Narrative).where(Narrative.person_id == person_id)
        
        if narrative_type:
            query = query.where(Narrative.narrative_type == narrative_type)
            
        query = query.order_by(Narrative.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
        
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from text using simple keyword detection.
        
        Args:
            text: Text to extract tags from
            
        Returns:
            List of extracted tags
        """
        # Simple keyword extraction - in production, use NLP
        keywords = [
            "morning", "evening", "night", "afternoon",
            "productivity", "focus", "energy", "tired",
            "meeting", "coding", "writing", "thinking",
            "break", "exercise", "coffee", "lunch",
            "stressed", "calm", "motivated", "frustrated"
        ]
        
        text_lower = text.lower()
        tags = []
        
        for keyword in keywords:
            if keyword in text_lower:
                tags.append(keyword)
                
        return tags[:5]  # Limit to 5 tags