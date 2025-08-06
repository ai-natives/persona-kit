"""Daily Work Optimizer mapper for generating work optimization personas."""
import logging
from datetime import UTC, datetime
from typing import Any

from ..models.mindscape import Mindscape
from .base import PersonaMapper

logger = logging.getLogger(__name__)


class DailyWorkOptimizer(PersonaMapper):
    """
    Mapper that generates personas for daily work optimization.

    Analyzes work patterns, energy levels, and productivity traits
    to create time-aware suggestions for optimal work scheduling.
    """

    def __init__(self) -> None:
        """Initialize Daily Work Optimizer mapper."""
        super().__init__(
            mapper_id="daily_work_optimizer",
            ttl_hours=24,  # Daily personas expire after 24 hours
        )

    def get_required_traits(self) -> list[str]:
        """Get traits required for work optimization."""
        return [
            "work.energy_patterns",
            "work.focus_duration",
            "productivity.peak_hours",
            "work.task_switching_cost",
            "current_state.energy_level",
        ]

    def map_to_persona(
        self, mindscape: Mindscape, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Generate work optimization persona from mindscape.

        Args:
            mindscape: Source mindscape with work-related traits
            context: Optional context including:
                - current_time: Current datetime
                - day_of_week: Monday-Sunday
                - upcoming_meetings: List of upcoming meetings

        Returns:
            Persona configuration with work optimization suggestions
        """
        context = context or {}
        current_time = context.get("current_time", datetime.now(UTC))
        current_hour = current_time.hour

        # Extract trait values
        energy_patterns = self._extract_trait_value(
            mindscape, "work.energy_patterns", {}
        )
        focus_duration = self._extract_trait_value(mindscape, "work.focus_duration", {})
        peak_hours = self._extract_trait_value(
            mindscape, "productivity.peak_hours", []
        )
        task_switching_cost = self._extract_trait_value(
            mindscape, "work.task_switching_cost", "medium"
        )
        # current_energy not used directly as we determine from patterns
        # self._extract_trait_value(
        #     mindscape, "current_state.energy_level", "medium"
        # )

        # Determine current energy state from patterns
        energy_state = self._determine_energy_state(current_hour, energy_patterns)

        # Generate core persona (stable throughout the day)
        core = {
            "work_style": {
                "focus_blocks": self._calculate_focus_blocks(focus_duration),
                "task_switching_tolerance": self._map_switching_tolerance(
                    task_switching_cost
                ),
                "peak_performance_windows": peak_hours,
            },
            "preferences": {
                "meeting_buffer_time": self._calculate_meeting_buffer(
                    task_switching_cost
                ),
                "break_frequency": self._calculate_break_frequency(focus_duration),
                "communication_batching": task_switching_cost == "high",
            },
        }

        # Generate overlay (context-specific adjustments)
        overlay = {
            "current_state": {
                "energy_level": energy_state,
                "is_peak_time": self._is_peak_time(current_hour, peak_hours),
                "recommended_task_type": self._recommend_task_type(
                    energy_state, current_hour
                ),
            },
            "suggestions": self._generate_suggestions(
                energy_state,
                current_hour,
                focus_duration,
                context.get("upcoming_meetings", []),
            ),
        }

        return {"core": core, "overlay": overlay}

    def _determine_energy_state(
        self, current_hour: int, energy_patterns: dict[str, Any]
    ) -> str:
        """Determine current energy state based on patterns."""
        # Check if current hour falls in high energy slots
        high_slots = energy_patterns.get("high_energy_slots", [])
        for slot in high_slots:
            if self._hour_in_slot(current_hour, slot):
                return "high"

        # Check low energy slots
        low_slots = energy_patterns.get("low_energy_slots", [])
        for slot in low_slots:
            if self._hour_in_slot(current_hour, slot):
                return "low"

        return "medium"

    def _hour_in_slot(self, hour: int, slot: str) -> bool:
        """Check if hour falls within time slot (e.g., "09:00-11:00")."""
        try:
            start_str, end_str = slot.split("-")
            start_hour = int(start_str.split(":")[0])
            end_hour = int(end_str.split(":")[0])
            return start_hour <= hour < end_hour
        except (ValueError, IndexError):
            return False

    def _is_peak_time(self, current_hour: int, peak_hours: list[str]) -> bool:
        """Check if current hour is within peak performance time."""
        for slot in peak_hours:
            if self._hour_in_slot(current_hour, slot):
                return True
        return False

    def _calculate_focus_blocks(self, focus_duration: dict[str, Any]) -> dict[str, int]:
        """Calculate recommended focus block durations."""
        median_duration = focus_duration.get("p50", 60)
        p90_duration = focus_duration.get("p90", 90)

        return {
            "default": median_duration,
            "deep_work": p90_duration,
            "light_work": max(30, median_duration // 2),
        }

    def _map_switching_tolerance(self, cost: str) -> str:
        """Map task switching cost to tolerance level."""
        mapping = {
            "high": "low",  # High cost = low tolerance
            "medium": "medium",
            "low": "high",  # Low cost = high tolerance
        }
        return mapping.get(cost, "medium")

    def _calculate_meeting_buffer(self, task_switching_cost: str) -> int:
        """Calculate buffer time needed after meetings."""
        buffers = {"high": 30, "medium": 15, "low": 5}
        return buffers.get(task_switching_cost, 15)

    def _calculate_break_frequency(self, focus_duration: dict[str, Any]) -> str:
        """Calculate recommended break frequency."""
        median_duration = focus_duration.get("p50", 60)

        if median_duration >= 90:
            return "every_90_min"
        elif median_duration >= 60:
            return "every_60_min"
        else:
            return "every_45_min"

    def _recommend_task_type(self, energy_state: str, current_hour: int) -> str:
        """Recommend task type based on energy and time."""
        if energy_state == "high":
            return "complex_creative"
        elif energy_state == "low":
            return "administrative"
        else:
            # Medium energy - check time of day
            if 9 <= current_hour <= 11 or 14 <= current_hour <= 16:
                return "analytical"
            else:
                return "collaborative"

    def _generate_suggestions(
        self,
        energy_state: str,
        current_hour: int,
        focus_duration: dict[str, Any],
        upcoming_meetings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate actionable suggestions for current context."""
        suggestions = []

        # Energy-based suggestions
        if energy_state == "high":
            suggestions.append({
                "type": "task_recommendation",
                "priority": "high",
                "title": "Deep Work Window",
                "description": "Your energy is high. Block the next 90 minutes for your most challenging work.",
                "action": "schedule_focus_block",
                "duration_minutes": focus_duration.get("p90", 90),
            })
        elif energy_state == "low":
            suggestions.append({
                "type": "break_recommendation",
                "priority": "high",
                "title": "Energy Recovery",
                "description": "Low energy detected. Take a 15-minute break or handle routine tasks.",
                "action": "take_break",
                "duration_minutes": 15,
            })

        # Meeting preparation
        next_meeting = self._get_next_meeting(upcoming_meetings)
        if next_meeting and self._meeting_within_hour(next_meeting):
            suggestions.append({
                "type": "meeting_prep",
                "priority": "medium",
                "title": "Meeting Preparation",
                "description": f"Prepare for upcoming meeting: {next_meeting.get('title', 'Meeting')}",
                "action": "prepare_meeting",
                "duration_minutes": 10,
            })

        # Time-specific suggestions
        if current_hour >= 16 and energy_state != "low":
            suggestions.append({
                "type": "daily_planning",
                "priority": "medium",
                "title": "Tomorrow Planning",
                "description": "End of day approaching. Review today and plan tomorrow's priorities.",
                "action": "daily_review",
                "duration_minutes": 15,
            })

        return suggestions

    def _get_next_meeting(
        self, meetings: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Get the next upcoming meeting."""
        if not meetings:
            return None

        now = datetime.now(UTC)
        future_meetings = [
            m for m in meetings
            if isinstance(m.get("start"), datetime) and m["start"] > now
        ]

        if future_meetings:
            return min(future_meetings, key=lambda m: m["start"])
        return None

    def _meeting_within_hour(self, meeting: dict[str, Any]) -> bool:
        """Check if meeting starts within the next hour."""
        if not meeting or "start" not in meeting:
            return False

        now = datetime.now(UTC)
        meeting_start = meeting["start"]

        if isinstance(meeting_start, datetime):
            time_until = (meeting_start - now).total_seconds() / 60
            return 0 < time_until <= 60

        return False
