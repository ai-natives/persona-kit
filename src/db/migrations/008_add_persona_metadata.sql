-- Migration: Add metadata fields to personas table
-- Phase 6.5: Support for configuration-driven mappers

-- Add metadata column to personas (if not exists)
ALTER TABLE personas 
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- These columns were added in migration 007 but let's ensure they exist
-- Using IF NOT EXISTS prevents errors if they already exist
-- (columns were already added in previous migration)