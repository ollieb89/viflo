# Viflo Roadmap

## Milestones

- ✅ **v1.0 MVP** — Phases 0–4 (shipped 2026-02-23) — [Archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Dogfooding** — Phases 5–10 (shipped 2026-02-24) — [Archive](milestones/v1.1-ROADMAP.md)
- ✅ **v1.2 Foundation Skills** — Phase 11 (shipped 2026-02-24) — [Archive](milestones/v1.2-ROADMAP.md)
- ✅ **v1.3 Expert Skills** — Phases 12–14 (shipped 2026-02-24) — [Archive](milestones/v1.3-ROADMAP.md)
- ✅ **v1.4 Project Tooling** — Phases 15–16 (shipped 2026-02-24) — [Archive](milestones/v1.4-ROADMAP.md)
- ✅ **v1.5 viflo init CLI** — Phases 17–19 (shipped 2026-02-24) — [Archive](milestones/v1.5-ROADMAP.md)
- ✅ **v1.6 Infrastructure Hardening & Quality Gates** — Phases 20–22 (shipped 2026-02-25)
- 📋 **v1.7 Observability & Analytics** — Phases 23–25 (planned)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 0–4) — SHIPPED 2026-02-23</summary>

- [x] Phase 0: Foundation — completed 2026-02-23
- [x] Phase 1: Core Skills Development — completed 2026-02-23
- [x] Phase 2: Extended Skills & Examples — completed 2026-02-23
- [x] Phase 3: DevOps & Deployment — completed 2026-02-23
- [x] Phase 4: Polish & Community (4/4 plans) — completed 2026-02-23

</details>

<details>
<summary>✅ v1.1 Dogfooding (Phases 5–10) — SHIPPED 2026-02-24</summary>

- [x] Phase 5: CI & Security (2/2 plans) — completed 2026-02-23
- [x] Phase 6: Test Suite (2/2 plans) — completed 2026-02-23
- [x] Phase 7: Content Hygiene (3/3 plans) — completed 2026-02-23
- [x] Phase 8: Verification & Requirements Closure (2/2 plans) — completed 2026-02-23
- [x] Phase 9: Workspace & Developer Tooling (2/2 plans) — completed 2026-02-24
- [x] Phase 10: Commit and Verify Uncommitted Work (3/3 plans) — completed 2026-02-24

</details>

<details>
<summary>✅ v1.2 Foundation Skills (Phase 11) — SHIPPED 2026-02-24</summary>

- [x] Phase 11: Foundation Skills (3/3 plans) — completed 2026-02-24

</details>

<details>
<summary>✅ v1.3 Expert Skills (Phases 12–14) — SHIPPED 2026-02-24</summary>

- [x] Phase 12: RAG / Vector Search (2/2 plans) — completed 2026-02-24
- [x] Phase 13: Agent Architecture (2/2 plans) — completed 2026-02-24
- [x] Phase 14: Stripe Payments (2/2 plans) — completed 2026-02-24

</details>

<details>
<summary>✅ v1.4 Project Tooling (Phases 15–16) — SHIPPED 2026-02-24</summary>

- [x] Phase 15: Integration Review (3/3 plans) — completed 2026-02-24
- [x] Phase 16: CLI Foundation (2/2 plans) — completed 2026-02-24

</details>

<details>
<summary>✅ v1.5 viflo init CLI (Phases 17–19) — SHIPPED 2026-02-24</summary>

- [x] Phase 17: Minimal Mode (2/2 plans) — completed 2026-02-24
- [x] Phase 18: Full Mode (2/2 plans) — completed 2026-02-24
- [x] Phase 19: Polish (2/2 plans) — completed 2026-02-24

</details>

### 📋 v1.6 Infrastructure Hardening & Quality Gates (Phases 20–22)

- [x] **Phase 20: Gate Enforcement Hardening** — align/activate GitHub Actions gates with local reproducibility and enforce secret scanning hooks (completed 2026-02-25)
- [x] **Phase 21: Test Reliability and Budget Guards** — enforce baseline tests, coverage ratchet, and explicit low-cost/local gating for LLM-assisted tests (completed 2026-02-25)
- [x] **Phase 22: Database Ops for Integration** — operationalize migration command and CI database provisioning for integration tests (completed 2026-02-25)

## Phase Details

### Phase 20: Gate Enforcement Hardening

**Goal**: Repository-level quality and security gates are deterministic, active, and reproducible locally
**Depends on**: Phase 19
**Requirements**: GATE-01, GATE-02, SEC-01, SEC-02
**Success Criteria** (what must be TRUE):

1. Push and pull request workflows block merge when lint, typecheck, test, or build fails
2. Local documented quality-gate command path reproduces CI pass/fail behavior
3. Pre-commit hooks block staged commits containing secrets detected by `gitleaks` or `detect-secrets`
4. One bootstrap command installs or refreshes pre-commit security hooks for contributors
   **Plans**: 2 plans

### Phase 21: Test Reliability and Budget Guards

**Goal**: Test safety net is measurable and regression-resistant while optional LLM testing remains cost-controlled
**Depends on**: Phase 20
**Requirements**: TEST-01, TEST-02, TEST-03, COST-01
**Success Criteria** (what must be TRUE):

1. `apps/web` Vitest suite runs in CI and local command parity path
2. At least 5 baseline unit tests for core web components/utilities run green in CI
3. Coverage ratchet fails CI on coverage regression below baseline
4. Any LLM-assisted test path is off by default and only runs via explicit low-cost/local model mode
   **Plans**: 2 plans

### Phase 22: Database Ops for Integration

**Goal**: Database schema lifecycle is operationalized for local development and CI integration testing
**Depends on**: Phase 21
**Requirements**: DBOP-01, DBOP-02
**Success Criteria** (what must be TRUE):

1. Single workspace migration command provisions or updates development schema from committed migrations
2. CI integration-test flow starts database service and runs migration command before integration tests
3. Migration flow is documented with expected local and CI invocation paths
   **Plans**: 1 plan

### 📊 v1.7 Observability & Analytics (Phases 23–25)

- [ ] **Phase 23: Telemetry Ingestion Pipeline** — GitHub Actions workflow data and LLM telemetry CSV ingestion into PostgreSQL
- [ ] **Phase 24: Coverage History Tracking** — Store and trend coverage data over time with automated snapshots
- [ ] **Phase 25: Observability Dashboard** — Web dashboard and CLI reports for quality metrics and cost analytics

## Phase Details

| Phase                                  | Milestone | Plans Complete | Status     | Completed  |
| -------------------------------------- | --------- | -------------- | ---------- | ---------- |
| 0. Foundation                          | v1.0      | —              | Complete   | 2026-02-23 |
| 1. Core Skills Development             | v1.0      | —              | Complete   | 2026-02-23 |
| 2. Extended Skills                     | v1.0      | —              | Complete   | 2026-02-23 |
| 3. DevOps & Deployment                 | v1.0      | —              | Complete   | 2026-02-23 |
| 4. Polish & Community                  | v1.0      | 4/4            | Complete   | 2026-02-23 |
| 5. CI & Security                       | v1.1      | 2/2            | Complete   | 2026-02-23 |
| 6. Test Suite                          | v1.1      | 2/2            | Complete   | 2026-02-23 |
| 7. Content Hygiene                     | v1.1      | 3/3            | Complete   | 2026-02-23 |
| 8. Verification Closure                | v1.1      | 2/2            | Complete   | 2026-02-23 |
| 9. Workspace Tooling                   | v1.1      | 2/2            | Complete   | 2026-02-24 |
| 10. Commit & Verify                    | v1.1      | 3/3            | Complete   | 2026-02-24 |
| 11. Foundation Skills                  | v1.2      | 3/3            | Complete   | 2026-02-24 |
| 12. RAG / Vector Search                | v1.3      | 2/2            | Complete   | 2026-02-24 |
| 13. Agent Architecture                 | v1.3      | 2/2            | Complete   | 2026-02-24 |
| 14. Stripe Payments                    | v1.3      | 2/2            | Complete   | 2026-02-24 |
| 15. Integration Review                 | v1.4      | 3/3            | Complete   | 2026-02-24 |
| 16. CLI Foundation                     | v1.4      | 2/2            | Complete   | 2026-02-24 |
| 17. Minimal Mode                       | v1.5      | 2/2            | Complete   | 2026-02-24 |
| 18. Full Mode                          | v1.5      | 2/2            | Complete   | 2026-02-24 |
| 19. Polish                             | v1.5      | 2/2            | Complete   | 2026-02-24 |
| 20. Gate Enforcement Hardening         | v1.6      | Complete       | 2026-02-25 | 2026-02-25 |
| 21. Test Reliability and Budget Guards | v1.6      | 2/2            | Complete   | 2026-02-25 |
| 22. Database Ops for Integration       | v1.6      | 1/1            | Complete   | 2026-02-25 |
| 23. Telemetry Ingestion Pipeline       | v1.7      | 0/2            | Planned    | —          |
| 24. Coverage History Tracking          | v1.7      | 0/1            | Planned    | —          |
| 25. Observability Dashboard            | v1.7      | 0/2            | Planned    | —          |

### Phase 23: Telemetry Ingestion Pipeline

**Goal**: Automated data collection from GitHub Actions and LLM telemetry into queryable PostgreSQL storage
**Depends on**: Phase 22
**Requirements**: TELEM-01, OBS-01 (partial)
**Success Criteria** (what must be TRUE):

1. GitHub Actions workflow run data is ingested into database (workflow name, status, duration, timestamp)
2. LLM telemetry CSV logs are parsed and stored (model, tokens, cost, success/failure, phase)
3. Ingestion can be run manually or on schedule via GitHub Actions cron
4. Schema supports time-series queries and milestone-level aggregation
   **Plans**: 2 plans

### Phase 24: Coverage History Tracking

**Goal**: Persistent coverage tracking to visualize trends over time
**Depends on**: Phase 23
**Requirements**: TELEM-02, OBS-02
**Success Criteria** (what must be TRUE):

1. Coverage snapshots stored per commit with timestamp and git ref
2. Historical coverage data queryable by date range and branch
3. Coverage regression detection beyond single baseline (trend analysis)
4. Data accessible to dashboard for visualization
   **Plans**: 1 plan

### Phase 25: Observability Dashboard

**Goal**: Accessible insights for maintainers on quality trends and AI usage costs
**Depends on**: Phase 24
**Requirements**: OBS-01, OBS-02, AGCAP-01, DASH-01, DASH-02
**Success Criteria** (what must be TRUE):

1. Web dashboard displays quality gate pass/fail trends by workflow over time
2. Coverage trend chart shows lines/functions/branches/statements over time
3. Cost dashboard shows tokens per model, cost per milestone, success rates
4. CLI provides quick reports: `viflo dashboard --quality`, `--cost`, `--coverage`
5. Dashboard is read-only, requires no authentication for local development
   **Plans**: 2 plans
