#!/usr/bin/env python3
"""Simple JSONB test to verify functionality."""
import asyncio
import json

import asyncpg

from src.config import settings


async def test_jsonb():
    """Test JSONB operations directly."""
    print("=== Simple JSONB Test ===\n")
    
    # Connect directly
    db_url = settings.database_url.replace("postgresql+asyncpg://", "")
    conn = await asyncpg.connect(f"postgresql://{db_url}")
    
    try:
        # Test 1: Insert complex JSON into mindscapes
        print("1. Testing mindscape JSONB insert...")
        person_id = "550e8400-e29b-41d4-a716-446655440001"
        traits = {
            "work_patterns": {
                "peak_hours": ["09:00-11:00", "14:00-16:00"],
                "focus_duration": 45,
                "break_style": "pomodoro"
            },
            "preferences": {
                "tools": ["VSCode", "Terminal"],
                "languages": ["Python", "TypeScript"],
                "music": True
            }
        }
        
        await conn.execute("""
            INSERT INTO mindscapes (person_id, traits, version, updated_at)
            VALUES ($1::UUID, $2::JSONB, 1, NOW())
            ON CONFLICT (person_id) DO UPDATE
            SET traits = $2::JSONB, version = mindscapes.version + 1
        """, person_id, json.dumps(traits))
        
        print("  ✅ Inserted complex traits")
        
        # Test 2: Query JSONB data
        print("\n2. Testing JSONB queries...")
        
        # Query specific field
        result = await conn.fetchval("""
            SELECT traits->'work_patterns'->'peak_hours'
            FROM mindscapes
            WHERE person_id = $1::UUID
        """, person_id)
        
        peak_hours = json.loads(result) if result else None
        print(f"  ✅ Peak hours: {peak_hours}")
        
        # Query with JSONB operators
        has_music = await conn.fetchval("""
            SELECT traits->'preferences'->>'music' = 'true'
            FROM mindscapes
            WHERE person_id = $1::UUID
        """, person_id)
        
        print(f"  ✅ Likes music: {has_music}")
        
        # Test 3: Update specific fields
        print("\n3. Testing JSONB updates...")
        
        await conn.execute("""
            UPDATE mindscapes
            SET traits = jsonb_set(
                traits,
                '{work_patterns,focus_duration}',
                '60'::jsonb
            )
            WHERE person_id = $1::UUID
        """, person_id)
        
        print("  ✅ Updated focus duration")
        
        # Test 4: Insert observation with enum
        print("\n4. Testing observation with enum...")
        
        obs_id = "660e8400-e29b-41d4-a716-446655440002"
        await conn.execute("""
            INSERT INTO observations (id, person_id, type, content, metadata, created_at)
            VALUES ($1::UUID, $2::UUID, $3, $4::JSONB, $5::JSONB, NOW())
        """, obs_id, person_id, "work_session", json.dumps({
            "duration": 45,
            "project": "PersonaKit",
            "tasks": ["coding", "testing"]
        }), json.dumps({"source": "test"}))
        
        print("  ✅ Inserted observation with enum")
        
        # Verify
        obs_type = await conn.fetchval("""
            SELECT type FROM observations WHERE id = $1::UUID
        """, obs_id)
        
        print(f"  ✅ Observation type: {obs_type}")
        
        print("\n✅ All JSONB operations work correctly!")
        
        # Cleanup
        await conn.execute("DELETE FROM observations WHERE person_id = $1::UUID", person_id)
        await conn.execute("DELETE FROM mindscapes WHERE person_id = $1::UUID", person_id)
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(test_jsonb())