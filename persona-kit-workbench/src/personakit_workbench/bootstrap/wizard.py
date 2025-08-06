"""Interactive bootstrap wizard for PersonaKit."""
import asyncio
from datetime import UTC, datetime, time
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, available_timezones

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..api_client import PersonaKitClient

console = Console()


class BootstrapWizard:
    """Interactive wizard for bootstrapping PersonaKit."""

    def __init__(self, client: PersonaKitClient) -> None:
        """Initialize wizard with API client."""
        self.client = client
        self.person_id: UUID | None = None
        self.responses: dict[str, Any] = {}

    async def run(self, person_id: str | None = None) -> UUID:
        """Run the bootstrap wizard."""
        console.print("\n[bold cyan]Welcome to PersonaKit![/bold cyan]")
        console.print("Let's learn about your work patterns in just a few minutes.\n")

        # Get or create person ID
        if person_id:
            self.person_id = UUID(person_id)
            console.print(f"Setting up profile for: [green]{self.person_id}[/green]\n")
        else:
            self.person_id = uuid4()
            console.print(f"Creating new profile: [green]{self.person_id}[/green]\n")

        # Run through questions
        await self._ask_work_schedule()
        await self._ask_productivity_time()
        await self._ask_focus_duration()
        await self._ask_flow_disruptors()

        # Show summary
        self._show_summary()

        # Create observations
        if Confirm.ask("\nCreate your PersonaKit profile with these settings?"):
            await self._create_observations()
            console.print("\n[bold green]✓ Profile created successfully![/bold green]")
            console.print(
                "\nYou can now use [cyan]persona-kit suggest[/cyan] to get personalized work suggestions."
            )
            return self.person_id
        else:
            console.print("\n[yellow]Setup cancelled.[/yellow]")
            raise KeyboardInterrupt()

    async def _ask_work_schedule(self) -> None:
        """Ask about work start time and timezone."""
        console.print("[bold]1. Work Schedule[/bold]")

        # Ask for timezone first
        default_tz = "America/New_York"
        tz_input = Prompt.ask(
            "What timezone are you in?",
            default=default_tz,
        )

        # Validate timezone
        if tz_input not in available_timezones():
            console.print(f"[yellow]Unknown timezone '{tz_input}', using {default_tz}[/yellow]")
            tz_input = default_tz

        self.responses["timezone"] = tz_input

        # Ask for work start time
        while True:
            time_str = Prompt.ask(
                "What time do you usually start work?",
                default="9:00 AM",
            )
            try:
                # Parse time
                parsed_time = self._parse_time(time_str)
                self.responses["work_start_time"] = parsed_time
                break
            except ValueError:
                console.print("[red]Invalid time format. Please use HH:MM AM/PM[/red]")

        console.print()

    async def _ask_productivity_time(self) -> None:
        """Ask about peak productivity times."""
        console.print("[bold]2. Peak Productivity[/bold]")

        choices = {
            "1": "morning",
            "2": "afternoon",
            "3": "evening",
            "4": "varies",
        }

        console.print("When are you most productive?")
        for key, value in choices.items():
            console.print(f"  {key}. {value.title()}")

        while True:
            choice = Prompt.ask("Choose", choices=list(choices.keys()))
            self.responses["most_productive"] = choices[choice]
            break

        console.print()

    async def _ask_focus_duration(self) -> None:
        """Ask about typical focus duration."""
        console.print("[bold]3. Focus Duration[/bold]")

        choices = {
            "1": "30min",
            "2": "1hr",
            "3": "2hr+",
        }

        console.print("How long can you typically focus without a break?")
        for key, value in choices.items():
            console.print(f"  {key}. {value}")

        while True:
            choice = Prompt.ask("Choose", choices=list(choices.keys()))
            self.responses["focus_duration"] = choices[choice]
            break

        console.print()

    async def _ask_flow_disruptors(self) -> None:
        """Ask about what disrupts flow."""
        console.print("[bold]4. Flow Disruptors[/bold]")

        choices = {
            "1": "meetings",
            "2": "slack",
            "3": "email",
            "4": "context-switches",
        }

        console.print("What disrupts your flow the most?")
        for key, value in choices.items():
            console.print(f"  {key}. {value.title()}")

        while True:
            choice = Prompt.ask("Choose", choices=list(choices.keys()))
            self.responses["flow_disruptor"] = choices[choice]
            break

        console.print()

    def _show_summary(self) -> None:
        """Show summary of responses."""
        console.print("\n[bold]Summary of your work patterns:[/bold]\n")

        table = Table(show_header=False, box=None)
        table.add_column(style="cyan", width=20)
        table.add_column()

        table.add_row("Timezone:", self.responses["timezone"])
        table.add_row(
            "Work starts:",
            self.responses["work_start_time"].strftime("%I:%M %p"),
        )
        table.add_row("Most productive:", self.responses["most_productive"])
        table.add_row("Focus duration:", self.responses["focus_duration"])
        table.add_row("Main disruptor:", self.responses["flow_disruptor"])

        console.print(table)

    async def _create_observations(self) -> None:
        """Create observations from wizard responses."""
        console.print("\n[dim]Creating observations...[/dim]")

        # Create user input observation with wizard responses
        await self.client.create_observation(
            person_id=self.person_id,
            observation_type="user_input",
            content={
                "type": "wizard_response",
                "responses": {
                    "timezone": self.responses["timezone"],
                    "work_start_time": self.responses["work_start_time"].isoformat(),
                    "most_productive": self.responses["most_productive"],
                    "focus_duration": self.responses["focus_duration"],
                    "flow_disruptor": self.responses["flow_disruptor"],
                },
            },
            meta={
                "source": "bootstrap_wizard",
                "version": "1.0",
            },
        )

        # Create a sample work session observation for immediate results
        now = datetime.now(UTC)
        work_start = self.responses["work_start_time"]
        
        # Create datetime for today with work start time
        session_start = now.replace(
            hour=work_start.hour,
            minute=work_start.minute,
            second=0,
            microsecond=0,
        )

        # Map productivity time to score
        productivity_score = {
            "morning": 5 if 6 <= work_start.hour <= 11 else 3,
            "afternoon": 5 if 12 <= work_start.hour <= 17 else 3,
            "evening": 5 if 18 <= work_start.hour <= 23 else 3,
            "varies": 4,
        }.get(self.responses["most_productive"], 3)

        await self.client.create_observation(
            person_id=self.person_id,
            observation_type="work_session",
            content={
                "start": session_start.isoformat(),
                "duration_minutes": 90,
                "productivity_score": productivity_score,
                "interruptions": 0,
            },
            meta={
                "source": "bootstrap_wizard",
                "note": "Initial session for immediate persona generation",
            },
        )

    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object."""
        time_str = time_str.strip().upper()

        # Handle common formats
        for fmt in ["%I:%M %p", "%I:%M%p", "%I %p", "%I%p", "%H:%M"]:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.time()
            except ValueError:
                continue

        raise ValueError(f"Could not parse time: {time_str}")


async def main() -> None:
    """Run wizard standalone for testing."""
    async with PersonaKitClient() as client:
        wizard = BootstrapWizard(client)
        try:
            person_id = await wizard.run()
            console.print(f"\n[green]Setup complete! Person ID: {person_id}[/green]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Wizard cancelled.[/yellow]")


if __name__ == "__main__":
    asyncio.run(main())