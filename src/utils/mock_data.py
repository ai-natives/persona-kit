"""Mock data generator for testing."""
import random
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any


class MockDataGenerator:
    """Generate mock observations for testing."""

    def __init__(self, person_id: uuid.UUID | None = None) -> None:
        """Initialize generator."""
        self.person_id = person_id or uuid.uuid4()

    def generate_work_session(
        self,
        start_time: datetime | None = None,
        duration_minutes: int | None = None,
    ) -> dict[str, Any]:
        """Generate a mock work session observation."""
        if not start_time:
            # Random time in the past week
            days_ago = random.randint(0, 7)
            hour = random.choice([9, 10, 11, 14, 15, 16])  # Work hours
            start_time = datetime.now(UTC).replace(
                hour=hour, minute=0, second=0, microsecond=0
            ) - timedelta(days=days_ago)

        if not duration_minutes:
            duration_minutes = random.choice([30, 45, 60, 90, 120])

        # Productivity correlates with time of day
        hour = start_time.hour
        if 9 <= hour <= 11:  # Morning peak
            productivity = random.choice([4, 5, 5])  # High
        elif 14 <= hour <= 16:  # Afternoon peak
            productivity = random.choice([3, 4, 4])  # Medium-high
        else:
            productivity = random.choice([2, 3, 3])  # Lower

        # Interruptions inversely correlate with productivity
        interruptions = max(0, 5 - productivity + random.randint(-1, 1))

        return {
            "type": "work_session",
            "content": {
                "start": start_time.isoformat(),
                "end": (start_time + timedelta(minutes=duration_minutes)).isoformat(),
                "duration_minutes": duration_minutes,
                "productivity_score": productivity,
                "interruptions": interruptions,
                "activity": random.choice(["coding", "writing", "analysis", "design"]),
                "project": "PersonaKit",
            },
            "meta": {"source": "mock_generator"},
        }

    def generate_user_input(self, input_type: str = "energy_check") -> dict[str, Any]:
        """Generate a mock user input observation."""
        if input_type == "energy_check":
            return {
                "type": "user_input",
                "content": {
                    "type": "energy_check",
                    "energy_level": random.choice(["low", "medium", "high"]),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                "meta": {"source": "mock_generator"},
            }
        elif input_type == "wizard_response":
            return {
                "type": "user_input",
                "content": {
                    "type": "wizard_response",
                    "responses": {
                        "start_time": "09:00",
                        "most_productive": random.choice(["morning", "afternoon", "varies"]),
                        "focus_duration": random.choice(["30min", "1hr", "2hr+"]),
                        "flow_disruptor": random.choice(["meetings", "slack", "context-switches"]),
                    },
                },
                "meta": {"source": "mock_generator", "wizard_version": "1.0"},
            }
        else:
            raise ValueError(f"Unknown input type: {input_type}")

    def generate_calendar_event(
        self, event_type: str = "meeting", start_time: datetime | None = None
    ) -> dict[str, Any]:
        """Generate a mock calendar event observation."""
        if not start_time:
            start_time = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)

        if event_type == "meeting":
            duration = random.choice([30, 60, 90])
            return {
                "type": "calendar_event",
                "content": {
                    "id": f"evt_{uuid.uuid4().hex[:8]}",
                    "type": "meeting",
                    "title": random.choice([
                        "Team Standup",
                        "1:1 Meeting",
                        "Project Review",
                        "Planning Session",
                    ]),
                    "start": start_time.isoformat(),
                    "end": (start_time + timedelta(minutes=duration)).isoformat(),
                    "duration_minutes": duration,
                    "attendees": random.randint(2, 10),
                },
                "meta": {"source": "mock_calendar"},
            }
        elif event_type == "focus_block":
            duration = random.choice([90, 120, 180])
            return {
                "type": "calendar_event",
                "content": {
                    "id": f"evt_{uuid.uuid4().hex[:8]}",
                    "type": "focus_block",
                    "title": "Deep Work",
                    "start": start_time.isoformat(),
                    "end": (start_time + timedelta(minutes=duration)).isoformat(),
                    "duration_minutes": duration,
                },
                "meta": {"source": "mock_calendar"},
            }
        else:
            raise ValueError(f"Unknown event type: {event_type}")

    def generate_work_pattern(self, days: int = 7) -> list[dict[str, Any]]:
        """Generate a realistic work pattern over multiple days."""
        observations = []

        # Start with wizard response
        observations.append(self.generate_user_input("wizard_response"))

        # Generate daily patterns
        for day in range(days):
            date = datetime.now(UTC) - timedelta(days=day)

            # Morning energy check
            morning_check = self.generate_user_input("energy_check")
            morning_check["content"]["timestamp"] = date.replace(
                hour=8, minute=30
            ).isoformat()
            observations.append(morning_check)

            # Morning work session
            observations.append(
                self.generate_work_session(
                    start_time=date.replace(hour=9, minute=0),
                    duration_minutes=random.choice([90, 120]),
                )
            )

            # Meeting
            if random.random() > 0.3:  # 70% chance of meetings
                observations.append(
                    self.generate_calendar_event(
                        "meeting",
                        start_time=date.replace(hour=11, minute=0),
                    )
                )

            # Afternoon work session
            observations.append(
                self.generate_work_session(
                    start_time=date.replace(hour=14, minute=0),
                    duration_minutes=random.choice([60, 90, 120]),
                )
            )

            # Occasional focus block
            if random.random() > 0.6:  # 40% chance
                observations.append(
                    self.generate_calendar_event(
                        "focus_block",
                        start_time=date.replace(hour=16, minute=0),
                    )
                )

        return observations
