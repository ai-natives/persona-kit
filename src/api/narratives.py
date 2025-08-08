"""Narrative API endpoints."""
import logging
from typing import List, Optional
import uuid
from datetime import datetime
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.narrative import (
    CreateNarrativeRequest,
    CreateNarrativeResponse,
    CurationRequest,
    NarrativeResponse,
    NarrativeSearchRequest,
    NarrativeSearchResponse,
    NarrativeSearchResult,
)
from ..services.narrative_service import NarrativeService
from ..services.embedding_service import EmbeddingService

router = APIRouter()
logger = logging.getLogger(__name__)

# Global embedding service instance (initialized on first use)
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        # Use local embedding service (no API key needed)
        _embedding_service = EmbeddingService()
    return _embedding_service


@router.post("/self-observation", response_model=CreateNarrativeResponse)
async def create_self_observation(
    request: CreateNarrativeRequest,
    db: AsyncSession = Depends(get_db),
) -> CreateNarrativeResponse:
    """Create a new self-observation narrative."""
    try:
        embedding_service = get_embedding_service()
        narrative_service = NarrativeService(db, embedding_service)
        
        narrative = await narrative_service.create_self_observation(request)
        
        return CreateNarrativeResponse(
            id=narrative.id,
            message="Self-observation created successfully",
            embedding_generated=narrative.embedding is not None
        )
        
    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create self-observation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create narrative: {str(e)}")


@router.post("/curate", response_model=CreateNarrativeResponse)
async def create_curation(
    request: CurationRequest,
    db: AsyncSession = Depends(get_db),
) -> CreateNarrativeResponse:
    """Create a trait curation narrative."""
    try:
        embedding_service = get_embedding_service()
        narrative_service = NarrativeService(db, embedding_service)
        
        narrative = await narrative_service.create_curation(request)
        
        return CreateNarrativeResponse(
            id=narrative.id,
            message=f"Curation for {request.trait_path} created successfully",
            embedding_generated=narrative.embedding is not None
        )
        
    except ValueError as e:
        logger.warning(f"Invalid curation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create curation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create curation")


@router.get("/", response_model=List[NarrativeResponse])
async def get_narratives(
    person_id: Optional[str] = Query(None),
    narrative_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[NarrativeResponse]:
    """Get narratives with optional filters."""
    try:
        from sqlalchemy import select
        from ..models.narrative import Narrative
        
        query = select(Narrative)
        
        if person_id:
            query = query.where(Narrative.person_id == uuid.UUID(person_id))
        
        if narrative_type:
            query = query.where(Narrative.narrative_type == narrative_type)
            
        query = query.order_by(Narrative.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        narratives = result.scalars().all()
        
        return [
            NarrativeResponse(
                id=n.id,
                person_id=n.person_id,
                narrative_type=n.narrative_type,
                raw_text=n.raw_text,
                curated_text=n.curated_text,
                tags=n.tags or [],
                context=n.context or {},
                embedding_generated=n.embedding is not None,
                created_at=n.created_at,
            )
            for n in narratives
        ]
        
    except ValueError as e:
        logger.warning(f"Invalid query parameters: {e}")
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    except Exception as e:
        logger.error(f"Failed to fetch narratives: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch narratives")


@router.post("/search", response_model=NarrativeSearchResponse)
async def search_narratives(
    request: NarrativeSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> NarrativeSearchResponse:
    """Search narratives semantically."""
    start_time = datetime.now()
    
    print(f"DEBUG: Received search request: {request}")
    logger.info(f"Received search request for query: {request.query}")
    
    try:
        embedding_service = get_embedding_service()
        narrative_service = NarrativeService(db, embedding_service)
        
        logger.info(f"Starting search for query: {request.query}")
        results = await narrative_service.semantic_search(request)
        logger.info(f"Search returned {len(results)} results")
        
        search_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        response = NarrativeSearchResponse(
            query=request.query,
            results=results,
            total_found=len(results),
            search_time_ms=search_time_ms
        )
        print(f"DEBUG: Returning response with {len(results)} results")
        return response
        
    except Exception as e:
        print(f"DEBUG: Search failed with error: {e}")
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/{narrative_id}", response_model=NarrativeResponse)
async def get_narrative(
    narrative_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> NarrativeResponse:
    """Get a specific narrative by ID."""
    embedding_service = get_embedding_service()
    narrative_service = NarrativeService(db, embedding_service)
    
    narrative = await narrative_service.get_narrative(narrative_id)
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
        
    return NarrativeResponse.model_validate(narrative)




@router.get("/person/{person_id}", response_model=List[NarrativeResponse])
async def get_person_narratives(
    person_id: uuid.UUID,
    narrative_type: Optional[str] = Query(None, description="Filter by narrative type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[NarrativeResponse]:
    """Get all narratives for a person."""
    embedding_service = get_embedding_service()
    narrative_service = NarrativeService(db, embedding_service)
    
    narratives = await narrative_service.get_person_narratives(
        person_id=person_id,
        narrative_type=narrative_type,
        limit=limit,
        offset=offset
    )
    
    return [NarrativeResponse.model_validate(n) for n in narratives]