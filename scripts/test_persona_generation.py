#!/usr/bin/env python3
"""Test script for persona generation."""
import asyncio
import json
import uuid
from datetime import UTC, datetime

import httpx


async def main() -> None:
    """Test persona generation end-to-end."""
    base_url = "http://localhost:8042"
    person_id = str(uuid.uuid4())
    
    async with httpx.AsyncClient() as client:
        print(f"Testing persona generation for person: {person_id}")
        
        # Step 1: Create initial observations
        print("\n1. Creating test observations...")
        
        observations = [
            {
                "person_id": person_id,
                "type": "work_session",
                "content": {
                    "start": "2024-01-15T09:00:00Z",
                    "duration_minutes": 90,
                    "productivity_score": 5,
                    "interruptions": 0,
                },
                "meta": {"source": "test_script"},
            },
            {
                "person_id": person_id,
                "type": "user_input",
                "content": {
                    "type": "wizard_response",
                    "responses": {
                        "most_productive": "morning",
                        "focus_duration": "2hr+",
                        "flow_disruptor": "meetings",
                    },
                },
                "meta": {"source": "test_script"},
            },
        ]
        
        for obs in observations:
            response = await client.post(f"{base_url}/observations", json=obs)
            if response.status_code == 200:
                print(f"  ✓ Created {obs['type']} observation")
            else:
                print(f"  ✗ Failed to create observation: {response.text}")
                return
        
        # Step 2: Wait for processing
        print("\n2. Waiting for observation processing...")
        await asyncio.sleep(3)
        
        # Step 3: Generate persona
        print("\n3. Generating persona...")
        
        persona_request = {
            "person_id": person_id,
            "mapper_id": "daily_work_optimizer",
            "context": {
                "current_time": datetime.now(UTC).replace(hour=10).isoformat(),
                "upcoming_meetings": [
                    {
                        "start": datetime.now(UTC).replace(hour=11).isoformat(),
                        "title": "Team Standup",
                    }
                ],
            },
        }
        
        response = await client.post(f"{base_url}/personas", json=persona_request)
        
        if response.status_code == 200:
            persona = response.json()
            print("  ✓ Persona generated successfully!")
            print(f"\nPersona ID: {persona['id']}")
            print(f"Expires at: {persona['expires_at']}")
            
            print("\nCore Configuration:")
            print(json.dumps(persona["core"], indent=2))
            
            print("\nCurrent State & Suggestions:")
            print(json.dumps(persona["overlay"], indent=2))
        else:
            print(f"  ✗ Failed to generate persona: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())