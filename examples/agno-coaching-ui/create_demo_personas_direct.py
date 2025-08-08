#!/usr/bin/env python3
"""
Create demo personas directly in the database for the Agno Coaching UI.
"""

import asyncio
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.database import async_session_maker
from src.models.persona import Persona
from src.models.narrative import Narrative
from sqlalchemy import select
import uuid
from datetime import datetime

# Demo personas to create
DEMO_PERSONAS = [
    {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
        "name": "Sato-san",
        "description": "Tech-averse assistant PM learning DX testing",
        "role": "Assistant Project Manager",
        "background": "Works in Technology Services industry at DX Initiative Corp. Has low technical comfort level and prefers visual, step-by-step explanations with simple analogies.",
        "communication_style": "simple_analogies",
        "expertise_areas": ["project_management", "process_improvement"],
        "metadata": {
            "company": "DX Initiative Corp",
            "industry": "Technology Services",
            "traits": {
                "tech_comfort_level": "low",
                "learning_style": "visual_step_by_step",
                "preference": "simple_analogies"
            }
        }
    },
    {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440002"),
        "name": "Alex Chen",
        "description": "Senior backend developer learning system design",
        "role": "Senior Backend Developer",
        "background": "Works in Software Development at TechCorp Solutions. Has high technical expertise and prefers theory-first, in-depth technical discussions.",
        "communication_style": "technical_depth",
        "expertise_areas": ["backend_development", "system_architecture", "distributed_systems"],
        "metadata": {
            "company": "TechCorp Solutions",
            "industry": "Software Development",
            "traits": {
                "tech_comfort_level": "high",
                "learning_style": "theory_first",
                "preference": "technical_depth"
            }
        }
    },
    {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440003"),
        "name": "Jordan Lee",
        "description": "Frontend developer transitioning to full-stack",
        "role": "Frontend Developer",
        "background": "Works in E-commerce at StartupXYZ. Has medium technical level, transitioning from frontend to full-stack. Prefers hands-on learning with practical examples.",
        "communication_style": "practical_examples",
        "expertise_areas": ["frontend_development", "react", "ui_ux"],
        "metadata": {
            "company": "StartupXYZ",
            "industry": "E-commerce",
            "traits": {
                "tech_comfort_level": "medium",
                "learning_style": "hands_on",
                "preference": "practical_examples"
            }
        }
    }
]

# Initial observations for each persona
PERSONA_OBSERVATIONS = {
    "550e8400-e29b-41d4-a716-446655440001": [
        "I get overwhelmed when people use too much technical jargon",
        "I learn best when concepts are explained with everyday analogies",
        "Visual diagrams and step-by-step instructions really help me understand",
        "I'm working on a DX project but struggle with the testing concepts",
        "I prefer when mentors are patient and encouraging"
    ],
    "550e8400-e29b-41d4-a716-446655440002": [
        "I enjoy diving deep into technical concepts and understanding the theory",
        "I appreciate discussions about trade-offs and architectural decisions",
        "I'm comfortable with complex technical terminology",
        "Currently exploring microservices patterns and event-driven architectures",
        "I like to understand the 'why' behind best practices"
    ],
    "550e8400-e29b-41d4-a716-446655440003": [
        "I learn best by doing - show me code examples and let me try",
        "I'm transitioning from frontend to full-stack development",
        "I understand React/Vue well but backend concepts are newer to me",
        "I prefer practical applications over abstract theory",
        "Real-world examples help me connect frontend knowledge to backend concepts"
    ]
}


async def create_personas():
    """Create demo personas in the database."""
    async with async_session_maker() as session:
        created_count = 0
        
        for persona_data in DEMO_PERSONAS:
            try:
                # Check if persona already exists
                existing = await session.execute(
                    select(Persona).where(Persona.id == persona_data["id"])
                )
                if existing.scalar_one_or_none():
                    print(f"ℹ️  Persona already exists: {persona_data['name']}")
                    continue
                
                # Create persona
                persona = Persona(**persona_data)
                session.add(persona)
                await session.flush()
                
                print(f"✅ Created persona: {persona_data['name']}")
                
                # Add initial observations as narratives
                persona_id_str = str(persona_data["id"])
                for observation in PERSONA_OBSERVATIONS.get(persona_id_str, []):
                    narrative = Narrative(
                        person_id=persona_data["id"],
                        content=observation,
                        narrative_type="self_observation",
                        tags=["initial", "profile", "learning_preference"],
                        context={
                            "source": "demo_setup",
                            "persona_name": persona_data["name"]
                        },
                        created_at=datetime.utcnow()
                    )
                    session.add(narrative)
                
                created_count += 1
                
            except Exception as e:
                print(f"❌ Error creating {persona_data['name']}: {e}")
                await session.rollback()
                continue
        
        if created_count > 0:
            await session.commit()
            print(f"\n✅ Successfully created {created_count} personas!")
        
        return created_count


async def main():
    """Main function."""
    print("🚀 Creating demo personas directly in PersonaKit database...")
    print("=" * 60)
    
    created = await create_personas()
    
    if created > 0:
        print("\nThe Agno Coaching UI will now show real PersonaKit profiles!")
        print("Profile Loaded: ✅")
    else:
        print("\nNo new personas were created.")


if __name__ == "__main__":
    asyncio.run(main())