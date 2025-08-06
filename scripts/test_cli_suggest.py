#!/usr/bin/env python3
"""Test the CLI suggest command."""
import subprocess
import sys
import uuid


def main() -> None:
    """Test CLI suggest command."""
    # Use a test person ID
    person_id = str(uuid.uuid4())
    
    print(f"Testing CLI with person ID: {person_id}")
    print("\nRunning: persona-kit suggest --now --verbose")
    print("=" * 60)
    
    # Run the CLI command
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "suggest",
            "--person-id",
            person_id,
            "--now",
            "--verbose",
        ],
        capture_output=True,
        text=True,
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print("\n" + "=" * 60)
    print(f"Exit code: {result.returncode}")
    
    # Test JSON output
    print("\nTesting JSON output...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli.main",
            "suggest",
            "--person-id",
            person_id,
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0 and result.stdout:
        print("✓ JSON output received")
    else:
        print("✗ JSON output failed")
        print(result.stderr)


if __name__ == "__main__":
    main()