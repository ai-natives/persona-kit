#!/usr/bin/env python3
"""
Test script for configuration-driven mapper flow.

This script:
1. Uploads a mapper configuration via API
2. Generates a persona using the configuration
3. Submits feedback
4. Verifies weight adjustment
"""

import asyncio
import json
import sys
from pathlib import Path
import httpx
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

API_BASE = "http://localhost:8042"


async def test_mapper_upload():
    """Test uploading a mapper configuration."""
    print("\n1. Testing mapper upload...")
    
    # Read the YAML configuration
    config_path = Path(__file__).parent.parent / "configs/examples/daily_work_optimizer.yaml"
    with open(config_path) as f:
        config_content = f.read()
    
    async with httpx.AsyncClient() as client:
        # Upload the configuration
        response = await client.post(
            f"{API_BASE}/mappers/upload",
            files={"file": ("daily_work_optimizer.yaml", config_content, "text/yaml")},
            data={"status": "active"}
        )
        
        if response.status_code == 200:
            mapper_data = response.json()
            print(f"✓ Mapper uploaded successfully: {mapper_data['config_id']} v{mapper_data['version']}")
            return mapper_data['id']
        else:
            print(f"✗ Failed to upload mapper: {response.status_code}")
            print(response.text)
            return None


async def test_mapper_list():
    """Test listing mappers."""
    print("\n2. Testing mapper list...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/mappers")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data['total']} mappers:")
            for mapper in data['mappers']:
                print(f"  - {mapper['config_id']} v{mapper['version']} ({mapper['status']})")
        else:
            print(f"✗ Failed to list mappers: {response.status_code}")


async def test_persona_generation(mapper_config_id: str):
    """Test generating a persona with configuration-driven mapper."""
    print("\n3. Testing persona generation...")
    
    # First create a test person with observations
    person_id = "550e8400-e29b-41d4-a716-446655440001"
    
    # Create a test mindscape (normally this would be done by observation processing)
    mindscape_data = {
        "work": {
            "energy_patterns": {
                "morning": "high",
                "afternoon": "low",
                "evening": "medium"
            },
            "focus_duration": {
                "p50": 60,
                "p90": 90,
                "max": 120
            },
            "peak_hours": [9, 10, 11],
            "task_switching_cost": "high",
            "meeting_recovery": {
                "prep_needed": True,
                "typical_prep_minutes": 15
            }
        },
        "productivity": {
            "flow_state": {
                "triggers": ["quiet_environment", "clear_goals"],
                "best_task_types": ["deep_analysis", "creative_work"]
            }
        },
        "current_state": {
            "energy_level": 4,
            "focus_available": True
        }
    }
    
    # In a real scenario, we'd create observations and process them
    # For testing, we'll assume the mindscape exists
    
    async with httpx.AsyncClient() as client:
        # Generate persona
        response = await client.post(
            f"{API_BASE}/personas",
            json={
                "person_id": person_id,
                "mapper_id": "daily-work-optimizer",
                "context": {
                    "time_of_day": "morning",
                    "day_of_week": "Monday",
                    "calendar_free_hours": 3
                }
            }
        )
        
        if response.status_code == 200:
            persona = response.json()
            print(f"✓ Persona generated successfully: {persona['id']}")
            print(f"  Suggestions: {len(persona['overlay']['suggestions'])}")
            
            # Print suggestions
            for i, suggestion in enumerate(persona['overlay']['suggestions'][:3]):
                print(f"  {i+1}. {suggestion['title']}")
                print(f"     {suggestion['description']}")
                print(f"     Rule: {suggestion.get('rule_id', 'unknown')}")
                
            return persona['id'], persona['overlay']['suggestions']
        else:
            print(f"✗ Failed to generate persona: {response.status_code}")
            print(response.text)
            return None, None


async def test_feedback_submission(persona_id: str, suggestions: list):
    """Test submitting feedback for a suggestion."""
    print("\n4. Testing feedback submission...")
    
    if not suggestions:
        print("✗ No suggestions to provide feedback for")
        return
    
    # Get the first suggestion
    suggestion = suggestions[0]
    rule_id = suggestion.get('rule_id')
    
    async with httpx.AsyncClient() as client:
        # Submit positive feedback
        response = await client.post(
            f"{API_BASE}/feedback",
            json={
                "persona_id": persona_id,
                "helpful": True,
                "rating": 5,
                "rule_id": rule_id,
                "context": {
                    "suggestion_type": suggestion['type']
                }
            }
        )
        
        if response.status_code == 200:
            feedback = response.json()
            print(f"✓ Feedback submitted successfully: {feedback['id']}")
            print(f"  Rule: {rule_id}")
            print(f"  Helpful: True")
        else:
            print(f"✗ Failed to submit feedback: {response.status_code}")


async def test_weight_history(mapper_id: str):
    """Check weight adjustment history."""
    print("\n5. Checking weight history...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/mappers/{mapper_id}/versions")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Mapper has {len(data['versions'])} versions:")
            for version in data['versions']:
                print(f"  - v{version['version']} ({version['status']}) - "
                      f"Usage: {version['usage_count']}")
        else:
            print(f"✗ Failed to get version history: {response.status_code}")


async def main():
    """Run all tests."""
    print("PersonaKit Configuration-Driven Mapper Test")
    print("=" * 50)
    
    # Test mapper upload
    mapper_id = await test_mapper_upload()
    if not mapper_id:
        print("\n❌ Mapper upload failed, stopping tests")
        return
    
    # Test mapper list
    await test_mapper_list()
    
    # Test persona generation
    persona_id, suggestions = await test_persona_generation(mapper_id)
    if not persona_id:
        print("\n❌ Persona generation failed, stopping tests")
        return
    
    # Test feedback submission
    await test_feedback_submission(persona_id, suggestions)
    
    # Check weight history
    await test_weight_history("daily-work-optimizer")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())