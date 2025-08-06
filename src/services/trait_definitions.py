"""Trait definitions and structures for PersonaKit."""
from typing import Any, TypedDict


class EnergyPattern(TypedDict):
    """Energy level patterns throughout the day."""
    high_energy_slots: list[str]  # e.g., ["09:00-11:00", "14:00-16:00"]
    low_energy_slots: list[str]   # e.g., ["13:00-14:00"]
    sample_size: int              # Number of observations used


class FocusDuration(TypedDict):
    """Focus duration statistics."""
    p50: int                      # Median duration in minutes
    p90: int                      # 90th percentile in minutes
    recent_trend: str             # "increasing", "decreasing", or "stable"


class PeakHours(TypedDict):
    """Peak productivity time ranges."""
    start: str                    # e.g., "09:00"
    end: str                      # e.g., "11:00"
    confidence: float             # 0.0 to 1.0


class PeakHoursData(TypedDict):
    """Complete peak hours data."""
    primary: PeakHours
    secondary: PeakHours | None


# Complete trait structure
TRAIT_SCHEMA = {
    "work.energy_patterns": {
        "type": "object",
        "properties": {
            "high_energy_slots": {"type": "array", "items": {"type": "string"}},
            "low_energy_slots": {"type": "array", "items": {"type": "string"}},
            "sample_size": {"type": "integer"}
        }
    },
    "work.focus_duration": {
        "type": "object",
        "properties": {
            "p50": {"type": "integer"},
            "p90": {"type": "integer"},
            "recent_trend": {"type": "string", "enum": ["increasing", "decreasing", "stable"]}
        }
    },
    "work.peak_hours": {
        "type": "object",
        "properties": {
            "primary": {
                "type": "object",
                "properties": {
                    "start": {"type": "string"},
                    "end": {"type": "string"},
                    "confidence": {"type": "number"}
                }
            },
            "secondary": {
                "type": ["object", "null"],
                "properties": {
                    "start": {"type": "string"},
                    "end": {"type": "string"},
                    "confidence": {"type": "number"}
                }
            }
        }
    }
}


def get_default_traits() -> dict[str, Any]:
    """Get default trait values for a new mindscape."""
    return {
        "work.energy_patterns": {
            "high_energy_slots": [],
            "low_energy_slots": [],
            "sample_size": 0
        },
        "work.focus_duration": {
            "p50": 0,
            "p90": 0,
            "recent_trend": "stable"
        },
        "work.peak_hours": {
            "primary": None,
            "secondary": None
        }
    }
