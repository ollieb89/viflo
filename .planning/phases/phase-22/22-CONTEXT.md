# Phase 22: Database Ops for Integration - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers a minimal, operational database schema lifecycle for local development and CI integration testing. Scope is limited to PostgreSQL setup, migration tooling, and CI service integration—not production infrastructure or complex data models.

</domain>

<decisions>
## Implementation Decisions

### Database Choice

- **PostgreSQL 16** — Matches existing `database-design` skill (SQLAlchemy/Alembic)
- **Local Docker** for development — Simple, reproducible, no cloud dependencies
- **GitHub Actions service container** for CI — Ephemeral, isolated, standard pattern

### Migration Tool

- **Alembic** (via SQLAlchemy 2.0) — Established in `.agent/skills/database-design`
- **Location:** `packages/db/` — Shared database package for migrations and models
- **Not Prisma** — Aligns with Python backend patterns in existing skills

### Workspace Command

- **`pnpm db:migrate`** — Simple, no Turborepo dependency needed
- Alternative: `pnpm --filter @viflo/db migrate` if we create a db package
- Command runs: `docker-compose up -d postgres` (if not running) + `alembic upgrade head`

### Integration Test Strategy

- **Location:** `packages/db/tests/integration/` — Database-specific integration tests
- **Pattern:** Test migrations + basic CRUD against real PostgreSQL
- **CI:** Database service starts before tests, migrations run, tests execute

### Package Structure

```
packages/db/
├── src/
│   ├── models/          # SQLAlchemy models
│   ├── migrations/      # Alembic versions
│   └── connection.py    # Database connection/session
├── tests/
│   └── integration/     # Integration tests
├── docker-compose.yml   # Local PostgreSQL
├── alembic.ini         # Alembic config
└── package.json        # Scripts: migrate, reset, test:integration
```

### CI Integration

- Add `integration` job to `.github/workflows/ci.yml`
- Service: `postgres:16-alpine`
- Steps: Start service → Run migrations → Run integration tests
- Does not block merge on failure initially (observation period)

### Environment Configuration

- `.env.template` additions: `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- CI: Use GitHub Actions service hostname (`postgres`)
- Local: Use `localhost:5432`

</decisions>

<specifics>
## Specific Ideas

### Migration Workflow

```bash
# Local development
pnpm db:up          # Start PostgreSQL container
pnpm db:migrate     # Run migrations
pnpm db:reset       # Drop, recreate, migrate (fresh start)

# Creating new migration
pnpm db:revision -- -m "Add user table"

# Integration tests
pnpm db:test        # Start test DB, run migrations, run tests
```

### CI Service Configuration

```yaml
integration:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:16-alpine
      env:
        POSTGRES_USER: test
        POSTGRES_PASSWORD: test
        POSTGRES_DB: test
      options: >-
        --health-cmd pg_isready
        --health-interval 10s
        --health-timeout 5s
        --health-retries 5
      ports:
        - 5432:5432
```

### Success Criteria Verification

1. **DBOP-01**: `pnpm db:migrate` completes successfully locally
2. **DBOP-02**: CI integration job passes with database service
3. **Documentation**: MIGRATIONS.md explains local and CI workflows

</specifics>

<deferred>
## Deferred Ideas

- Production database provisioning (Neon, RDS, etc.)
- Complex multi-region migration strategies
- Database per tenant architecture
- Advanced migration safety checks (beyond Alembic basics)
- Migration rollback automation in CI

</deferred>

<open-questions>
## Open Questions (for user)

1. **Models scope**: Should we create a simple example model (e.g., `projects` table) or just the migration infrastructure?

2. **Test depth**: How many integration tests? Just one smoke test (connect + migrate), or full CRUD tests?

3. **Naming**: Prefer `packages/db/` or `packages/database/` for the package?

4. **CLI exposure**: Should `viflo` CLI get a `db` subcommand (e.g., `viflo db migrate`), or keep it pnpm-only?

</open-questions>

---

_Phase: 22-database-ops-for-integration_
_Context gathered: 2026-02-25_
