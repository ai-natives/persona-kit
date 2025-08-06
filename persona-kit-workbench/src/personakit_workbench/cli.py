"""CLI interface for PersonaKit Workbench."""
import asyncio
import os
import sys
from pathlib import Path
from uuid import UUID

import click
from rich.console import Console

from .api_client import PersonaKitClient
from .bootstrap import BootstrapWizard
from .bootstrap.mock_data import MockDataGenerator

console = Console()


def get_person_id() -> str | None:
    """Get person ID from environment or config."""
    # Check environment
    if person_id := os.getenv("PERSONAKIT_PERSON_ID"):
        return person_id
    
    # Check config file
    config_path = Path.home() / ".personakit" / "config.json"
    if config_path.exists():
        import json
        with open(config_path) as f:
            config = json.load(f)
            return config.get("person_id")
    
    return None


def save_person_id(person_id: str) -> None:
    """Save person ID to config file."""
    config_dir = Path.home() / ".personakit"
    config_dir.mkdir(exist_ok=True)
    
    config_path = config_dir / "config.json"
    config = {}
    
    if config_path.exists():
        import json
        with open(config_path) as f:
            config = json.load(f)
    
    config["person_id"] = person_id
    
    import json
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


@click.group()
def cli() -> None:
    """PersonaKit Workbench - Tools for bootstrapping, testing, and development."""
    pass


@cli.command()
@click.option(
    "--person-id",
    help="Use existing person ID instead of creating new one",
)
@click.option(
    "--api-url",
    default="http://localhost:8042",
    help="PersonaKit API URL",
    envvar="PERSONAKIT_API_URL",
)
def bootstrap(person_id: str | None, api_url: str) -> None:
    """Run the interactive bootstrap wizard."""
    async def run() -> None:
        async with PersonaKitClient(api_url) as client:
            # Check API health first
            try:
                await client.health_check()
            except Exception as e:
                console.print(
                    f"[red]Error: Cannot connect to PersonaKit API at {api_url}[/red]"
                )
                console.print(f"[dim]{e}[/dim]")
                sys.exit(1)
            
            wizard = BootstrapWizard(client)
            try:
                new_person_id = await wizard.run(person_id)
                
                # Save person ID for future use
                save_person_id(str(new_person_id))
                console.print(
                    f"\n[dim]Person ID saved to ~/.personakit/config.json[/dim]"
                )
                
            except KeyboardInterrupt:
                sys.exit(0)
    
    asyncio.run(run())


@cli.command()
@click.option(
    "--person-id",
    help="Person ID to generate data for",
)
@click.option(
    "--days",
    default=7,
    help="Number of days of data to generate",
)
@click.option(
    "--api-url",
    default="http://localhost:8042",
    help="PersonaKit API URL",
    envvar="PERSONAKIT_API_URL",
)
def generate_mock_data(person_id: str | None, days: int, api_url: str) -> None:
    """Generate mock observation data for testing."""
    # Get person ID
    if not person_id:
        person_id = get_person_id()
    
    if not person_id:
        console.print(
            "[red]Error: No person ID provided.[/red]\n"
            "Run 'persona-kit-workbench bootstrap' first or use --person-id"
        )
        sys.exit(1)
    
    async def run() -> None:
        async with PersonaKitClient(api_url) as client:
            # Check API health
            try:
                await client.health_check()
            except Exception as e:
                console.print(
                    f"[red]Error: Cannot connect to PersonaKit API at {api_url}[/red]"
                )
                console.print(f"[dim]{e}[/dim]")
                sys.exit(1)
            
            generator = MockDataGenerator(client)
            
            try:
                person_uuid = UUID(person_id)
            except ValueError:
                console.print(f"[red]Error: Invalid person ID format: {person_id}[/red]")
                sys.exit(1)
            
            await generator.generate(person_uuid, days=days)
    
    asyncio.run(run())


@cli.command()
def config() -> None:
    """Show current configuration."""
    console.print("[bold]PersonaKit Workbench Configuration[/bold]\n")
    
    # API URL
    api_url = os.getenv("PERSONAKIT_API_URL", "http://localhost:8042")
    console.print(f"API URL: [cyan]{api_url}[/cyan]")
    
    # Person ID
    if person_id := get_person_id():
        console.print(f"Person ID: [green]{person_id}[/green]")
        if os.getenv("PERSONAKIT_PERSON_ID"):
            console.print("  [dim](from environment variable)[/dim]")
        else:
            console.print("  [dim](from ~/.personakit/config.json)[/dim]")
    else:
        console.print("Person ID: [yellow]Not set[/yellow]")
        console.print("  [dim]Run 'persona-kit-workbench bootstrap' to set up[/dim]")
    
    # Config file location
    config_path = Path.home() / ".personakit" / "config.json"
    if config_path.exists():
        console.print(f"\nConfig file: [dim]{config_path}[/dim]")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()