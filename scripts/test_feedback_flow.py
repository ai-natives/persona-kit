#!/usr/bin/env python3
"""Test the complete feedback flow end-to-end."""
import asyncio
import uuid
from datetime import UTC, datetime

import httpx

# Configuration
API_URL = "http://localhost:8042"
PERSON_ID = uuid.uuid4()


async def main() -> None:
    """Test feedback flow."""
    print("Testing PersonaKit Feedback Flow")
    print("=" * 40)
    
    async with httpx.AsyncClient(base_url=API_URL, timeout=10.0) as client:
        # Step 1: Create initial observations
        print("\n1. Creating initial observations...")
        
        # Create work session observations
        for i in range(5):
            response = await client.post(
                "/observations",
                json={
                    "person_id": str(PERSON_ID),
                    "observation_type": "work_session",
                    "content": {
                        "duration_minutes": 90,
                        "productivity_score": 4,
                        "interruptions": 0,
                        "start": datetime.now(UTC).replace(hour=9 + i).isoformat(),
                    },
                    "meta": {"source": "test_feedback_flow"},
                },
            )
            response.raise_for_status()
        
        print("   ✓ Created 5 work session observations")
        
        # Wait for processing
        print("\n2. Waiting for observation processing...")
        await asyncio.sleep(3)
        
        # Step 2: Generate persona
        print("\n3. Generating persona...")
        response = await client.post(
            "/personas",
            json={
                "person_id": str(PERSON_ID),
                "mapper_id": "daily_work_optimizer",
            },
        )
        response.raise_for_status()
        persona = response.json()
        persona_id = persona["id"]
        
        print(f"   ✓ Generated persona: {persona_id}")
        
        # Show suggestions
        suggestions = persona.get("overlay", {}).get("suggestions", [])
        if suggestions:
            print("\n   Suggestions:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"   {i}. {suggestion.get('title')}")
                print(f"      Type: {suggestion.get('type')}")
                print(f"      ID: {suggestion.get('id')}")
        
        # Step 3: Submit positive feedback
        print("\n4. Submitting positive feedback...")
        if suggestions:
            feedback_response = await client.post(
                "/feedback",
                json={
                    "persona_id": persona_id,
                    "helpful": True,
                    "rating": 5,
                    "context": {
                        "suggestion_id": suggestions[0]["id"],
                    },
                },
            )
            feedback_response.raise_for_status()
            print(f"   ✓ Submitted positive feedback for: {suggestions[0]['title']}")
        
        # Step 4: Submit multiple negative feedback
        print("\n5. Submitting negative feedback (testing threshold)...")
        
        # Create new persona to test negative feedback
        response = await client.post(
            "/personas",
            json={
                "person_id": str(PERSON_ID),
                "mapper_id": "daily_work_optimizer",
            },
        )
        response.raise_for_status()
        persona2 = response.json()
        
        # Submit 5 negative feedback to trigger threshold
        for i in range(5):
            feedback_response = await client.post(
                "/feedback",
                json={
                    "persona_id": persona2["id"],
                    "helpful": False,
                    "rating": 1,
                    "context": {
                        "suggestion_id": suggestions[0]["id"] if suggestions else "test",
                    },
                },
            )
            feedback_response.raise_for_status()
        
        print("   ✓ Submitted 5 negative feedback (threshold reached)")
        
        # Step 5: Generate new persona to see changes
        print("\n6. Generating new persona to verify trait adjustments...")
        await asyncio.sleep(1)  # Allow processing
        
        response = await client.post(
            "/personas",
            json={
                "person_id": str(PERSON_ID),
                "mapper_id": "daily_work_optimizer",
            },
        )
        response.raise_for_status()
        new_persona = response.json()
        
        print("   ✓ Generated new persona after feedback")
        
        # Compare suggestions
        new_suggestions = new_persona.get("overlay", {}).get("suggestions", [])
        if new_suggestions:
            print("\n   Updated suggestions:")
            for i, suggestion in enumerate(new_suggestions[:3], 1):
                print(f"   {i}. {suggestion.get('title')}")
        
        # Step 6: Get analytics
        print("\n7. Fetching feedback analytics...")
        analytics_response = await client.get(
            "/feedback/analytics",
            params={"person_id": str(PERSON_ID), "days": 7},
        )
        analytics_response.raise_for_status()
        analytics = analytics_response.json()
        
        print(f"   Total feedback: {analytics.get('total_feedback', 0)}")
        print(f"   Positive: {analytics.get('positive', 0)}")
        print(f"   Negative: {analytics.get('negative', 0)}")
        print(f"   Positive rate: {analytics.get('positive_rate', 0)}%")
        
        # Show feedback by type
        if by_type := analytics.get("by_suggestion_type"):
            print("\n   Feedback by suggestion type:")
            for stype, stats in by_type.items():
                print(f"   - {stype}: {stats}")
        
        print("\n" + "=" * 40)
        print("✓ Feedback flow test complete!")
        print(f"\nPerson ID: {PERSON_ID}")
        print("\nNote: Trait weights are adjusted based on feedback patterns.")
        print("Negative feedback threshold (5) triggers weight reduction.")
        print("Positive feedback immediately increases weights.")


if __name__ == "__main__":
    asyncio.run(main())