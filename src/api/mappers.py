"""
API endpoints for mapper configuration management.

This module provides REST endpoints for creating, reading, updating,
and managing mapper configurations.
"""

import json
import yaml
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ..database import get_db
from ..models.mapper_config import MapperConfig, MapperStatus
from ..services.rule_engine import ConfigurationValidator
from .auth import get_current_user

router = APIRouter(prefix="/mappers", tags=["mappers"])


class MapperListResponse(BaseModel):
    """Response model for listing mappers."""
    mappers: List[dict]
    total: int


class MapperDetailResponse(BaseModel):
    """Response model for mapper details."""
    id: str
    config_id: str
    version: int
    configuration: dict
    status: str
    created_at: datetime
    updated_at: datetime
    usage_count: int
    last_used_at: Optional[datetime]


class MapperCreateRequest(BaseModel):
    """Request model for creating a mapper."""
    config_id: str = Field(..., description="Unique identifier for this mapper")
    configuration: dict = Field(..., description="Mapper configuration as JSON")
    status: str = Field("draft", description="Initial status (draft/active)")


class MapperUpdateRequest(BaseModel):
    """Request model for updating a mapper."""
    configuration: Optional[dict] = Field(None, description="Updated configuration")
    status: Optional[str] = Field(None, description="Updated status")


@router.get("", response_model=MapperListResponse)
async def list_mappers(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> MapperListResponse:
    """
    List available mapper configurations.
    
    Args:
        status: Filter by status (draft/active/deprecated)
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    query = db.query(MapperConfig)
    
    if status:
        try:
            status_enum = MapperStatus(status)
            query = query.filter(MapperConfig.status == status_enum)
        except ValueError:
            raise HTTPException(400, f"Invalid status: {status}")
    
    # Get latest version of each config_id using a subquery
    
    # Subquery to get max version for each config_id
    subquery = db.query(
        MapperConfig.config_id,
        func.max(MapperConfig.version).label("max_version")
    ).group_by(MapperConfig.config_id).subquery()
    
    # Join with main table to get full records
    query = query.join(
        subquery,
        and_(
            MapperConfig.config_id == subquery.c.config_id,
            MapperConfig.version == subquery.c.max_version
        )
    )
    
    mappers = query.offset(skip).limit(limit).all()
    unique_mappers = [mapper.to_dict() for mapper in mappers]
    
    return MapperListResponse(
        mappers=unique_mappers,
        total=len(unique_mappers)
    )


@router.get("/{mapper_id}", response_model=MapperDetailResponse)
async def get_mapper(
    mapper_id: str,
    version: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> MapperDetailResponse:
    """
    Get a specific mapper configuration.
    
    Args:
        mapper_id: Either the UUID or config_id
        version: Specific version to retrieve (latest if not specified)
    """
    # Try to parse as UUID first
    try:
        mapper_uuid = uuid.UUID(mapper_id)
        mapper = db.query(MapperConfig).filter(
            MapperConfig.id == mapper_uuid
        ).first()
    except ValueError:
        # Not a UUID, treat as config_id
        if version:
            mapper = db.query(MapperConfig).filter(
                MapperConfig.config_id == mapper_id,
                MapperConfig.version == version
            ).first()
        else:
            mapper = MapperConfig.get_latest_version(db, mapper_id)
    
    if not mapper:
        raise HTTPException(404, "Mapper configuration not found")
    
    return MapperDetailResponse(**mapper.to_dict())


@router.post("", response_model=MapperDetailResponse)
async def create_mapper(
    request: MapperCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> MapperDetailResponse:
    """Create a new mapper configuration."""
    # Validate configuration
    errors = ConfigurationValidator.validate(request.configuration)
    if errors:
        raise HTTPException(
            400,
            detail={"message": "Invalid configuration", "errors": errors}
        )
    
    # Check if config_id already exists
    existing = MapperConfig.get_latest_version(db, request.config_id)
    if existing:
        raise HTTPException(
            409,
            f"Mapper '{request.config_id}' already exists. Use PUT to update."
        )
    
    # Create new mapper
    mapper = MapperConfig(
        config_id=request.config_id,
        version=1,
        configuration=request.configuration,
        status=MapperStatus(request.status),
        created_by=current_user.get("username", "system")
    )
    
    db.add(mapper)
    db.commit()
    db.refresh(mapper)
    
    return MapperDetailResponse(**mapper.to_dict())


@router.post("/upload", response_model=MapperDetailResponse)
async def upload_mapper(
    file: UploadFile = File(...),
    status: str = Form("draft"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> MapperDetailResponse:
    """
    Upload a mapper configuration from a YAML or JSON file.
    
    Args:
        file: YAML or JSON file containing the configuration
        status: Initial status for the mapper
    """
    # Check file size (limit to 1MB)
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large. Maximum size is 1MB.")
    
    # Parse based on file extension
    if file.filename.endswith('.yaml') or file.filename.endswith('.yml'):
        try:
            configuration = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise HTTPException(400, f"Invalid YAML: {str(e)}")
    elif file.filename.endswith('.json'):
        try:
            configuration = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(400, f"Invalid JSON: {str(e)}")
    else:
        raise HTTPException(400, "File must be .yaml, .yml, or .json")
    
    # Validate configuration
    errors = ConfigurationValidator.validate(configuration)
    if errors:
        raise HTTPException(
            400,
            detail={"message": "Invalid configuration", "errors": errors}
        )
    
    # Extract config_id from metadata
    config_id = configuration.get("metadata", {}).get("id")
    if not config_id:
        raise HTTPException(400, "Configuration must include metadata.id")
    
    # Check if this is a new version
    existing = MapperConfig.get_latest_version(db, config_id)
    version = existing.version + 1 if existing else 1
    
    # Create new mapper version
    mapper = MapperConfig(
        config_id=config_id,
        version=version,
        configuration=configuration,
        status=MapperStatus(status),
        created_by=current_user.get("username", "system")
    )
    
    db.add(mapper)
    db.commit()
    db.refresh(mapper)
    
    return MapperDetailResponse(**mapper.to_dict())


@router.put("/{mapper_id}", response_model=MapperDetailResponse)
async def update_mapper(
    mapper_id: str,
    request: MapperUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> MapperDetailResponse:
    """
    Update a mapper configuration (creates new version).
    
    Args:
        mapper_id: Config ID of the mapper to update
        request: Update request with new configuration and/or status
    """
    # Get latest version
    existing = MapperConfig.get_latest_version(db, mapper_id)
    if not existing:
        raise HTTPException(404, "Mapper configuration not found")
    
    # Prepare new configuration
    new_config = request.configuration or existing.configuration
    
    # Validate if configuration changed
    if request.configuration:
        errors = ConfigurationValidator.validate(new_config)
        if errors:
            raise HTTPException(
                400,
                detail={"message": "Invalid configuration", "errors": errors}
            )
    
    # Create new version
    new_mapper = MapperConfig(
        config_id=existing.config_id,
        version=existing.version + 1,
        configuration=new_config,
        status=MapperStatus(request.status) if request.status else existing.status,
        created_by=current_user.get("username", "system")
    )
    
    # If new version is active, deprecate all previous active versions
    if new_mapper.status == MapperStatus.ACTIVE:
        db.query(MapperConfig).filter(
            MapperConfig.config_id == existing.config_id,
            MapperConfig.status == MapperStatus.ACTIVE
        ).update({"status": MapperStatus.DEPRECATED})
    
    db.add(new_mapper)
    db.commit()
    db.refresh(new_mapper)
    
    return MapperDetailResponse(**new_mapper.to_dict())


@router.get("/{mapper_id}/versions")
async def get_mapper_versions(
    mapper_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get version history for a mapper configuration."""
    versions = db.query(MapperConfig).filter(
        MapperConfig.config_id == mapper_id
    ).order_by(MapperConfig.version.desc()).all()
    
    if not versions:
        raise HTTPException(404, "Mapper configuration not found")
    
    return {
        "config_id": mapper_id,
        "versions": [
            {
                "version": v.version,
                "status": v.status.value,
                "created_at": v.created_at.isoformat(),
                "created_by": v.created_by,
                "usage_count": v.usage_count
            }
            for v in versions
        ]
    }


@router.delete("/{mapper_id}")
async def deprecate_mapper(
    mapper_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Deprecate a mapper configuration (soft delete).
    
    Note: Mappers are never hard-deleted to maintain history.
    """
    # Update all versions to deprecated
    result = db.query(MapperConfig).filter(
        MapperConfig.config_id == mapper_id
    ).update({"status": MapperStatus.DEPRECATED})
    
    if result == 0:
        raise HTTPException(404, "Mapper configuration not found")
    
    db.commit()
    
    return {"message": f"Deprecated {result} versions of mapper '{mapper_id}'"}