# Project Index: ShDebug

Generated: 2026-02-16

## Project Structure

```
shdebug/
├── ui/                         # TypeScript + Playwright test harness
│   ├── src/
│   │   ├── extract.ts          # UI output types & JSON writing
│   │   ├── extract.test.ts
│   │   ├── navigation.ts       # Navigation retry logic
│   │   ├── navigation.test.ts
│   │   ├── site-profile.ts     # Extraction strategies & money parsing
│   │   └── site-profile.test.ts
│   ├── e2e/
│   │   └── checkout.spec.ts    # E2E checkout flow tests
│   ├── assets/                 # CSS (Tailwind v4), JS, icons for dashboard
│   ├── *.html                  # Dashboard pages (index, findings, patterns, config, run-details)
│   ├── playwright.config.ts
│   ├── vitest.config.ts
│   ├── tailwind.config.js
│   └── package.json            # pnpm, Vitest 2.1, Playwright 1.52
│
├── api/                        # Python security validation engine
│   ├── src/harness/
│   │   ├── run.py              # Main orchestration (~500 LOC)
│   │   ├── config.py           # pydantic-settings configuration
│   │   ├── scanner.py          # URL path classification & ranking
│   │   ├── normalizer.py       # PostgreSQL data ingestion (~850 LOC)
│   │   ├── pattern_rag.py      # Vector embeddings & strategy retrieval
│   │   ├── frontier.py         # Prioritization logic
│   │   ├── findings.py         # Finding/coverage output
│   │   ├── http.py             # Rate-limited HTTP client (httpx)
│   │   ├── safety.py           # Host allowlist enforcement
│   │   ├── rules.py            # Business rule validation
│   │   ├── scenarios.py        # Test scenario loading
│   │   ├── invariants/
│   │   │   ├── money.py        # Money parsing & validation
│   │   │   └── state.py        # State invariants
│   │   └── evidence/
│   │       ├── capture.py      # Evidence writing
│   │       └── redact.py       # PII/secret redaction
│   ├── tests/                  # 17 pytest files (~1500 LOC)
│   │   ├── test_money_invariants.py
│   │   ├── test_safety_allowlist.py
│   │   ├── test_scanner.py
│   │   ├── test_normalizer.py
│   │   ├── test_pattern_rag.py
│   │   ├── test_evidence_redaction.py
│   │   ├── test_http_layer.py
│   │   ├── test_state_invariants.py
│   │   ├── test_rules_security.py
│   │   ├── test_scenarios.py
│   │   ├── test_frontier.py
│   │   ├── test_findings_output.py
│   │   ├── test_config.py
│   │   ├── test_run_helpers.py
│   │   ├── test_makefile_preflight.py
│   │   ├── test_project_layout.py
│   │   └── test_scan_control_plane_schema.py
│   ├── sql/
│   │   ├── 001_security_data_model.sql     # Core security schema
│   │   ├── 002_ui_pattern_memory.sql       # Pattern RAG tables
│   │   ├── 003_scan_control_plane.sql      # Project/job orchestration
│   │   ├── 004_pgvector_embeddings.sql     # Vector similarity search
│   │   └── 005_job_queue_columns.sql       # Transactional job queue
│   └── pyproject.toml          # uv, Python 3.11+, pytest, ruff, mypy
│
├── server/                     # TypeScript control plane API
│   ├── src/
│   │   ├── app.ts              # HTTP server with in-memory store
│   │   ├── auth.ts             # Bearer token authentication
│   │   ├── config.ts           # Configuration loading
│   │   ├── queue.ts            # Job queue (transactional claim)
│   │   ├── url-normalize.ts    # URL canonicalization
│   │   ├── routes/
│   │   │   ├── projects.ts     # Project CRUD
│   │   │   ├── urls.ts         # URL management
│   │   │   ├── config-lists.ts # Config list management
│   │   │   └── jobs.ts         # Job status/history
│   │   └── schemas/
│   │       └── config-lists.ts # Zod validation schemas
│   └── tests/                  # 4 Vitest files
│       ├── auth.test.ts
│       ├── projects-routes.test.ts
│       ├── config-lists.test.ts
│       └── queue.test.ts
│
├── scripts/
│   ├── preflight.sh            # Playwright browser validation
│   └── batch_scan.sh           # Batch URL scanning
│
├── docs/plans/                 # 9 design/implementation documents
├── runs/                       # Generated evidence artifacts per run
├── Makefile                    # Orchestration (run, ui, api, ingest, pattern-scan)
├── .env.example                # Environment configuration template
├── .github/workflows/ci.yml   # CI: ui-tests, api-tests, server-tests
├── AGENTS.md                   # Coding guidelines
├── CLAUDE.md                   # Claude Code guidance
└── README.md
```

## Entry Points

- **Full pipeline:** `make run` → runs Playwright UI tests then Python API validation
- **UI tests only:** `make ui` or `cd ui && pnpm test:e2e`
- **API validation:** `make api` → `python -m harness.run <run_dir>`
- **Data ingestion:** `make ingest` → `python -m harness.normalizer <run_dir>`
- **Pattern RAG:** `make pattern-scan` → `python -m harness.pattern_rag`
- **Server:** `node server/src/app.ts` (custom HTTP server, no framework)

## Core Modules

### ui/src/extract.ts
- Purpose: Defines UI output data types and writes extracted data to JSON
- Consumed by: checkout.spec.ts (e2e), harness.run (Python reads output)

### ui/src/site-profile.ts
- Purpose: Extraction strategies for different site layouts, money string parsing
- Exports: Strategy selection, currency parsing utilities

### ui/src/navigation.ts
- Purpose: Navigation retry logic for flaky page loads
- Exports: Retry-wrapped navigation helpers

### api/src/harness/run.py
- Purpose: Main orchestration — reads UI output, runs invariant checks, produces findings
- Entry: `python -m harness.run <run_dir>`

### api/src/harness/normalizer.py
- Purpose: PostgreSQL data ingestion — normalizes run artifacts into relational schema
- Entry: `python -m harness.normalizer <run_dir> --database-url <url>`

### api/src/harness/pattern_rag.py
- Purpose: Vector embedding-based strategy retrieval for extraction patterns
- Entry: `python -m harness.pattern_rag --database-url <url> --url <target>`

### api/src/harness/safety.py
- Purpose: Host allowlist enforcement — blocks requests to non-allowed hosts

### api/src/harness/invariants/money.py
- Purpose: Money parsing, validation, arithmetic tolerance checks

### api/src/harness/evidence/redact.py
- Purpose: PII and secret redaction in evidence artifacts

### server/src/app.ts
- Purpose: HTTP server for scan control plane — project management, job queue, URL tracking
- Routes: /projects, /urls, /config-lists, /jobs

### server/src/queue.ts
- Purpose: Job queue with PostgreSQL-based transactional claim (FOR UPDATE SKIP LOCKED)

## Configuration

- `.env.example` → `.env`: BASE_URL, ALLOWLIST_HOSTS, UI selectors, API paths, rate limits, DATABASE_URL
- `api/pyproject.toml`: Python deps (uv-managed), pytest pythonpath=["src"]
- `ui/playwright.config.ts`: 60s timeout, trace on failure, HTTP/2 disabled
- `ui/vitest.config.ts`: Unit test configuration
- `ui/tsconfig.json`: ES2022, NodeNext, strict
- `server/tsconfig.json`: ES2022, NodeNext, strict
- `api/sql/*.sql`: PostgreSQL schema (5 migration files, applied manually)
- `.github/workflows/ci.yml`: CI with 3 parallel jobs (ui-tests, api-tests, server-tests)

## Documentation

- `docs/plans/2026-02-15-moneyflow-test-harness-ui-api.md`: Original UI+API design
- `docs/plans/2026-02-15-security-analyzer-design.md`: Security analyzer architecture
- `docs/plans/2026-02-15-security-data-model-design.md`: PostgreSQL schema design
- `docs/plans/2026-02-15-continuous-security-monitoring-design.md`: Monitoring design
- `docs/plans/2026-02-16-pattern-rag-ranking-stability-design.md`: RAG stability
- `docs/plans/2026-02-16-ui-scanning-analysis-implementation-plan.md`: Dashboard UI plan

## Test Coverage

- **UI unit tests:** 3 files (extract, navigation, site-profile) — `cd ui && pnpm test`
- **UI e2e tests:** 1 file (checkout flow) — `cd ui && pnpm test:e2e`
- **API tests:** 17 files (~1500 LOC) — `cd api && pytest`
- **Server tests:** 4 files (auth, projects, config-lists, queue) — `cd server && pnpm test`
- **CI:** GitHub Actions validates Playwright browser setup on PR/push

## Key Dependencies

### UI (pnpm)
- `@playwright/test@^1.52.0` — browser e2e testing
- `vitest@^2.1.8` — unit testing
- `tailwindcss@^4.0.0` + `@tailwindcss/cli@^4.1.18` — dashboard styling
- `typescript@^5.7.3`

### API (uv)
- `httpx@>=0.27.0` — async HTTP client
- `psycopg[binary]@>=3.2.0` — PostgreSQL driver
- `pydantic-settings@>=2.6.0` — config from env vars
- `rich@>=13.9.0` — terminal output
- `tenacity@>=9.0.0` — retry logic
- `hypothesis@>=6.112.0` — property-based testing (dev)
- `ruff@>=0.7.0` — linting (dev)
- `mypy@>=1.11.2` — type checking (dev)

### Server (pnpm)
- `vitest@^2.1.9` — unit testing
- `typescript@^5.7.3`

## Quick Start

1. `cp .env.example .env` — configure BASE_URL and selectors
2. `cd ui && pnpm install && pnpm exec playwright install` — set up UI
3. `cd api && uv venv && source .venv/bin/activate && uv sync` — set up API
4. `cd server && pnpm install` — set up server
5. `make run` — execute full pipeline (outputs to `runs/run-<timestamp>/`)
6. `make ingest RUN_DIR=<path> DATABASE_URL=<url>` — persist to PostgreSQL
