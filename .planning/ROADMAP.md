# Viflo Roadmap

## Milestones

- ✅ **v1.0 MVP** — Phases 0–4 (shipped 2026-02-23) — [Archive](.planning/milestones/v1.0-ROADMAP.md)
- 🚧 **v1.1 Dogfooding** — Phases 5–7 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 0–4) — SHIPPED 2026-02-23</summary>

- [x] Phase 0: Foundation — completed 2026-02-23
- [x] Phase 1: Core Skills Development — completed 2026-02-23
- [x] Phase 2: Extended Skills & Examples — completed 2026-02-23
- [x] Phase 3: DevOps & Deployment — completed 2026-02-23
- [x] Phase 4: Polish & Community (4/4 plans) — completed 2026-02-23

</details>

### 🚧 v1.1 Dogfooding (In Progress)

**Milestone Goal:** Apply viflo's own methodology, CI templates, testing patterns, and security scanning to the viflo repository itself — proving the toolkit with its own toolkit.

- [x] **Phase 5: CI & Security** - GitHub Actions pipeline active with pre-commit secret scanning ✅
- [ ] **Phase 6: Test Suite** - Vitest suite live in `apps/web/` with coverage ratchet enforced in CI
- [ ] **Phase 7: Content Hygiene** - Oversized skills modularized, VERIFICATION.md backfilled, telemetry logging in place

## Phase Details

### Phase 5: CI & Security

**Goal**: The viflo repo enforces quality on every commit and PR through automated CI and secret detection
**Depends on**: Phase 4 (v1.0 complete)
**Requirements**: CI-01, CI-02, CI-03, QUAL-01, QUAL-02
**Success Criteria** (what must be TRUE):

1. A push or opened PR triggers the GitHub Actions workflow automatically
2. The pipeline runs install → lint → type-check → test → build in sequence and fails fast when a step fails
3. A PR with a failing pipeline step cannot be merged (branch protection enforces it)
4. Committing a plaintext secret triggers the pre-commit hook and blocks the commit with an error message
5. The `.pre-commit-config.yaml` and workflow file exist in the repo and are the authoritative source of these rules
   **Plans**: 2 plans

Plans:

- [x] 05-01-PLAN.md — GitHub Actions CI workflow + branch protection (CI-01, CI-02, CI-03) ✅
- [x] 05-02-PLAN.md — Pre-commit secret scanning setup (QUAL-01, QUAL-02) ✅

### Phase 6: Test Suite

**Goal**: `apps/web/` has a live Vitest test suite that runs in CI and prevents coverage regression
**Depends on**: Phase 5
**Requirements**: QUAL-03, QUAL-04, QUAL-05
**Success Criteria** (what must be TRUE):

1. Running `pnpm test` in `apps/web/` executes the Vitest suite and reports pass/fail
2. Every utility function in `apps/web/` has at least one test covering its expected behavior
3. The CI pipeline runs the test suite and fails the build when any test fails
4. A coverage ratchet script records the current coverage baseline and fails if a subsequent run reports a lower percentage

**Plans**: 2 plans

Plans:

- [ ] 06-01-PLAN.md — Vitest test suite with utility functions and tests (QUAL-03, QUAL-04)
- [ ] 06-02-PLAN.md — Coverage ratchet script (QUAL-05)

### Phase 7: Content Hygiene

**Goal**: All oversized skill files are modularized, historical phases have VERIFICATION.md records, and LLM calls are logged to CSV
**Depends on**: Phase 5
**Requirements**: CONTENT-01, CONTENT-02, CONTENT-03
**Success Criteria** (what must be TRUE):

1. No SKILL.md file exceeds 500 lines; content moved to `references/` sub-guides linked from the primary file
2. VERIFICATION.md exists for each of Phases 0, 1, 2, and 3 documenting what was built and what was verified
3. A telemetry script exists that, when invoked, appends a structured row (timestamp, model, prompt_tokens, completion_tokens, task_success) to a CSV file
4. The telemetry CSV can be opened in any spreadsheet tool and shows at least one sample row demonstrating the schema
   **Plans**: TBD

## Progress

| Phase                      | Milestone | Plans Complete | Status      | Completed  |
| -------------------------- | --------- | -------------- | ----------- | ---------- |
| 0. Foundation              | v1.0      | —              | Complete    | 2026-02-23 |
| 1. Core Skills Development | v1.0      | —              | Complete    | 2026-02-23 |
| 2. Extended Skills         | v1.0      | —              | Complete    | 2026-02-23 |
| 3. DevOps & Deployment     | v1.0      | —              | Complete    | 2026-02-23 |
| 4. Polish & Community      | v1.0      | 4/4            | Complete    | 2026-02-23 |
| 5. CI & Security           | v1.1      | 2/2            | Complete    | 2026-02-23 |
| 6. Test Suite              | v1.1      | 0/2            | Planned     | -          |
| 7. Content Hygiene         | v1.1      | 0/TBD          | Not started | -          |
