#!/usr/bin/env python3
"""CLI command for getting work suggestions from PersonaKit."""
import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def get_api_url() -> str:
    """Get API URL from environment or default."""
    return os.getenv("PERSONAKIT_API_URL", "http://localhost:8042")


def get_person_id() -> str:
    """Get person ID from config file or environment."""
    # Check environment first
    person_id = os.getenv("PERSONAKIT_PERSON_ID")
    if person_id:
        return person_id

    # Check config file
    config_path = Path.home() / ".personakit" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            return str(config.get("person_id", ""))

    return ""


async def get_suggestions(person_id: str, current_time: datetime | None = None) -> dict[str, Any]:
    """Get suggestions from PersonaKit API."""
    api_url = get_api_url()

    async with httpx.AsyncClient(timeout=10.0) as client:
        # First, check if we have an active persona
        response = await client.get(
            f"{api_url}/personas/active",
            params={"person_id": person_id}
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get active personas: {response.text}")

        personas = response.json()

        # Look for daily_work_optimizer persona
        work_persona = None
        for persona in personas:
            if persona["mapper_id"] == "daily_work_optimizer":
                work_persona = persona
                break

        # If no active persona, generate one
        if not work_persona:
            console.print("[yellow]No active persona found. Generating new persona...[/yellow]")

            context = {}
            if current_time:
                context["current_time"] = current_time.isoformat()

            response = await client.post(
                f"{api_url}/personas",
                json={
                    "person_id": person_id,
                    "mapper_id": "daily_work_optimizer",
                    "context": context,
                }
            )

            if response.status_code != 200:
                # Check if it's missing traits
                if response.status_code == 422:
                    raise Exception(
                        "Missing required traits. Please run 'persona-kit bootstrap' first."
                    )
                raise Exception(f"Failed to generate persona: {response.text}")

            work_persona = response.json()

        return dict(work_persona)


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable."""
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        if mins > 0:
            return f"{hours}h {mins}m"
        return f"{hours}h"
    return f"{minutes}m"


def display_suggestions(persona: dict[str, Any], verbose: bool = False) -> None:
    """Display suggestions in a formatted way."""
    overlay = persona.get("overlay", {})
    current_state = overlay.get("current_state", {})
    suggestions = overlay.get("suggestions", [])

    # Current state panel
    state_info = Table.grid(padding=1)
    state_info.add_column(style="cyan", no_wrap=True)
    state_info.add_column()

    energy_emoji = {
        "high": "⚡",
        "medium": "🔋",
        "low": "🪫"
    }.get(current_state.get("energy_level", "medium"), "🔋")

    state_info.add_row(
        "Energy Level:",
        f"{energy_emoji} {current_state.get('energy_level', 'unknown').title()}"
    )

    if current_state.get("is_peak_time"):
        state_info.add_row("Peak Time:", "✅ Yes - You're in your optimal performance window!")
    else:
        state_info.add_row("Peak Time:", "❌ No - Consider lighter tasks")

    task_type = current_state.get("recommended_task_type", "general")
    task_emoji = {
        "complex_creative": "🧠",
        "analytical": "📊",
        "administrative": "📝",
        "collaborative": "👥"
    }.get(task_type, "💼")

    state_info.add_row(
        "Recommended Tasks:",
        f"{task_emoji} {task_type.replace('_', ' ').title()}"
    )

    console.print(Panel(
        state_info,
        title="[bold cyan]Current State[/bold cyan]",
        border_style="cyan"
    ))

    # Suggestions
    if suggestions:
        console.print("\n[bold green]Suggestions:[/bold green]\n")

        for i, suggestion in enumerate(suggestions, 1):
            priority_color = {
                "high": "red",
                "medium": "yellow",
                "low": "green"
            }.get(suggestion.get("priority", "medium"), "white")

            # Title with priority
            console.print(
                f"{i}. [bold {priority_color}]{suggestion.get('title', 'Suggestion')}[/bold {priority_color}]"
            )

            # Description
            console.print(f"   {suggestion.get('description', '')}")

            # Duration if available
            if duration := suggestion.get("duration_minutes"):
                console.print(f"   [dim]Duration: {format_duration(duration)}[/dim]")

            # Action if verbose
            if verbose and (action := suggestion.get("action")):
                console.print(f"   [dim]Action: {action}[/dim]")

            console.print()
    else:
        console.print("[yellow]No specific suggestions at this time.[/yellow]")

    # Work preferences if verbose
    if verbose and (core := persona.get("core")):
        console.print("\n[bold blue]Work Preferences:[/bold blue]")

        if work_style := core.get("work_style"):
            if focus_blocks := work_style.get("focus_blocks"):
                console.print(f"  • Default focus duration: {format_duration(focus_blocks.get('default', 60))}")
                console.print(f"  • Deep work duration: {format_duration(focus_blocks.get('deep_work', 90))}")

        if preferences := core.get("preferences"):
            if buffer_time := preferences.get("meeting_buffer_time"):
                console.print(f"  • Meeting buffer: {format_duration(buffer_time)}")
            if break_freq := preferences.get("break_frequency"):
                console.print(f"  • Break frequency: {break_freq.replace('_', ' ')}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Get personalized work suggestions from PersonaKit"
    )
    parser.add_argument(
        "--person-id",
        help="Person ID (defaults to config or PERSONAKIT_PERSON_ID env var)"
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Get suggestions for current time (default)"
    )
    parser.add_argument(
        "--time",
        help="Get suggestions for specific time (ISO format, e.g., 2024-01-15T14:00:00)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show additional details"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )

    args = parser.parse_args()

    # Get person ID
    person_id = args.person_id or get_person_id()
    if not person_id:
        console.print(
            "[red]Error: No person ID provided.[/red]\n"
            "Set PERSONAKIT_PERSON_ID environment variable or use --person-id flag."
        )
        sys.exit(1)

    # Determine time context
    if args.time:
        try:
            current_time = datetime.fromisoformat(args.time.replace("Z", "+00:00"))
        except ValueError:
            console.print(f"[red]Error: Invalid time format: {args.time}[/red]")
            sys.exit(1)
    else:
        current_time = datetime.now(UTC)

    # Get suggestions
    try:
        persona = asyncio.run(get_suggestions(person_id, current_time))

        if args.json:
            # Raw JSON output
            print(json.dumps(persona, indent=2))
        else:
            # Formatted output
            time_str = current_time.strftime("%I:%M %p")
            console.print(f"\n[bold]PersonaKit Suggestions for {time_str}[/bold]\n")
            display_suggestions(persona, verbose=args.verbose)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
