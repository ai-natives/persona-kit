"""Feedback processing service."""
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.feedback import Feedback
from ..models.mindscape import Mindscape
from ..repositories.feedback import FeedbackRepository
from ..repositories.mindscape import MindscapeRepository

logger = logging.getLogger(__name__)


class FeedbackProcessor:
    """Process feedback and adjust trait weights."""
    
    # Feedback thresholds and adjustments
    NEGATIVE_FEEDBACK_THRESHOLD = 5
    NEGATIVE_ADJUSTMENT = -0.2  # 20% reduction
    POSITIVE_ADJUSTMENT = 0.1   # 10% increase
    MAX_NEGATIVE_CHANGE = 0.5   # Never reduce more than 50%
    MAX_POSITIVE_WEIGHT = 2.0   # Never more than 2x original
    
    def __init__(self, session: AsyncSession):
        """Initialize feedback processor."""
        self.session = session
        self.feedback_repo = FeedbackRepository(session)
        self.mindscape_repo = MindscapeRepository(session)
    
    async def process_feedback(self, feedback: Feedback) -> None:
        """Process a single feedback item."""
        # Get persona to find person_id
        from ..repositories.persona import PersonaRepository
        persona_repo = PersonaRepository(self.session)
        persona = await persona_repo.get(feedback.persona_id)
        
        if not persona:
            logger.warning(f"Persona {feedback.persona_id} not found for feedback")
            return
        
        # Determine if feedback is negative or positive
        is_negative = (
            (feedback.rating is not None and feedback.rating <= 2) or
            (feedback.helpful is False)
        )
        is_positive = (
            (feedback.rating is not None and feedback.rating >= 4) or
            (feedback.helpful is True)
        )
        
        if not is_negative and not is_positive:
            logger.info("Neutral feedback, no adjustment needed")
            return
        
        # Get suggestion type from context
        suggestion_type = feedback.context.get("suggestion_type")
        if not suggestion_type:
            logger.warning("No suggestion type in feedback context")
            return
        
        # Map suggestion types to traits
        trait_mapping = self._get_trait_mapping(suggestion_type)
        if not trait_mapping:
            logger.warning(f"No trait mapping for suggestion type: {suggestion_type}")
            return
        
        if is_negative:
            await self._process_negative_feedback(
                persona.person_id, trait_mapping, feedback.created_at
            )
        else:
            await self._process_positive_feedback(
                persona.person_id, trait_mapping
            )
    
    def _get_trait_mapping(self, suggestion_type: str) -> list[str]:
        """Map suggestion types to trait names."""
        mapping = {
            "task_recommendation": ["work.energy_patterns", "work.focus_duration"],
            "meeting_recovery": ["work.meeting_recovery", "work.context_switching"],
            "break_reminder": ["work.break_patterns", "work.sustained_attention"],
            "focus_block": ["work.peak_hours", "work.focus_duration"],
            "energy_management": ["work.energy_patterns", "work.fatigue_signals"],
        }
        return mapping.get(suggestion_type, [])
    
    async def _process_negative_feedback(
        self, person_id: uuid.UUID, traits: list[str], feedback_time: datetime
    ) -> None:
        """Process negative feedback with threshold checking."""
        # Count similar negative feedback in time window
        window_start = feedback_time - timedelta(days=7)
        
        # Get all negative feedback for this person in window
        from ..models.persona import Persona
        stmt = select(Feedback).join(
            Persona,
            Feedback.persona_id == Persona.id
        ).where(
            and_(
                Persona.person_id == person_id,
                Feedback.created_at >= window_start,
                Feedback.created_at <= feedback_time,
                (Feedback.rating <= 2) | (Feedback.helpful.is_(False))
            )
        )
        
        result = await self.session.execute(stmt)
        negative_feedback = result.scalars().all()
        
        # Count feedback by suggestion type
        type_counts: dict[str, int] = {}
        for fb in negative_feedback:
            if suggestion_type := fb.context.get("suggestion_type"):
                type_counts[suggestion_type] = type_counts.get(suggestion_type, 0) + 1
        
        # Check if any type exceeds threshold
        for suggestion_type, count in type_counts.items():
            if count >= self.NEGATIVE_FEEDBACK_THRESHOLD:
                logger.info(
                    f"Threshold reached for {suggestion_type}: {count} negative feedback"
                )
                # Get traits for this suggestion type
                affected_traits = self._get_trait_mapping(suggestion_type)
                await self._adjust_trait_weights(
                    person_id, affected_traits, self.NEGATIVE_ADJUSTMENT
                )
    
    async def _process_positive_feedback(
        self, person_id: uuid.UUID, traits: list[str]
    ) -> None:
        """Process positive feedback immediately."""
        await self._adjust_trait_weights(
            person_id, traits, self.POSITIVE_ADJUSTMENT
        )
    
    async def _adjust_trait_weights(
        self, person_id: uuid.UUID, traits: list[str], adjustment: float
    ) -> None:
        """Adjust trait weights in mindscape."""
        # Get current mindscape
        mindscape = await self.mindscape_repo.get_by_person(person_id)
        if not mindscape:
            logger.warning(f"No mindscape found for person {person_id}")
            return
        
        # Update trait weights
        updated = False
        for trait_name in traits:
            if trait_name in mindscape.traits:
                trait_data = mindscape.traits[trait_name]
                
                # Get current weight (default 1.0)
                current_weight = trait_data.get("weight", 1.0)
                
                # Calculate new weight
                new_weight = current_weight * (1 + adjustment)
                
                # Apply limits
                if adjustment < 0:  # Negative adjustment
                    min_weight = 1.0 - self.MAX_NEGATIVE_CHANGE
                    new_weight = max(new_weight, min_weight)
                else:  # Positive adjustment
                    new_weight = min(new_weight, self.MAX_POSITIVE_WEIGHT)
                
                # Update trait
                trait_data["weight"] = round(new_weight, 3)
                trait_data["last_adjusted"] = datetime.now(UTC).isoformat()
                trait_data["adjustment_reason"] = (
                    "negative_feedback_threshold" if adjustment < 0 
                    else "positive_feedback"
                )
                
                logger.info(
                    f"Adjusted {trait_name} weight: {current_weight:.3f} -> {new_weight:.3f}"
                )
                updated = True
        
        if updated:
            # Mark mindscape as modified and JSONB field as changed
            from sqlalchemy.orm import attributes
            attributes.flag_modified(mindscape, "traits")
            mindscape.version += 1
            await self.session.commit()
            logger.info(f"Updated mindscape version to {mindscape.version}")
    
    async def get_feedback_summary(
        self, person_id: uuid.UUID, days: int = 30
    ) -> dict[str, Any]:
        """Get feedback summary for analytics."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        
        # Get all feedback for person's personas
        from ..models.persona import Persona
        stmt = select(Feedback).join(
            Persona,
            Feedback.persona_id == Persona.id
        ).where(
            and_(
                Persona.person_id == person_id,
                Feedback.created_at >= cutoff
            )
        )
        
        result = await self.session.execute(stmt)
        all_feedback = result.scalars().all()
        
        # Calculate statistics
        total = len(all_feedback)
        positive = sum(
            1 for fb in all_feedback 
            if (fb.rating and fb.rating >= 4) or fb.helpful is True
        )
        negative = sum(
            1 for fb in all_feedback 
            if (fb.rating and fb.rating <= 2) or fb.helpful is False
        )
        neutral = total - positive - negative
        
        # Group by suggestion type
        by_type: dict[str, dict[str, int]] = {}
        for fb in all_feedback:
            suggestion_type = fb.context.get("suggestion_type", "unknown")
            if suggestion_type not in by_type:
                by_type[suggestion_type] = {"positive": 0, "negative": 0, "neutral": 0}
            
            if (fb.rating and fb.rating >= 4) or fb.helpful is True:
                by_type[suggestion_type]["positive"] += 1
            elif (fb.rating and fb.rating <= 2) or fb.helpful is False:
                by_type[suggestion_type]["negative"] += 1
            else:
                by_type[suggestion_type]["neutral"] += 1
        
        return {
            "period_days": days,
            "total_feedback": total,
            "positive": positive,
            "negative": negative, 
            "neutral": neutral,
            "positive_rate": round(positive / total * 100, 1) if total > 0 else 0,
            "by_suggestion_type": by_type,
            "average_rating": round(
                sum(fb.rating for fb in all_feedback if fb.rating) / 
                sum(1 for fb in all_feedback if fb.rating), 1
            ) if any(fb.rating for fb in all_feedback) else None,
        }