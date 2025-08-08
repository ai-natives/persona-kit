#!/usr/bin/env python3
"""PersonaKit CLI main entry point."""
import argparse
import sys

from .suggest import main as suggest_main


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="persona-kit",
        description="PersonaKit - Adaptive personas for enhanced productivity"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Suggest command
    suggest_parser = subparsers.add_parser(
        "suggest",
        help="Get personalized work suggestions"
    )
    suggest_parser.add_argument(
        "--person-id",
        help="Person ID (defaults to config or PERSONAKIT_PERSON_ID env var)"
    )
    suggest_parser.add_argument(
        "--now",
        action="store_true",
        help="Get suggestions for current time (default)"
    )
    suggest_parser.add_argument(
        "--time",
        help="Get suggestions for specific time (ISO format)"
    )
    suggest_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show additional details"
    )
    suggest_parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )


    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate command
    if args.command == "suggest":
        # Pass args to suggest command
        sys.argv = ["persona-kit-suggest"]
        if args.person_id:
            sys.argv.extend(["--person-id", args.person_id])
        if args.now:
            sys.argv.append("--now")
        if args.time:
            sys.argv.extend(["--time", args.time])
        if args.verbose:
            sys.argv.append("--verbose")
        if args.json:
            sys.argv.append("--json")
        suggest_main()


if __name__ == "__main__":
    main()
