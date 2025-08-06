#!/usr/bin/env python3
"""Test the complete bootstrap flow."""
import asyncio
import sys
import uuid
from datetime import UTC, datetime, time

sys.path.insert(0, 'persona-kit-workbench/src')

from personakit_workbench import PersonaKitClient
from personakit_workbench.bootstrap import BootstrapWizard
from personakit_workbench.bootstrap.mock_data import MockDataGenerator


async def test_bootstrap_flow() -> None:
    """Test the complete bootstrap flow programmatically."""
    print("Testing PersonaKit Bootstrap Flow")
    print("=" * 40)
    
    # Create a test person ID
    person_id = uuid.uuid4()
    print(f"Test Person ID: {person_id}")
    
    async with PersonaKitClient() as client:
        # Step 1: Check API health
        print("\n1. Checking API connection...")
        try:
            health = await client.health_check()
            print(f"   ✓ API is healthy: {health['status']}")
        except Exception as e:
            print(f"   ✗ API connection failed: {e}")
            print("\nMake sure PersonaKit API is running on http://localhost:8042")
            return
        
        # Step 2: Simulate wizard responses
        print("\n2. Creating wizard observations...")
        
        # Create wizard response observation
        await client.create_observation(
            person_id=person_id,
            observation_type="user_input",
            content={
                "type": "wizard_response",
                "responses": {
                    "timezone": "America/New_York",
                    "work_start_time": time(9, 0).isoformat(),
                    "most_productive": "morning",
                    "focus_duration": "1hr",
                    "flow_disruptor": "meetings",
                },
            },
            meta={"source": "test_script"},
        )
        print("   ✓ Wizard responses created")
        
        # Create initial work session
        now = datetime.now(UTC)
        await client.create_observation(
            person_id=person_id,
            observation_type="work_session",
            content={
                "start": now.replace(hour=9, minute=0).isoformat(),
                "duration_minutes": 90,
                "productivity_score": 5,
                "interruptions": 0,
            },
            meta={"source": "test_script"},
        )
        print("   ✓ Initial work session created")
        
        # Step 3: Generate mock data
        print("\n3. Generating 3 days of mock data...")
        generator = MockDataGenerator(client)
        stats = await generator.generate(person_id, days=3, verbose=False)
        print(f"   ✓ Generated {stats['total']} observations")
        print(f"     - Work sessions: {stats['work_sessions']}")
        print(f"     - Calendar events: {stats['calendar_events']}")
        print(f"     - User inputs: {stats['user_inputs']}")
        
        # Step 4: Wait for processing
        print("\n4. Waiting for observation processing...")
        await asyncio.sleep(5)
        print("   ✓ Processing complete")
        
        # Step 5: Generate persona
        print("\n5. Generating persona...")
        try:
            persona = await client.generate_persona(
                person_id=person_id,
                mapper_id="daily_work_optimizer",
            )
            print(f"   ✓ Persona generated: {persona['id']}")
            
            # Show some suggestions
            if suggestions := persona.get("overlay", {}).get("suggestions", []):
                print("\n   Suggestions:")
                for i, suggestion in enumerate(suggestions[:2], 1):
                    print(f"   {i}. {suggestion.get('title', 'Suggestion')}")
                    print(f"      {suggestion.get('description', '')}")
        except Exception as e:
            print(f"   ✗ Persona generation failed: {e}")
            return
        
        # Step 6: Test feedback
        print("\n6. Testing feedback...")
        try:
            feedback = await client.create_feedback(
                persona_id=persona["id"],
                helpful=True,
                context={"test": True},
            )
            print(f"   ✓ Feedback created: {feedback['id']}")
        except Exception as e:
            print(f"   ✗ Feedback failed: {e}")
        
        print("\n" + "=" * 40)
        print("✓ Bootstrap flow test complete!")
        print(f"\nYou can now use: persona-kit suggest --person-id {person_id}")


if __name__ == "__main__":
    asyncio.run(test_bootstrap_flow())