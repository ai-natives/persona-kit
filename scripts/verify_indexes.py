#!/usr/bin/env python3
"""Verify database indexes are created correctly."""
import asyncio

import asyncpg

from src.config import settings


async def verify_indexes():
    """Check that all expected indexes exist in the database."""
    # Parse connection URL
    db_url = settings.database_url.replace("postgresql+asyncpg://", "")
    
    # Connect directly with asyncpg
    conn = await asyncpg.connect(f"postgresql://{db_url}")
    
    try:
        # Query for all indexes
        query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
        """
        
        indexes = await conn.fetch(query)
        
        print("=== Database Indexes ===\n")
        
        current_table = None
        for idx in indexes:
            if idx['tablename'] != current_table:
                current_table = idx['tablename']
                print(f"\nTable: {current_table}")
                print("-" * 50)
            
            print(f"  {idx['indexname']}")
            print(f"    {idx['indexdef']}")
        
        # Check for expected indexes
        expected = [
            "idx_observations_person_created",
            "idx_mindscapes_person",
            "idx_personas_expires",
            "idx_personas_person_id",
            "idx_feedback_persona",
            "idx_outbox_status",
        ]
        
        index_names = [idx['indexname'] for idx in indexes]
        
        print("\n=== Index Verification ===\n")
        all_found = True
        for expected_idx in expected:
            if expected_idx in index_names:
                print(f"✅ {expected_idx}")
            else:
                print(f"❌ {expected_idx} - NOT FOUND")
                all_found = False
        
        if all_found:
            print("\n✅ All expected indexes are present!")
        else:
            print("\n❌ Some indexes are missing!")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(verify_indexes())