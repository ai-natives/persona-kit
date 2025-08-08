#!/usr/bin/env python3
"""
Set up PersonaKit with real data for the Agno Coaching demo.

This creates a user and personas that match what the demo expects.
"""

import asyncio
import httpx
import json
import sys

PERSONAKIT_URL = "http://localhost:8042"

# The personas we want to create
PERSONAS_DATA = [
    {
        "name": "Sato-san",
        "description": "Tech-averse assistant PM learning DX testing",
        "role": "Assistant Project Manager",
        "background": "Works in Technology Services industry at DX Initiative Corp. Has low technical comfort level and prefers visual, step-by-step explanations with simple analogies.",
        "communication_style": "simple_analogies",
        "expertise_areas": ["project_management", "process_improvement"],
        "metadata": {
            "company": "DX Initiative Corp",
            "industry": "Technology Services",
            "original_traits": {
                "tech.comfort_level": {"value": "low", "confidence": 0.9},
                "learning.style": {"value": "visual_step_by_step", "confidence": 0.8},
                "communication.preference": {"value": "simple_analogies", "confidence": 0.9}
            }
        }
    },
    {
        "name": "Alex Chen",
        "description": "Senior backend developer learning system design",
        "role": "Senior Backend Developer",
        "background": "Works in Software Development at TechCorp Solutions. Has high technical expertise and prefers theory-first, in-depth technical discussions.",
        "communication_style": "technical_depth",
        "expertise_areas": ["backend_development", "system_architecture", "distributed_systems"],
        "metadata": {
            "company": "TechCorp Solutions",
            "industry": "Software Development",
            "original_traits": {
                "tech.comfort_level": {"value": "high", "confidence": 0.95},
                "learning.style": {"value": "theory_first", "confidence": 0.8},
                "communication.preference": {"value": "technical_depth", "confidence": 0.9}
            }
        }
    },
    {
        "name": "Jordan Lee",
        "description": "Frontend developer transitioning to full-stack",
        "role": "Frontend Developer",
        "background": "Works in E-commerce at StartupXYZ. Has medium technical level, transitioning from frontend to full-stack. Prefers hands-on learning with practical examples.",
        "communication_style": "practical_examples",
        "expertise_areas": ["frontend_development", "react", "ui_ux"],
        "metadata": {
            "company": "StartupXYZ",
            "industry": "E-commerce",
            "original_traits": {
                "tech.comfort_level": {"value": "medium", "confidence": 0.8},
                "learning.style": {"value": "hands_on", "confidence": 0.85},
                "communication.preference": {"value": "practical_examples", "confidence": 0.8}
            }
        }
    }
]


async def create_user():
    """Create a demo user and get API key."""
    async with httpx.AsyncClient() as client:
        # First check if we can access without auth
        try:
            response = await client.get(f"{PERSONAKIT_URL}/health/")
            if response.status_code != 200:
                print("❌ PersonaKit is not running!")
                return None
        except:
            print("❌ Cannot connect to PersonaKit on http://localhost:8042")
            return None
        
        # Try to create a user
        print("📝 Creating demo user...")
        try:
            response = await client.post(
                f"{PERSONAKIT_URL}/users/",
                json={
                    "email": "agno-demo@personakit.ai",
                    "full_name": "Agno Demo User"
                }
            )
            
            if response.status_code == 201:
                user_data = response.json()
                print(f"✅ Created user: {user_data['email']}")
                print(f"🔑 API Key: {user_data['api_key']}")
                return user_data['api_key']
            elif response.status_code == 500:
                print("❌ User creation failed - PersonaKit may need database setup")
                print("   Run: cd ../../../ && alembic upgrade head")
                return None
            else:
                print(f"❌ Failed to create user: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None


async def create_personas(api_key: str):
    """Create personas using the API key."""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        created_count = 0
        for persona_data in PERSONAS_DATA:
            print(f"\n📝 Creating persona: {persona_data['name']}...")
            
            try:
                response = await client.post(
                    f"{PERSONAKIT_URL}/personas/",
                    json=persona_data,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    print(f"✅ Created persona: {persona_data['name']} (ID: {result['id']})")
                    created_count += 1
                else:
                    print(f"❌ Failed to create {persona_data['name']}: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Error creating {persona_data['name']}: {e}")
        
        return created_count


async def main():
    """Main setup function."""
    print("🚀 Setting up PersonaKit for Agno Coaching Demo")
    print("=" * 60)
    
    # Step 1: Create user and get API key
    api_key = await create_user()
    
    if not api_key:
        print("\n⚠️  Could not create user. Please ensure:")
        print("1. PersonaKit is running (uv run python src/main.py)")
        print("2. Database is migrated (alembic upgrade head)")
        print("3. PostgreSQL is running on port 5436")
        return
    
    # Step 2: Create personas
    print("\n🎭 Creating personas...")
    created = await create_personas(api_key)
    
    print("\n" + "=" * 60)
    if created > 0:
        print(f"✅ Successfully created {created} personas!")
        print(f"\n🔑 Save this API key for the backend: {api_key}")
        print("\nUpdate backend/.env:")
        print(f"PERSONAKIT_API_KEY={api_key}")
        print("\nThe Agno Coaching UI will now show real PersonaKit profiles!")
    else:
        print("❌ No personas were created.")


if __name__ == "__main__":
    asyncio.run(main())