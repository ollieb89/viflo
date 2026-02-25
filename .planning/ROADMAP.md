# Viflo Roadmap

## Milestones

- ✅ **v1.0 MVP** — Phases 0–4 (shipped 2026-02-23) — [Archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Dogfooding** — Phases 5–10 (shipped 2026-02-24) — [Archive](milestones/v1.1-ROADMAP.md)
- ✅ **v1.2 Foundation Skills** — Phase 11 (shipped 2026-02-24) — [Archive](milestones/v1.2-ROADMAP.md)
- ✅ **v1.3 Expert Skills** — Phases 12–14 (shipped 2026-02-24) — [Archive](milestones/v1.3-ROADMAP.md)
- ✅ **v1.4 Project Tooling** — Phases 15–16 (shipped 2026-02-24) — [Archive](milestones/v1.4-ROADMAP.md)
- ✅ **v1.5 viflo init CLI** — Phases 17–19 (shipped 2026-02-24) — [Archive](milestones/v1.5-ROADMAP.md)
- 📋 **v1.6 Infrastructure Hardening & Quality Gates** — Phases 20–22 (planned)

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
- [ ] **Phase 21: Test Reliability and Budget Guards** — enforce baseline tests, coverage ratchet, and explicit low-cost/local gating for LLM-assisted tests
- [ ] **Phase 22: Database Ops for Integration** — operationalize migration command and CI database provisioning for integration tests

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

## Progress

| Phase                                  | Milestone | Plans Complete | Status      | Completed  |
| -------------------------------------- | --------- | -------------- | ----------- | ---------- |
| 0. Foundation                          | v1.0      | —              | Complete    | 2026-02-23 |
| 1. Core Skills Development             | v1.0      | —              | Complete    | 2026-02-23 |
| 2. Extended Skills                     | v1.0      | —              | Complete    | 2026-02-23 |
| 3. DevOps & Deployment                 | v1.0      | —              | Complete    | 2026-02-23 |
| 4. Polish & Community                  | v1.0      | 4/4            | Complete    | 2026-02-23 |
| 5. CI & Security                       | v1.1      | 2/2            | Complete    | 2026-02-23 |
| 6. Test Suite                          | v1.1      | 2/2            | Complete    | 2026-02-23 |
| 7. Content Hygiene                     | v1.1      | 3/3            | Complete    | 2026-02-23 |
| 8. Verification Closure                | v1.1      | 2/2            | Complete    | 2026-02-23 |
| 9. Workspace Tooling                   | v1.1      | 2/2            | Complete    | 2026-02-24 |
| 10. Commit & Verify                    | v1.1      | 3/3            | Complete    | 2026-02-24 |
| 11. Foundation Skills                  | v1.2      | 3/3            | Complete    | 2026-02-24 |
| 12. RAG / Vector Search                | v1.3      | 2/2            | Complete    | 2026-02-24 |
| 13. Agent Architecture                 | v1.3      | 2/2            | Complete    | 2026-02-24 |
| 14. Stripe Payments                    | v1.3      | 2/2            | Complete    | 2026-02-24 |
| 15. Integration Review                 | v1.4      | 3/3            | Complete    | 2026-02-24 |
| 16. CLI Foundation                     | v1.4      | 2/2            | Complete    | 2026-02-24 |
| 17. Minimal Mode                       | v1.5      | 2/2            | Complete    | 2026-02-24 |
| 18. Full Mode                          | v1.5      | 2/2            | Complete    | 2026-02-24 |
| 19. Polish                             | v1.5      | 2/2            | Complete    | 2026-02-24 |
| 20. Gate Enforcement Hardening         | v1.6      | 2/2            | Complete    | 2026-02-25 |
| 21. Test Reliability and Budget Guards | v1.6      | 0/2            | Planned     | —          |
| 22. Database Ops for Integration       | v1.6      | 0/1            | Planned     | —          |
