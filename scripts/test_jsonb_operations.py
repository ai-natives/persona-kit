#!/usr/bin/env python3
"""Test JSONB operations with real PostgreSQL data."""
import asyncio
import uuid
from datetime import UTC, datetime

from src.database import get_db
from src.models.observation import ObservationType
from src.repositories import MindscapeRepository, ObservationRepository


async def test_jsonb_operations():
    """Test various JSONB operations."""
    print("=== Testing JSONB Operations ===\n")
    
    # Get database session
    async for session in get_db():
        person_id = uuid.uuid4()
        
        # Test 1: Create observations with nested JSON
        print("1. Creating observations with nested JSON content...")
        obs_repo = ObservationRepository(session)
        
        observations = [
            {
                "person_id": person_id,
                "type": ObservationType.WORK_SESSION,
                "content": {
                    "duration_minutes": 45,
                    "activities": ["coding", "debugging"],
                    "project": {
                        "name": "PersonaKit",
                        "language": "Python",
                        "frameworks": ["FastAPI", "SQLAlchemy"],
                    },
                    "productivity_score": 8.5,
                },
                "meta": {"source": "IDE", "version": "1.0"},
            },
            {
                "person_id": person_id,
                "type": ObservationType.USER_INPUT,
                "content": {
                    "feedback": "I work best in the morning",
                    "preferences": {
                        "focus_time": "09:00-11:00",
                        "break_duration": 15,
                    },
                },
                "meta": {"source": "user_survey"},
            },
        ]
        
        created_obs = []
        for obs_data in observations:
            obs = await obs_repo.create(**obs_data)
            created_obs.append(obs)
            print(f"  ✅ Created observation {obs.id}")
        
        # Test 2: Create and update mindscape with complex traits
        print("\n2. Testing mindscape JSONB operations...")
        mindscape_repo = MindscapeRepository(session)
        
        initial_traits = {
            "work_patterns": {
                "peak_hours": ["09:00-11:00", "14:00-16:00"],
                "preferred_break_duration": 15,
                "focus_music": True,
            },
            "project_preferences": {
                "languages": ["Python", "TypeScript"],
                "domains": ["backend", "data"],
            },
            "productivity_factors": {
                "positive": ["quiet_environment", "morning_time", "clear_goals"],
                "negative": ["interruptions", "unclear_requirements"],
            },
        }
        
        mindscape = await mindscape_repo.upsert(person_id, initial_traits)
        print(f"  ✅ Created mindscape with {len(initial_traits)} trait categories")
        
        # Update specific traits
        trait_updates = {
            "work_patterns": {
                "peak_hours": ["09:00-11:00", "14:00-16:00", "20:00-22:00"],
                "preferred_break_duration": 20,
                "focus_music": True,
                "new_field": "testing_update",
            },
            "new_category": {"test": "value"},
        }
        
        updated = await mindscape_repo.update_traits(person_id, trait_updates)
        print(f"  ✅ Updated mindscape traits, version: {updated.version}")
        
        # Test 3: Query observations by content
        print("\n3. Testing observation queries...")
        
        # Get all observations for person
        all_obs = await obs_repo.get_by_person(person_id)
        print(f"  ✅ Found {len(all_obs)} observations for person")
        
        # Get recent observations
        recent = await obs_repo.get_recent(person_id, days=1)
        print(f"  ✅ Found {len(recent)} recent observations")
        
        # Test 4: Verify JSON structure preservation
        print("\n4. Verifying JSON structure preservation...")
        
        for i, obs in enumerate(created_obs):
            original = observations[i]["content"]
            stored = obs.content
            
            # Check nested values
            if "project" in original:
                assert stored["project"]["name"] == original["project"]["name"]
                assert stored["project"]["frameworks"] == original["project"]["frameworks"]
                print(f"  ✅ Observation {i+1}: Nested JSON preserved correctly")
            
            if "preferences" in original:
                assert stored["preferences"]["focus_time"] == original["preferences"]["focus_time"]
                print(f"  ✅ Observation {i+1}: User preferences preserved")
        
        # Test 5: Verify mindscape trait merging
        print("\n5. Verifying mindscape trait merging...")
        
        final_mindscape = await mindscape_repo.get_by_person(person_id)
        traits = final_mindscape.traits
        
        # Check that old values are preserved
        assert traits["project_preferences"]["languages"] == ["Python", "TypeScript"]
        print("  ✅ Original traits preserved")
        
        # Check that updates were applied
        assert traits["work_patterns"]["preferred_break_duration"] == 20
        assert traits["work_patterns"]["new_field"] == "testing_update"
        print("  ✅ Trait updates applied correctly")
        
        # Check new category was added
        assert "new_category" in traits
        print("  ✅ New trait category added")
        
        print("\n✅ All JSONB operations completed successfully!")
        
        # Cleanup
        await session.rollback()  # Don't save test data


if __name__ == "__main__":
    asyncio.run(test_jsonb_operations())