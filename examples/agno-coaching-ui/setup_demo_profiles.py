#!/usr/bin/env python3
"""
Set up demo profiles in PersonaKit for the Agno Coaching UI.

This creates real PersonaKit profiles instead of relying on hardcoded data.
"""

import asyncio
import httpx
import json
from datetime import datetime
import uuid

PERSONAKIT_URL = "http://localhost:8042"

# Demo profiles to create
DEMO_PROFILES = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Sato-san",
        "role": "Assistant Project Manager",
        "company": "DX Initiative Corp",
        "industry": "Technology Services",
        "traits": {
            "tech.comfort_level": {"value": "low", "confidence": 0.9},
            "learning.style": {"value": "visual_step_by_step", "confidence": 0.8},
            "communication.preference": {"value": "simple_analogies", "confidence": 0.9},
            "work.focus": {"value": "process_improvement", "confidence": 0.7},
            "stress.indicators": {"value": "technical_jargon", "confidence": 0.8}
        },
        "initial_observations": [
            "I get overwhelmed when people use too much technical jargon",
            "I learn best when concepts are explained with everyday analogies",
            "Visual diagrams and step-by-step instructions really help me understand",
            "I'm working on a DX project but struggle with the testing concepts",
            "I prefer when mentors are patient and encouraging"
        ]
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440002", 
        "name": "Alex Chen",
        "role": "Senior Backend Developer",
        "company": "TechCorp Solutions",
        "industry": "Software Development",
        "traits": {
            "tech.comfort_level": {"value": "high", "confidence": 0.95},
            "learning.style": {"value": "theory_first", "confidence": 0.8},
            "communication.preference": {"value": "technical_depth", "confidence": 0.9},
            "work.focus": {"value": "system_architecture", "confidence": 0.85},
            "interests": {"value": "distributed_systems", "confidence": 0.9}
        },
        "initial_observations": [
            "I enjoy diving deep into technical concepts and understanding the theory",
            "I appreciate discussions about trade-offs and architectural decisions",
            "I'm comfortable with complex technical terminology",
            "Currently exploring microservices patterns and event-driven architectures",
            "I like to understand the 'why' behind best practices"
        ]
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "Jordan Lee", 
        "role": "Frontend Developer",
        "company": "StartupXYZ",
        "industry": "E-commerce",
        "traits": {
            "tech.comfort_level": {"value": "medium", "confidence": 0.8},
            "learning.style": {"value": "hands_on", "confidence": 0.85},
            "communication.preference": {"value": "practical_examples", "confidence": 0.8},
            "work.focus": {"value": "full_stack_transition", "confidence": 0.7},
            "background": {"value": "frontend_specialist", "confidence": 0.9}
        },
        "initial_observations": [
            "I learn best by doing - show me code examples and let me try",
            "I'm transitioning from frontend to full-stack development",
            "I understand React/Vue well but backend concepts are newer to me",
            "I prefer practical applications over abstract theory",
            "Real-world examples help me connect frontend knowledge to backend concepts"
        ]
    }
]


async def create_person(person_data):
    """Create a person in PersonaKit."""
    async with httpx.AsyncClient() as client:
        try:
            # Create the persona
            response = await client.post(
                f"{PERSONAKIT_URL}/personas/",
                json={
                    "name": person_data["name"],
                    "description": f"{person_data['role']} at {person_data['company']}",
                    "role": person_data["role"],
                    "background": f"Works in {person_data['industry']} industry",
                    "communication_style": person_data["traits"].get("communication.preference", {}).get("value", "balanced"),
                    "expertise_areas": [],
                    "metadata": {
                        "person_id": person_data["id"],
                        "company": person_data["company"],
                        "industry": person_data["industry"],
                        "original_traits": person_data["traits"]
                    }
                }
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created persona: {person_data['name']}")
                persona_id = response.json().get("id")
                
                # Add initial observations as narratives
                for observation in person_data["initial_observations"]:
                    await add_narrative(persona_id, person_data["name"], observation)
                    
                return True
            elif response.status_code == 409:
                print(f"ℹ️  Persona already exists: {person_data['name']}")
                return True
            else:
                print(f"❌ Failed to create {person_data['name']}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating {person_data['name']}: {e}")
            return False


async def add_trait(person_id, person_name, trait_path, trait_data):
    """Add a trait to a person."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{PERSONAKIT_URL}/api/v1/people/{person_id}/traits/{trait_path}",
                json=trait_data,
                headers={"Authorization": "Bearer demo-token"}
            )
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Added trait {trait_path} for {person_name}")
            else:
                print(f"  ❌ Failed to add trait {trait_path}: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error adding trait {trait_path}: {e}")


async def add_narrative(persona_id, person_name, observation):
    """Add an observation narrative."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{PERSONAKIT_URL}/api/narratives/self-observation",
                json={
                    "person_id": persona_id,
                    "content": observation,
                    "tags": ["initial", "profile", "learning_preference"],
                    "context": {
                        "source": "demo_setup",
                        "person_name": person_name
                    }
                }
            )
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Added observation for {person_name}")
            else:
                print(f"  ❌ Failed to add observation: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error adding observation: {e}")


async def main():
    """Set up all demo profiles."""
    print("🚀 Setting up PersonaKit demo profiles...")
    print("=" * 60)
    
    # Check if PersonaKit is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PERSONAKIT_URL}/health/")
            if response.status_code != 200:
                print("❌ PersonaKit is not running on http://localhost:8042")
                print("   Please start it with: uv run python src/main.py")
                return
    except:
        print("❌ Cannot connect to PersonaKit on http://localhost:8042")
        print("   Please start it with: uv run python src/main.py")
        return
    
    print("✅ PersonaKit is running\n")
    
    # Create each profile
    for profile in DEMO_PROFILES:
        print(f"\n📝 Setting up {profile['name']}...")
        await create_person(profile)
    
    print("\n" + "=" * 60)
    print("✅ Demo profiles setup complete!")
    print("\nYou can now use the Agno Coaching UI with real PersonaKit data.")
    print("The profiles will show 'Profile Loaded: ✅' in the UI.")


if __name__ == "__main__":
    asyncio.run(main())