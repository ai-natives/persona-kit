#!/bin/bash
# Manual setup script for demo profiles using PersonaKit CLI

echo "🚀 Setting up PersonaKit demo profiles..."
echo "=" | head -c 60 && echo

# Navigate to persona-kit root
cd ../../..

# Create Sato-san
echo "📝 Creating Sato-san..."
cat << 'EOF' | uv run python
import asyncio
from src.repositories.person import PersonRepository
from src.database import get_session
from src.models.person import Person
import uuid

async def create_sato_san():
    async with get_session() as session:
        repo = PersonRepository(session)
        
        # Create person
        person = Person(
            id=uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
            name="Sato-san",
            email="sato.san@example.com",
            metadata={
                "role": "Assistant Project Manager",
                "company": "DX Initiative Corp",
                "industry": "Technology Services"
            }
        )
        
        await repo.create(person)
        await session.commit()
        print("✅ Created Sato-san")

asyncio.run(create_sato_san())
EOF

# Add traits for Sato-san
echo "Adding traits for Sato-san..."
PERSON_ID="550e8400-e29b-41d4-a716-446655440001"

uv run python -m src.cli.main trait set $PERSON_ID tech.comfort_level low --confidence 0.9
uv run python -m src.cli.main trait set $PERSON_ID learning.style visual_step_by_step --confidence 0.8
uv run python -m src.cli.main trait set $PERSON_ID communication.preference simple_analogies --confidence 0.9

# Add observations
echo "Adding initial observations..."
uv run python -m src.cli.main narrative add $PERSON_ID "I get overwhelmed when people use too much technical jargon" --type self_observation
uv run python -m src.cli.main narrative add $PERSON_ID "I learn best when concepts are explained with everyday analogies" --type self_observation
uv run python -m src.cli.main narrative add $PERSON_ID "Visual diagrams and step-by-step instructions really help me understand" --type self_observation

echo ""
echo "✅ Sato-san profile created!"
echo ""
echo "Note: This script only sets up Sato-san as an example."
echo "You can create Alex Chen and Jordan Lee similarly with IDs:"
echo "- Alex Chen: 550e8400-e29b-41d4-a716-446655440002"
echo "- Jordan Lee: 550e8400-e29b-41d4-a716-446655440003"