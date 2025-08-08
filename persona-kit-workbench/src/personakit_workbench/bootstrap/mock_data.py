"""Mock data generator for PersonaKit testing."""
import random
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..api_client import PersonaKitClient

console = Console()


class MockDataGenerator:
    """Generate realistic mock data for PersonaKit."""

    def __init__(self, client: PersonaKitClient) -> None:
        """Initialize generator with API client."""
        self.client = client

    async def generate(
        self,
        person_id: UUID,
        days: int = 7,
        verbose: bool = True,
    ) -> dict[str, int]:
        """Generate mock observations for specified number of days."""
        if verbose:
            console.print(
                f"\n[bold cyan]Generating {days} days of mock data...[/bold cyan]\n"
            )

        stats = {
            "work_sessions": 0,
            "calendar_events": 0,
            "user_inputs": 0,
            "narratives": 0,
            "total": 0,
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating observations...", total=days)

            # Start from days ago
            start_date = datetime.now(UTC) - timedelta(days=days)

            for day_offset in range(days):
                current_date = start_date + timedelta(days=day_offset)
                
                # Skip weekends
                if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    progress.advance(task)
                    continue

                # Generate work sessions
                sessions = await self._generate_work_sessions(
                    person_id, current_date
                )
                stats["work_sessions"] += sessions

                # Generate calendar events
                events = await self._generate_calendar_events(
                    person_id, current_date
                )
                stats["calendar_events"] += events

                # Occasionally add user input
                if random.random() < 0.3:  # 30% chance
                    await self._generate_user_input(person_id, current_date)
                    stats["user_inputs"] += 1

                # Generate narratives
                narratives = await self._generate_narratives(
                    person_id, current_date
                )
                stats["narratives"] += narratives

                progress.advance(task)

        stats["total"] = sum(stats.values())

        if verbose:
            self._print_summary(stats)

        return stats

    async def _generate_work_sessions(
        self, person_id: UUID, date: datetime
    ) -> int:
        """Generate work session observations for a day."""
        count = 0
        
        # Morning session (9 AM - 12 PM)
        if random.random() < 0.9:  # 90% chance
            start_time = date.replace(
                hour=8 + random.randint(0, 1),
                minute=random.choice([0, 15, 30, 45]),
            )
            duration = random.randint(90, 180)  # 1.5-3 hours
            
            await self.client.create_observation(
                person_id=person_id,
                observation_type="work_session",
                content={
                    "start": start_time.isoformat(),
                    "duration_minutes": duration,
                    "productivity_score": self._get_productivity_score("morning"),
                    "interruptions": random.randint(0, 3),
                },
                meta={"source": "mock_data_generator"},
            )
            count += 1

        # Afternoon session (1 PM - 5 PM)
        if random.random() < 0.8:  # 80% chance
            start_time = date.replace(
                hour=13 + random.randint(0, 1),
                minute=random.choice([0, 15, 30, 45]),
            )
            duration = random.randint(60, 150)  # 1-2.5 hours
            
            await self.client.create_observation(
                person_id=person_id,
                observation_type="work_session",
                content={
                    "start": start_time.isoformat(),
                    "duration_minutes": duration,
                    "productivity_score": self._get_productivity_score("afternoon"),
                    "interruptions": random.randint(1, 5),
                },
                meta={"source": "mock_data_generator"},
            )
            count += 1

        # Evening session (6 PM - 9 PM)
        if random.random() < 0.3:  # 30% chance
            start_time = date.replace(
                hour=18 + random.randint(0, 1),
                minute=random.choice([0, 15, 30, 45]),
            )
            duration = random.randint(30, 90)  # 0.5-1.5 hours
            
            await self.client.create_observation(
                person_id=person_id,
                observation_type="work_session",
                content={
                    "start": start_time.isoformat(),
                    "duration_minutes": duration,
                    "productivity_score": self._get_productivity_score("evening"),
                    "interruptions": random.randint(0, 2),
                },
                meta={"source": "mock_data_generator"},
            )
            count += 1

        return count

    async def _generate_calendar_events(
        self, person_id: UUID, date: datetime
    ) -> int:
        """Generate calendar event observations for a day."""
        count = 0
        events = []

        # Morning standup (50% chance)
        if random.random() < 0.5:
            events.append({
                "start": date.replace(hour=9, minute=0),
                "duration": 30,
                "type": "meeting",
                "title": "Team Standup",
            })

        # Mid-morning meeting (40% chance)
        if random.random() < 0.4:
            events.append({
                "start": date.replace(hour=10, minute=30),
                "duration": 60,
                "type": "meeting",
                "title": random.choice([
                    "1:1 with Manager",
                    "Project Review",
                    "Design Discussion",
                ]),
            })

        # Lunch block (80% chance)
        if random.random() < 0.8:
            events.append({
                "start": date.replace(hour=12, minute=0),
                "duration": 60,
                "type": "break",
                "title": "Lunch",
            })

        # Afternoon meetings (60% chance for 1-2 meetings)
        if random.random() < 0.6:
            num_meetings = random.randint(1, 2)
            for i in range(num_meetings):
                start_hour = 14 + i * 2
                events.append({
                    "start": date.replace(hour=start_hour, minute=0),
                    "duration": random.choice([30, 60]),
                    "type": "meeting",
                    "title": random.choice([
                        "Sprint Planning",
                        "Code Review",
                        "Customer Call",
                        "Team Sync",
                    ]),
                })

        # Create observations for each event
        for event in events:
            await self.client.create_observation(
                person_id=person_id,
                observation_type="calendar_event",
                content={
                    "start": event["start"].isoformat(),
                    "end": (
                        event["start"] + timedelta(minutes=event["duration"])
                    ).isoformat(),
                    "type": event["type"],
                    "title": event["title"],
                    "duration_minutes": event["duration"],
                },
                meta={"source": "mock_data_generator"},
            )
            count += 1

        return count

    async def _generate_user_input(
        self, person_id: UUID, date: datetime
    ) -> None:
        """Generate occasional user input observations."""
        # Energy check
        energy_levels = ["low", "medium", "high"]
        weights = [0.2, 0.5, 0.3]  # More likely to be medium
        
        await self.client.create_observation(
            person_id=person_id,
            observation_type="user_input",
            content={
                "type": "energy_check",
                "energy_level": random.choices(energy_levels, weights=weights)[0],
                "timestamp": date.replace(
                    hour=random.randint(8, 10), minute=0
                ).isoformat(),
            },
            meta={"source": "mock_data_generator"},
        )

    async def _generate_narratives(
        self, person_id: UUID, date: datetime
    ) -> int:
        """Generate narrative observations for a day."""
        count = 0
        
        # Self-observation narratives (40% chance per day)
        if random.random() < 0.4:
            # Morning reflection
            if random.random() < 0.5:
                observations = [
                    "Started the day feeling energized after a good night's sleep. Ready to tackle the complex refactoring task.",
                    "Feeling a bit foggy this morning. Need extra coffee before diving into the code review.",
                    "Noticed I'm most focused in the first two hours. Should schedule important work then.",
                    "The open office is particularly noisy today. Switching to noise-cancelling headphones.",
                    "Really enjoying the new standing desk setup. Helps me stay alert during long coding sessions.",
                ]
                
                await self.client.create_self_observation(
                    person_id=person_id,
                    text=random.choice(observations),
                    tags=["morning", "reflection", "mock"],
                    context={
                        "source": "mock_data_generator",
                        "time_of_day": "morning",
                        "date": date.isoformat(),
                    },
                )
                count += 1
            
            # Afternoon observation
            if random.random() < 0.5:
                observations = [
                    "Post-lunch energy dip hit hard today. Taking a short walk helped reset my focus.",
                    "Back-to-back meetings really fragmented my afternoon. Need better calendar blocking.",
                    "Found my flow state while working on the API integration. Time just flew by.",
                    "Pair programming session was incredibly productive. We solved the bug in half the expected time.",
                    "Switching between contexts is exhausting. Need to batch similar tasks together.",
                ]
                
                await self.client.create_self_observation(
                    person_id=person_id,
                    text=random.choice(observations),
                    tags=["afternoon", "productivity", "mock"],
                    context={
                        "source": "mock_data_generator",
                        "time_of_day": "afternoon",
                        "date": date.isoformat(),
                    },
                )
                count += 1
        
        # Curation narratives (20% chance per day)
        if random.random() < 0.2:
            curations = [
                {
                    "trait_path": "work_patterns.peak_hours",
                    "text": "My peak hours seem to be shifting earlier. I'm most productive from 8-11 AM now.",
                    "tags": ["schedule", "productivity"],
                },
                {
                    "trait_path": "work_preferences.interruption_sensitivity",
                    "text": "Slack notifications are my biggest productivity killer. Need to set better boundaries.",
                    "tags": ["focus", "interruptions"],
                },
                {
                    "trait_path": "energy_patterns.post_meeting_impact",
                    "text": "Video calls drain my energy more than in-person meetings. Need recovery time after.",
                    "tags": ["energy", "meetings"],
                },
                {
                    "trait_path": "work_patterns.focus_duration",
                    "text": "Can maintain deep focus for about 90 minutes before needing a real break.",
                    "tags": ["focus", "time-management"],
                },
            ]
            
            curation = random.choice(curations)
            await self.client.create_curation(
                person_id=person_id,
                trait_path=curation["trait_path"],
                text=curation["text"],
                tags=curation["tags"] + ["mock"],
                context={
                    "source": "mock_data_generator",
                    "date": date.isoformat(),
                },
            )
            count += 1
        
        return count

    def _get_productivity_score(self, time_of_day: str) -> int:
        """Get realistic productivity score based on time of day."""
        if time_of_day == "morning":
            # Morning tends to be high productivity
            return random.choices([3, 4, 5], weights=[0.2, 0.3, 0.5])[0]
        elif time_of_day == "afternoon":
            # Post-lunch slump
            return random.choices([2, 3, 4], weights=[0.3, 0.5, 0.2])[0]
        else:  # evening
            # Variable - some people work well, others are tired
            return random.choices([2, 3, 4, 5], weights=[0.3, 0.3, 0.3, 0.1])[0]

    def _print_summary(self, stats: dict[str, int]) -> None:
        """Print summary of generated data."""
        console.print("\n[bold green]✓ Mock data generated successfully![/bold green]\n")
        console.print(f"  Work sessions:    {stats['work_sessions']}")
        console.print(f"  Calendar events:  {stats['calendar_events']}")
        console.print(f"  User inputs:      {stats['user_inputs']}")
        console.print(f"  Narratives:       {stats['narratives']}")
        console.print(f"  [bold]Total:[/bold]            {stats['total']}")
        console.print(
            "\n[dim]The background worker will process these observations shortly.[/dim]"
        )