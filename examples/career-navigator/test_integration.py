#!/usr/bin/env python3
"""
Test script to verify Career Navigator integrates with PersonaKit properly
"""

import asyncio
import httpx
import json
from datetime import datetime

PERSONAKIT_URL = "http://localhost:8042"
CAREER_NAV_URL = "http://localhost:8103"

async def test_integration():
    """Test that Career Navigator properly uses PersonaKit"""
    
    async with httpx.AsyncClient() as client:
        # 1. Check PersonaKit is running
        print("1. Checking PersonaKit health...")
        try:
            response = await client.get(f"{PERSONAKIT_URL}/health")
            assert response.status_code == 200
            print("   ✅ PersonaKit is healthy")
        except Exception as e:
            print(f"   ❌ PersonaKit not running: {e}")
            return
        
        # 2. Check Career Navigator is running
        print("\n2. Checking Career Navigator...")
        try:
            response = await client.get(f"{CAREER_NAV_URL}/")
            assert response.status_code == 200
            print("   ✅ Career Navigator is running")
        except Exception as e:
            print(f"   ❌ Career Navigator not running: {e}")
            return
        
        # 3. Submit a career assessment
        print("\n3. Submitting career assessment...")
        test_person_id = f"test-user-{int(datetime.now().timestamp())}"
        assessment = {
            "person_id": test_person_id,
            "current_role": "Software Developer",
            "target_role": "Tech Lead",
            "years_experience": 5,
            "skills": ["Python", "Team Collaboration", "Code Review"],
            "goals": ["Lead larger teams", "Make architectural decisions"],
            "concerns": ["Lack of leadership experience", "Work-life balance"]
        }
        
        response = await client.post(
            f"{CAREER_NAV_URL}/api/career/assess",
            json=assessment
        )
        assert response.status_code == 200
        career_path = response.json()
        print(f"   ✅ Career path generated with {len(career_path['milestones'])} milestones")
        print(f"   Timeline: {career_path['timeline_months']} months")
        
        # 4. Verify observation was recorded in PersonaKit
        print("\n4. Checking PersonaKit recorded the observation...")
        response = await client.get(
            f"{PERSONAKIT_URL}/observations",
            params={"person_id": test_person_id}
        )
        observations = response.json()
        assert len(observations) > 0
        assert observations[0]["observation_type"] == "career_assessment"
        print(f"   ✅ Found {len(observations)} observations")
        
        # 5. Check if persona was created
        print("\n5. Checking for active personas...")
        response = await client.get(
            f"{PERSONAKIT_URL}/personas/active",
            params={"person_id": test_person_id}
        )
        personas = response.json()
        if personas:
            print(f"   ✅ Found {len(personas)} active personas")
            persona = personas[0]
            print(f"   Overlay: {json.dumps(persona.get('overlay', {}), indent=2)}")
        else:
            print("   ⚠️  No personas found (may need mapper configuration)")
        
        # 6. Get daily tasks
        print("\n6. Fetching personalized daily tasks...")
        response = await client.get(
            f"{CAREER_NAV_URL}/api/career/tasks/{test_person_id}"
        )
        tasks_data = response.json()
        tasks = tasks_data.get("tasks", [])
        adaptations = tasks_data.get("adaptation_reasons", [])
        print(f"   ✅ Got {len(tasks)} daily tasks")
        for reason in adaptations:
            print(f"   - {reason}")
        
        print("\n✅ Integration test complete!")
        print(f"   Person ID: {test_person_id}")
        print("   Career Navigator is properly integrated with PersonaKit")

if __name__ == "__main__":
    asyncio.run(test_integration())