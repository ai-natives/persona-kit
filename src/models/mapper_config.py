"""
Mapper configuration data model.

This module defines the database model for storing mapper configurations
as JSONB documents with version tracking.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, DateTime, Integer, String, Text, JSON, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .base import Base


class MapperStatus(str, enum.Enum):
    """Status of a mapper configuration."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class MapperConfig(Base):
    """Stores mapper configurations as versioned JSONB documents."""
    
    __tablename__ = "mapper_configs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Configuration identity
    config_id = Column(String(100), nullable=False)  # e.g., "daily-work-optimizer"
    version = Column(Integer, nullable=False, default=1)
    
    # Configuration content (JSONB)
    configuration = Column(JSON, nullable=False)
    
    # Status
    status = Column(
        Enum(MapperStatus),
        nullable=False,
        default=MapperStatus.DRAFT
    )
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))  # User or system that created this
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    # Indexes for efficient querying
    __table_args__ = (
        # Unique constraint on config_id + version
        Index('idx_mapper_config_id_version', 'config_id', 'version', unique=True),
        # Index for finding active configs
        Index('idx_mapper_config_status', 'config_id', 'status'),
        # Index for usage tracking
        Index('idx_mapper_config_usage', 'last_used_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "config_id": self.config_id,
            "version": self.version,
            "configuration": self.configuration,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "usage_count": self.usage_count,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None
        }
    
    @classmethod
    def get_active_version(cls, db, config_id: str) -> Optional["MapperConfig"]:
        """Get the active version of a configuration."""
        return db.query(cls).filter(
            cls.config_id == config_id,
            cls.status == MapperStatus.ACTIVE
        ).order_by(cls.version.desc()).first()
    
    @classmethod
    def get_latest_version(cls, db, config_id: str) -> Optional["MapperConfig"]:
        """Get the latest version of a configuration (any status)."""
        return db.query(cls).filter(
            cls.config_id == config_id
        ).order_by(cls.version.desc()).first()
    
    @classmethod
    def increment_usage(cls, db, mapper_id: uuid.UUID) -> None:
        """Increment usage count and update last used timestamp."""
        mapper = db.query(cls).filter(cls.id == mapper_id).first()
        if mapper:
            mapper.usage_count += 1
            mapper.last_used_at = datetime.utcnow()
            db.commit()