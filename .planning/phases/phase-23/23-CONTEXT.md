# Phase 23: Telemetry Ingestion Pipeline - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers automated data collection infrastructure that ingests GitHub Actions workflow data and LLM telemetry CSV logs into PostgreSQL. This data will power the observability dashboard (Phase 25).

</domain>

<decisions>
## Implementation Decisions

### Data Sources

1. **GitHub Actions API** - Workflow runs, status, duration, timestamps
2. **CSV Telemetry Logs** - LLM call logs (from `.telemetry/usage.csv`)

### Schema Design

- `workflow_runs` table - GitHub Actions data
- `llm_calls` table - Individual LLM call telemetry
- `coverage_snapshots` table - Coverage data (also used by Phase 24)

### Ingestion Strategy

- **GitHub data**: Python script using `requests` to call GitHub API
- **CSV data**: Python script parsing existing CSV logs
- **Scheduling**: GitHub Actions cron job (every 6 hours)
- **Manual trigger**: CLI command for ad-hoc ingestion

### Technology Choices

- **Language**: Python 3.11+ (matches existing tooling)
- **Database**: PostgreSQL (via packages/db/ from v1.6)
- **GitHub API**: REST API v3 with token (GITHUB_TOKEN in Actions, GITHUB_PERSONAL_TOKEN for local)
- **ORM**: SQLAlchemy 2.0 (consistent with packages/db/)

### Storage Location

- New package: `packages/telemetry/` for ingestion scripts and models
- Migrations: Add to `packages/db/src/migrations/versions/`

### Access Control

- GitHub token stored in repository secrets (`GITHUB_TOKEN` for Actions)
- Local development: Use `GITHUB_PERSONAL_TOKEN` env var
- Read-only GitHub API access (workflow scope)

### Data Retention

- **Historical backfill**: Last 30 days only (avoid API rate limits and stale data)
- **Data pruning**: Delete records older than 6 months
- Implemented as DELETE statement at end of cron ingestion script

</decisions>

<specifics>
## Specific Ideas

### Database Schema

```sql
-- workflow_runs table
CREATE TABLE workflow_runs (
    id SERIAL PRIMARY KEY,
    github_run_id BIGINT NOT NULL,
    run_attempt INTEGER DEFAULT 1,
    workflow_name VARCHAR(255) NOT NULL,
    branch VARCHAR(255),
    commit_sha VARCHAR(40),
    event_type VARCHAR(50), -- push, pull_request, schedule
    status VARCHAR(20) NOT NULL, -- success, failure, cancelled
    conclusion VARCHAR(20), -- success, failure, cancelled, skipped
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    html_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(github_run_id, run_attempt)
);

-- llm_calls table
CREATE TABLE llm_calls (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    phase VARCHAR(50),
    prompt_name VARCHAR(255), -- specific prompt template or task ID
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    estimated_cost DECIMAL(10, 6),
    success BOOLEAN,
    error_message TEXT, -- captures failure reason when success is false
    duration_ms INTEGER,
    session_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(timestamp, session_id, prompt_name)
);
```

### CLI Commands

```bash
# Ingest GitHub workflow runs (backfill last 30 days by default)
pnpm telemetry:ingest:github [--since 2026-02-01]

# Ingest CSV telemetry (configurable path, default: .telemetry/usage.csv)
pnpm telemetry:ingest:csv [path/to/telemetry.csv]

# Run all ingestion
pnpm telemetry:ingest:all

# Show telemetry statistics
pnpm telemetry:stats
```

### Environment Variables

```bash
# Required: GitHub API token
# In GitHub Actions: GITHUB_TOKEN (automatically provided)
# Local development: GITHUB_PERSONAL_TOKEN (user-provided)
GITHUB_TOKEN=${GITHUB_TOKEN:-$GITHUB_PERSONAL_TOKEN}

# Optional: CSV log path (default: .telemetry/usage.csv)
TELEMETRY_CSV_PATH=.telemetry/usage.csv
```

### GitHub Actions Cron Job

```yaml
- cron: "0 */6 * * *" # Every 6 hours
```

### CSV Format (Current)

The existing telemetry CSV uses this schema:

```
timestamp,model,prompt_tokens,completion_tokens,task_success,task_type,duration_ms,notes
```

Mapped to database fields:

- `timestamp` → `timestamp`
- `model` → `model`
- `prompt_tokens` → `input_tokens`
- `completion_tokens` → `output_tokens`
- `task_success` → `success`
- `task_type` → `prompt_name` (optional mapping)
- `duration_ms` → `duration_ms`
- `notes` → (can be stored or parsed for `phase`)

</specifics>

<deferred>
## Deferred Ideas

- Real-time webhook ingestion (complex infrastructure)
- Multiple repository aggregation (out of scope)
- Anomaly detection on telemetry (ML, out of scope)

</deferred>

<implementation-notes>
## Implementation Notes

### Idempotency

- Workflow runs: Use UPSERT based on `(github_run_id, run_attempt)` unique constraint
- LLM calls: Use UPSERT based on `(timestamp, session_id, prompt_name)` unique constraint

### Error Handling

- CSV parsing: Skip invalid rows, log warnings
- GitHub API: Handle rate limits with exponential backoff
- Database: Transaction rollback on batch failure

### Data Pruning

Add to end of ingestion script:

```sql
-- Prune workflow runs older than 6 months
DELETE FROM workflow_runs WHERE created_at < NOW() - INTERVAL '6 months';
-- Prune LLM calls older than 6 months
DELETE FROM llm_calls WHERE created_at < NOW() - INTERVAL '6 months';
```

</implementation-notes>

---

_Phase: 23-telemetry-ingestion-pipeline_
_Context updated: 2026-02-25_
