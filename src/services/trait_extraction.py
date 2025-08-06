"""Trait extraction service for processing observations."""
from datetime import datetime
from typing import Any

from ..models.observation import ObservationType


class TraitExtractor:
    """Extract traits from observations."""

    def extract_traits(
        self, observation_type: ObservationType, content: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """
        Extract traits from observation content.

        Returns dict of traits with structure:
        {
            "trait.name": {
                "value": <value>,
                "confidence": 0.0-1.0,
                "sample_size": int
            }
        }
        """
        if observation_type == ObservationType.WORK_SESSION:
            return self._extract_work_session_traits(content)
        elif observation_type == ObservationType.USER_INPUT:
            return self._extract_user_input_traits(content)
        elif observation_type == ObservationType.CALENDAR_EVENT:
            return self._extract_calendar_traits(content)
        else:
            return {}

    def _extract_work_session_traits(
        self, content: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """Extract traits from work session observations."""
        traits = {}

        # Extract focus duration
        if duration := content.get("duration_minutes"):
            traits["work.focus_duration"] = {
                "value": duration,
                "confidence": 0.9,  # High confidence for direct measurement
                "sample_size": 1,
            }

        # Extract energy patterns based on time and productivity
        if (
            (start_time := content.get("start")) and
            (productivity := content.get("productivity_score"))
        ):
            hour = self._parse_hour(start_time)
            if hour is not None:
                # Track high productivity hours
                if productivity >= 4:  # 4-5 on scale
                    traits["work.peak_hours"] = {
                        "value": [f"{hour:02d}:00-{(hour+1):02d}:00"],
                        "confidence": 0.7,
                        "sample_size": 1,
                    }

                # Energy level inference from productivity
                energy_level = "high" if productivity >= 4 else "medium" if productivity >= 3 else "low"
                traits["current_state.energy_level"] = {
                    "value": energy_level,
                    "confidence": 0.6,
                    "sample_size": 1,
                }

        # Task switching cost from interruptions
        if interruptions := content.get("interruptions"):
            # Higher interruptions = higher task switching cost
            cost = "high" if interruptions >= 3 else "medium" if interruptions >= 1 else "low"
            traits["work.task_switching_cost"] = {
                "value": cost,
                "confidence": 0.7,
                "sample_size": 1,
            }

        return traits

    def _extract_user_input_traits(
        self, content: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """Extract traits from user input observations."""
        traits = {}

        # Handle wizard responses or direct user input
        if response_type := content.get("type"):
            if response_type == "wizard_response":
                return self._extract_wizard_traits(content.get("responses", {}))
            elif response_type == "energy_check":
                if energy := content.get("energy_level"):
                    traits["current_state.energy_level"] = {
                        "value": energy,
                        "confidence": 1.0,  # Direct user input
                        "sample_size": 1,
                    }

        return traits

    def _extract_calendar_traits(
        self, content: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """Extract traits from calendar observations."""
        traits = {}

        # Meeting recovery time inference
        if event_type := content.get("type"):
            if event_type == "meeting":
                # After meetings, assume recovery time needed
                duration = content.get("duration_minutes", 60)
                recovery_time = 15 if duration <= 30 else 30 if duration <= 60 else 45

                traits["work.meeting_recovery_time"] = {
                    "value": recovery_time,
                    "confidence": 0.5,  # Lower confidence for inference
                    "sample_size": 1,
                }

        return traits

    def _extract_wizard_traits(
        self, responses: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """Extract traits from wizard responses."""
        traits = {}

        # Productivity time preference
        if productive_time := responses.get("most_productive"):
            time_map = {
                "morning": ["06:00-12:00"],
                "afternoon": ["12:00-18:00"],
                "evening": ["18:00-23:00"],
                "varies": ["09:00-11:00", "14:00-16:00"],  # Default peaks
            }
            if time_ranges := time_map.get(productive_time):
                traits["work.energy_patterns"] = {
                    "value": time_ranges,
                    "confidence": 0.8,
                    "sample_size": 1,
                }
                traits["work.peak_hours"] = {
                    "value": time_ranges,
                    "confidence": 0.8,
                    "sample_size": 1,
                }

        # Focus duration
        if focus_duration := responses.get("focus_duration"):
            duration_map = {"30min": 30, "1hr": 60, "2hr+": 120}
            if minutes := duration_map.get(focus_duration):
                traits["work.focus_duration"] = {
                    "value": minutes,
                    "confidence": 0.9,
                    "sample_size": 1,
                }

        # Flow disruptors -> task switching cost
        if disruptor := responses.get("flow_disruptor"):
            cost_map = {
                "meetings": "high",
                "slack": "medium",
                "context-switches": "high",
                "email": "low",
            }
            if cost := cost_map.get(disruptor, "medium"):
                traits["work.task_switching_cost"] = {
                    "value": cost,
                    "confidence": 0.8,
                    "sample_size": 1,
                }

        return traits

    def _parse_hour(self, timestamp: str) -> int | None:
        """Parse hour from ISO timestamp string."""
        try:
            # Handle both datetime objects and strings
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                dt = timestamp
            return dt.hour
        except (ValueError, AttributeError):
            return None
