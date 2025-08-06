-- Migration: Add mapper_configs table for configuration-driven mappers
-- Phase 6.5: Configuration-Driven Architecture

-- Create enum for mapper status
CREATE TYPE mapper_status AS ENUM ('draft', 'active', 'deprecated');

-- Create mapper_configs table
CREATE TABLE mapper_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    configuration JSONB NOT NULL,
    status mapper_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP
);

-- Create indexes
CREATE UNIQUE INDEX idx_mapper_config_id_version ON mapper_configs(config_id, version);
CREATE INDEX idx_mapper_config_status ON mapper_configs(config_id, status);
CREATE INDEX idx_mapper_config_usage ON mapper_configs(last_used_at);

-- Add updated_at trigger
CREATE TRIGGER update_mapper_configs_updated_at
    BEFORE UPDATE ON mapper_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add column to personas table to track which mapper config was used
ALTER TABLE personas ADD COLUMN mapper_config_id UUID REFERENCES mapper_configs(id);

-- Add column to feedback table to track which rule generated the suggestion
ALTER TABLE feedback ADD COLUMN rule_id VARCHAR(100);
ALTER TABLE feedback ADD COLUMN mapper_version INTEGER;