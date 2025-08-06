"""Repository for Mindscape model operations."""
import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.mindscape import Mindscape
from .base import BaseRepository


class MindscapeRepository(BaseRepository[Mindscape]):
    """Repository for mindscape-specific database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize mindscape repository."""
        super().__init__(Mindscape, session)

    async def get_by_person(self, person_id: uuid.UUID) -> Mindscape | None:
        """Get mindscape for a specific person."""
        stmt = select(Mindscape).where(Mindscape.person_id == person_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self, person_id: uuid.UUID, traits: dict[str, Any]
    ) -> Mindscape:
        """Create or update mindscape for a person."""
        stmt = insert(Mindscape).values(
            person_id=person_id,
            traits=traits,
            version=1,
        )
        
        # On conflict, update traits and increment version
        stmt = stmt.on_conflict_do_update(
            index_elements=["person_id"],
            set_={
                "traits": stmt.excluded.traits,
                "version": Mindscape.version + 1,
                "updated_at": sa.func.now(),
            },
        )
        
        await self.session.execute(stmt)
        await self.session.commit()
        
        # Fetch the updated record with fresh session state
        mindscape = await self.get_by_person(person_id)
        if mindscape:
            await self.session.refresh(mindscape)
        return mindscape  # type: ignore

    async def update_traits(
        self, person_id: uuid.UUID, trait_updates: dict[str, Any]
    ) -> Mindscape | None:
        """Update specific traits in a mindscape."""
        mindscape = await self.get_by_person(person_id)
        if not mindscape:
            return None
        
        # Merge trait updates with existing traits
        updated_traits = {**mindscape.traits, **trait_updates}
        mindscape.traits = updated_traits
        mindscape.version += 1
        
        await self.session.commit()
        await self.session.refresh(mindscape)
        return mindscape