-- Enable commonly used PostgreSQL extensions

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- JSONB operations
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Update statistics
ANALYZE;
