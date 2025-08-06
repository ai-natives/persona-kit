"""Repository for Persona model operations."""
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.persona import Persona
from .base import BaseRepository


class PersonaRepository(BaseRepository[Persona]):
    """Repository for persona-specific database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize persona repository."""
        super().__init__(Persona, session)

    async def get_active(self, person_id: uuid.UUID) -> list[Persona]:
        """Get all active (non-expired) personas for a person."""
        now = datetime.now(UTC)

        stmt = select(Persona).where(
            and_(
                Persona.person_id == person_id,
                Persona.expires_at > now,
            )
        ).order_by(Persona.created_at.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_by_mapper(
        self, person_id: uuid.UUID, mapper_id: str
    ) -> Persona | None:
        """Get active persona for a specific mapper."""
        now = datetime.now(UTC)

        stmt = select(Persona).where(
            and_(
                Persona.person_id == person_id,
                Persona.mapper_id == mapper_id,
                Persona.expires_at > now,
            )
        ).order_by(Persona.created_at.desc()).limit(1)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_expired(self) -> int:
        """Delete all expired personas."""
        now = datetime.now(UTC)

        stmt = select(Persona).where(Persona.expires_at <= now)
        result = await self.session.execute(stmt)
        expired = result.scalars().all()

        count = 0
        for persona in expired:
            await self.session.delete(persona)
            count += 1

        await self.session.commit()
        return count

    async def extend_ttl(
        self, persona_id: uuid.UUID, additional_seconds: int
    ) -> Persona | None:
        """Extend the TTL of a persona."""
        persona = await self.get(persona_id)
        if persona:
            # Only extend if not already expired
            now = datetime.now(UTC)
            if persona.expires_at > now:
                persona.expires_at = persona.expires_at + timedelta(seconds=additional_seconds)
                await self.session.commit()
                await self.session.refresh(persona)
        return persona
