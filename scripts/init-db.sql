-- PersonaKit v0.1 Database Initialization
-- Sets up timezone support and extensions

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Future extensions (v0.2+)
-- CREATE EXTENSION IF NOT EXISTS "vector";  -- Uncomment when using pgvector

-- Set timezone
SET timezone = 'UTC';

-- Create custom types if needed
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'observation_type') THEN
        CREATE TYPE observation_type AS ENUM ('work_session', 'user_input', 'calendar_event');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_status') THEN
        CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'done', 'failed');
    END IF;
END$$;