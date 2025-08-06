"""Repository for Observation model operations."""
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.observation import Observation, ObservationType
from .base import BaseRepository


class ObservationRepository(BaseRepository[Observation]):
    """Repository for observation-specific database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize observation repository."""
        super().__init__(Observation, session)

    async def get_by_person(
        self,
        person_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
        observation_type: ObservationType | None = None,
    ) -> list[Observation]:
        """Get observations for a specific person."""
        stmt = select(Observation).where(Observation.person_id == person_id)
        
        if observation_type:
            stmt = stmt.where(Observation.type == observation_type)
        
        stmt = stmt.order_by(Observation.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent(
        self,
        person_id: uuid.UUID,
        days: int = 7,
        observation_type: ObservationType | None = None,
    ) -> list[Observation]:
        """Get recent observations within specified days."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        stmt = select(Observation).where(
            and_(
                Observation.person_id == person_id,
                Observation.created_at >= cutoff,
            )
        )
        
        if observation_type:
            stmt = stmt.where(Observation.type == observation_type)
        
        stmt = stmt.order_by(Observation.created_at.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_old_observations(self, days: int = 90) -> int:
        """Delete observations older than specified days."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        stmt = select(Observation).where(Observation.created_at < cutoff)
        result = await self.session.execute(stmt)
        old_observations = result.scalars().all()
        
        count = 0
        for obs in old_observations:
            await self.session.delete(obs)
            count += 1
        
        await self.session.commit()
        return count