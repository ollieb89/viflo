# Requirements: Viflo

**Defined:** 2026-02-23
**Core Value:** A complete agentic dev environment you can install in one command — structured methodology, ready-made skills, and proven workflows so teams skip setup and ship faster.

## v1.1 Requirements

Milestone: **Dogfooding** — viflo applies its own methodology, CI templates, testing patterns, and security scanning to the viflo repository itself.

### CI — Active Continuous Integration

- [ ] **CI-01**: Repository has an active GitHub Actions workflow that runs on push and PR
- [ ] **CI-02**: CI pipeline enforces: install → lint → type-check → test → build in sequence
- [ ] **CI-03**: CI blocks merge when any pipeline step fails

### QUAL — Code Quality Enforcement

- [ ] **QUAL-01**: Pre-commit hooks run `gitleaks` and `detect-secrets` before every commit
- [ ] **QUAL-02**: A secret committed to the repo is blocked by the pre-commit hook
- [ ] **QUAL-03**: `apps/web/` has a Vitest test suite with ≥1 test per utility function
- [ ] **QUAL-04**: Vitest test suite runs in CI and fails the pipeline on test failure
- [ ] **QUAL-05**: A coverage ratchet script enforces that coverage percentage never decreases between runs

### CONTENT — Skill & Documentation Quality

- [ ] **CONTENT-01**: All SKILL.md files >500 lines are split into a primary SKILL.md + named reference sub-guides in a `references/` directory
- [ ] **CONTENT-02**: VERIFICATION.md exists for Phases 0, 1, 2, and 3 documenting what was built and verified
- [ ] **CONTENT-03**: A telemetry script logs each LLM call (timestamp, model, prompt_tokens, completion_tokens, task_success) and exports to CSV

## v1.0 Requirements (Validated)

All 14 v1.0 requirements shipped and validated 2026-02-23:

- ✓ **R1**: Complete 5-phase methodology documentation
- ✓ **R2**: Agent configuration structure (skills, rules, workflows)
- ✓ **R3**: GSD Workflow skill with helper scripts
- ✓ **R4**: Project templates (PROJECT, REQUIREMENTS, ROADMAP, PLAN)
- ✓ **R5**: AGENTS.md reference guide
- ✓ **R6**: Frontend development skill (React/Next.js)
- ✓ **R7**: Backend development skill (FastAPI)
- ✓ **R8**: Database design skill (PostgreSQL)
- ✓ **R9**: E2E testing skill (Playwright)
- ✓ **R10**: Example project templates
- ✓ **R11**: CI/CD integration guides
- ✓ **R12**: Docker/containerization skill
- ✓ **R13**: Cloud deployment skill (AWS/Vercel)
- ✓ **R14**: Multi-language support (i18n)

## Future Requirements (Deferred)

### v1.2+

- **INFRA-01**: Live PostgreSQL database provisioned and schema migrations run (G-05)
- **INFRA-02**: Integration tests run against a live FastAPI service (G-06)
- **OBS-01**: Cost dashboard visualizes cost-per-feature from telemetry data (G-12)
- **AUTO-01**: Automated prompt library extracts anti-patterns from failed task logs (G-09)
- **AUTO-02**: Level 3 escalation webhook sends alerts to Slack/Discord when NEEDS_HUMAN (G-11)

## Out of Scope

| Feature | Reason |
|---------|--------|
| IDE plugins/extensions | High complexity, not core to methodology value — revisit v1.2 |
| AI model training/fine-tuning | Out of viflo's domain |
| Proprietary/closed-source components | Contradicts tool-agnostic constraint |
| Live DB provisioning (G-05) | Requires runtime infrastructure decisions not ready for v1.1 |
| Cost dashboard UI (G-12) | Phase 5 complexity — defer until telemetry data exists |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CI-01 | Phase 5 | Pending |
| CI-02 | Phase 5 | Pending |
| CI-03 | Phase 5 | Pending |
| QUAL-01 | Phase 5 | Pending |
| QUAL-02 | Phase 5 | Pending |
| QUAL-03 | Phase 6 | Pending |
| QUAL-04 | Phase 6 | Pending |
| QUAL-05 | Phase 6 | Pending |
| CONTENT-01 | Phase 7 | Pending |
| CONTENT-02 | Phase 7 | Pending |
| CONTENT-03 | Phase 7 | Pending |

**Coverage:**
- v1.1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-23*
*Last updated: 2026-02-23 after v1.1 roadmap created*
