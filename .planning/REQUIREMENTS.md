# Requirements: Viflo

**Defined:** 2026-02-24
**Core Value:** A complete agentic dev environment you can install in one command — structured methodology, ready-made skills, and proven workflows so teams skip setup and ship faster.

## v1.6 Requirements

Requirements for milestone v1.6 Infrastructure Hardening & Quality Gates. Each maps to roadmap phases 20–22.

### CI/CD Gates

- [ ] **GATE-01**: Maintainer can rely on push and pull request workflows to block merges when lint, typecheck, unit tests, or build fail
- [ ] **GATE-02**: Contributor can run the same quality gate command set locally as CI so failures reproduce before push

### Security Enforcement

- [ ] **SEC-01**: Contributor commit is blocked when staged changes contain detected secrets from `gitleaks` or `detect-secrets`
- [ ] **SEC-02**: Contributor can install or refresh pre-commit security hooks with one documented bootstrap command

### Test Baseline and Coverage

- [x] **TEST-01**: `apps/web` has a working Vitest setup that runs in CI
- [x] **TEST-02**: `apps/web` includes at least 5 baseline unit tests for core components or utilities
- [x] **TEST-03**: Coverage ratchet blocks CI when coverage falls below the locked baseline

### Database Operationalization

- [x] **DBOP-01**: Contributor can run one workspace command (for example `turbo db:migrate`) to provision or update development database schema from migrations
- [x] **DBOP-02**: CI integration-test flow provisions a database service and successfully runs migration command before integration tests

### LLM Test Cost Control

- [x] **COST-01**: Any LLM-assisted test path is disabled by default and runs only when explicitly requested with approved low-cost/local model profile

## Future Requirements

### Quality Observability

- **OBS-01**: Maintainer can view historical quality gate pass/fail trend by workflow and phase
- **OBS-02**: Maintainer can see test coverage trend over time in a lightweight dashboard

### Feature-Level Agentic Capabilities

- **AGCAP-01**: Agent telemetry and cost dashboard for milestone-level model usage analytics

## Out of Scope

| Feature                                             | Reason                                                                          |
| --------------------------------------------------- | ------------------------------------------------------------------------------- |
| Custom CI orchestration framework                   | Must use standard GitHub Actions templates from `.agent/skills/ci-cd-pipelines` |
| Premium-model-first automated test generation in CI | Cost control constraint requires low-cost/local-gated execution only            |
| Production database provisioning                    | v1.6 scope is development and integration-test operationalization               |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase    | Status   |
| ----------- | -------- | -------- |
| GATE-01     | Phase 20 | Pending  |
| GATE-02     | Phase 20 | Pending  |
| SEC-01      | Phase 20 | Pending  |
| SEC-02      | Phase 20 | Pending  |
| TEST-01     | Phase 21 | Complete |
| TEST-02     | Phase 21 | Complete |
| TEST-03     | Phase 21 | Complete |
| COST-01     | Phase 21 | Complete |
| DBOP-01     | Phase 22 | Complete |
| DBOP-02     | Phase 22 | Complete |

**Coverage:**

- v1.6 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0 ✓

---

_Requirements defined: 2026-02-24_
_Last updated: 2026-02-24 after v1.6 milestone definition_
