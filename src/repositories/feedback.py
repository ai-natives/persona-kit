"""Repository for Feedback model operations."""
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.feedback import Feedback
from .base import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    """Repository for feedback-specific database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize feedback repository."""
        super().__init__(Feedback, session)

    async def get_by_persona(
        self, persona_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> list[Feedback]:
        """Get feedback for a specific persona."""
        stmt = (
            select(Feedback)
            .where(Feedback.persona_id == persona_id)
            .order_by(Feedback.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_negative(
        self, persona_id: uuid.UUID, days: int = 7
    ) -> list[Feedback]:
        """Get recent negative feedback for a persona."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        stmt = select(Feedback).where(
            and_(
                Feedback.persona_id == persona_id,
                Feedback.created_at >= cutoff,
                # Negative feedback: rating <= 2 or helpful = False
                (Feedback.rating <= 2) | (Feedback.helpful == False),
            )
        ).order_by(Feedback.created_at.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_negative_feedback(
        self, persona_id: uuid.UUID, days: int = 7
    ) -> int:
        """Count negative feedback for a persona within specified days."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        stmt = select(func.count(Feedback.id)).where(
            and_(
                Feedback.persona_id == persona_id,
                Feedback.created_at >= cutoff,
                (Feedback.rating <= 2) | (Feedback.helpful == False),
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_feedback_stats(self, persona_id: uuid.UUID) -> dict:
        """Get feedback statistics for a persona."""
        # Average rating
        avg_stmt = select(func.avg(Feedback.rating)).where(
            and_(
                Feedback.persona_id == persona_id,
                Feedback.rating.is_not(None),
            )
        )
        avg_result = await self.session.execute(avg_stmt)
        avg_rating = avg_result.scalar()
        
        # Helpful percentage
        helpful_stmt = select(
            func.count(Feedback.id).filter(Feedback.helpful == True),
            func.count(Feedback.id).filter(Feedback.helpful.is_not(None)),
        ).where(Feedback.persona_id == persona_id)
        
        helpful_result = await self.session.execute(helpful_stmt)
        helpful_count, total_helpful = helpful_result.one()
        
        helpful_percentage = (
            (helpful_count / total_helpful * 100) if total_helpful > 0 else None
        )
        
        return {
            "average_rating": float(avg_rating) if avg_rating else None,
            "helpful_percentage": helpful_percentage,
            "total_feedback": await self.session.scalar(
                select(func.count(Feedback.id)).where(
                    Feedback.persona_id == persona_id
                )
            ),
        }