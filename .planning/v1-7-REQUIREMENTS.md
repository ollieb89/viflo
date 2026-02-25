# Requirements: Viflo v1.7

**Defined:** 2026-02-25
**Core Value:** Operational visibility into development quality and AI-assisted workflow costs

## v1.7: Observability & Analytics

Requirements for milestone v1.7. Building on v1.6's infrastructure hardening, this milestone delivers dashboards and insights for maintainers to understand quality trends and AI usage costs.

### Quality Observability

- [ ] **OBS-01**: Maintainer can view historical quality gate pass/fail trend by workflow and phase
  - Source: GitHub Actions workflow run data
  - Storage: PostgreSQL (packages/db/ from v1.6)
  - Display: Simple web dashboard or CLI report

- [ ] **OBS-02**: Maintainer can see test coverage trend over time in a lightweight dashboard
  - Source: Coverage ratchet data (apps/web/.coverage/baseline.json history)
  - Storage: PostgreSQL
  - Display: Line chart showing coverage % over time

### Agent Telemetry & Cost Analytics

- [ ] **AGCAP-01**: Agent telemetry and cost dashboard for milestone-level model usage analytics
  - Source: CSV telemetry logs (from scripts/telemetry/)
  - Storage: PostgreSQL with time-series friendly schema
  - Metrics: Tokens per model, cost per milestone, success rate by phase
  - Display: Dashboard with filters by date range, milestone, model

### Data Collection Infrastructure

- [ ] **TELEM-01**: Automated ingestion of GitHub Actions workflow runs into database
  - GitHub API integration for workflow history
  - Scheduled job (GitHub Actions cron) or manual trigger

- [ ] **TELEM-02**: Coverage data tracking over time
  - Store coverage snapshots per commit/PR
  - Track lines, functions, branches, statements separately

### Dashboard Delivery

- [ ] **DASH-01**: Web dashboard for quality metrics
  - Simple Next.js app or static site
  - Read-only view of aggregated data
  - Time range filtering

- [ ] **DASH-02**: CLI report for quick insights
  - `viflo dashboard --quality` - Recent gate trends
  - `viflo dashboard --cost` - Cost summary for milestone
  - `viflo dashboard --coverage` - Coverage trend report

## Out of Scope

| Feature                    | Reason                                            |
| -------------------------- | ------------------------------------------------- |
| Real-time alerting         | Complex infrastructure; defer to v1.8             |
| Predictive analytics       | Requires ML/data science; out of scope            |
| Multi-team cost allocation | Complex auth/permissions; defer                   |
| Live log streaming         | Infrastructure heavy; batch processing sufficient |

## Traceability

| Requirement | Phase    | Status  |
| ----------- | -------- | ------- |
| OBS-01      | Phase 23 | Pending |
| OBS-02      | Phase 24 | Pending |
| AGCAP-01    | Phase 25 | Pending |
| TELEM-01    | Phase 23 | Pending |
| TELEM-02    | Phase 24 | Pending |
| DASH-01     | Phase 25 | Pending |
| DASH-02     | Phase 25 | Pending |

---

_Requirements defined: 2026-02-25 for v1.7 planning_
