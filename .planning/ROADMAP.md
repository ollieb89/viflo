# Viflo Roadmap

## Milestones

- ✅ **v1.0 MVP** — Phases 0–4 (shipped 2026-02-23) — [Archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Dogfooding** — Phases 5–10 (shipped 2026-02-24) — [Archive](milestones/v1.1-ROADMAP.md)
- ✅ **v1.2 Foundation Skills** — Phase 11 (shipped 2026-02-24) — [Archive](milestones/v1.2-ROADMAP.md)
- ✅ **v1.3 Expert Skills** — Phases 12–14 (shipped 2026-02-24) — [Archive](milestones/v1.3-ROADMAP.md)
- 📋 **v1.4 Project Tooling** — Phases 15–19 (in progress)

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

### 📋 v1.4 Project Tooling (Phases 15–19)

- [x] **Phase 15: Integration Review** — Update INDEX.md, verify 500-line compliance, and add cross-skill references across all new skills (3 plans) (completed 2026-02-24)
- [ ] **Phase 16: CLI Foundation** — Path utilities and write primitives with Vitest unit tests; idempotency built in from the start
- [ ] **Phase 17: Minimal Mode** — bin/viflo.cjs entry point + --minimal flag end-to-end (CLAUDE.md stanza + settings.json)
- [ ] **Phase 18: Full Mode** — --full flag with .planning/ scaffold and starter CLAUDE.md template
- [ ] **Phase 19: Polish** — --dry-run flag, labelled per-file output, and package.json bin wiring

## Phase Details

### Phase 15: Integration Review
**Goal**: The skill library is coherent, discoverable, and cross-referenced — closing all housekeeping debt from v1.3
**Depends on**: Nothing (first phase of v1.4; all skill content is final)
**Requirements**: INFRA-01, INFRA-02, INFRA-03
**Success Criteria** (what must be TRUE):
  1. INDEX.md lists prompt-engineering, auth-systems, rag-vector-search, agent-architecture, and stripe-payments with accurate one-line descriptions
  2. VERIFICATION.md records the line count for every new/updated SKILL.md and each count is confirmed ≤500
  3. The RAG skill links to Agent Architecture at the episodic memory seam; Agent Architecture links back to RAG at the pgvector pattern seam; both link to prompt-engineering at the system-prompt design seam
**Plans**: 3 plans

Plans:
- [ ] 15-01-PLAN.md — Update INDEX.md with accurate v1.4 skill descriptions and intro paragraph (INFRA-01)
- [ ] 15-02-PLAN.md — Add See Also cross-reference sections to rag-vector-search, agent-architecture, and prompt-engineering SKILL.md files (INFRA-03)
- [ ] 15-03-PLAN.md — Create VERIFICATION.md with post-edit line counts for all five v1.4 skills (INFRA-02)

### Phase 16: CLI Foundation
**Goal**: Safe, tested path utilities and write primitives exist so all later CLI phases can build on a correct foundation
**Depends on**: Phase 15
**Requirements**: INIT-05
**Success Criteria** (what must be TRUE):
  1. `bin/lib/paths.cjs` exports functions that resolve viflo root via `__dirname` and target-project paths via an explicit `cwd` parameter — no `~` literals anywhere in path construction
  2. `bin/lib/writers.cjs` exports a CLAUDE.md sentinel-aware merge function and a settings.json JSON merge function with `Set`-based array deduplication
  3. Vitest unit tests for `paths.cjs` and `writers.cjs` pass in CI — tests mock `os.homedir()` and run from a temp directory outside the viflo repo
  4. Re-running any writer function on already-written output produces identical file contents and emits a skipped/unchanged signal rather than re-writing
**Plans**: 2 plans

Plans:
- [ ] 16-01-PLAN.md — Create bin/lib/paths.cjs and bin/lib/writers.cjs library modules (INIT-05)
- [ ] 16-02-PLAN.md — Create Vitest test suite for paths and writers, wire test:cli script (INIT-05)

### Phase 17: Minimal Mode
**Goal**: A developer can run `viflo init --minimal` in any project and get CLAUDE.md skill imports and safe Claude Code permissions wired in one command
**Depends on**: Phase 16
**Requirements**: INIT-01, INIT-02
**Success Criteria** (what must be TRUE):
  1. Running `viflo init --minimal` in a project without CLAUDE.md creates CLAUDE.md containing a `<!-- viflo:start -->` / `<!-- viflo:end -->` sentinel block with `@` import lines for all viflo skills
  2. Running `viflo init --minimal` creates or merges `.claude/settings.json` with safe default `permissions.allow` entries — existing entries in the file are preserved
  3. Running `viflo init --minimal` a second time on a project that already has the sentinel block and settings entries completes without modifying any file content
**Plans**: TBD

### Phase 18: Full Mode
**Goal**: A developer starting a new project can run `viflo init --full` and immediately have both viflo skill imports and a GSD planning scaffold ready to use
**Depends on**: Phase 17
**Requirements**: INIT-03, INIT-04
**Success Criteria** (what must be TRUE):
  1. Running `viflo init --full` in an empty project creates `.planning/` with stub files for PROJECT.md, STATE.md, ROADMAP.md, and config.json
  2. Running `viflo init --full` when `.planning/` already contains customized files skips each existing file individually — no existing content is overwritten
  3. Running `viflo init --full` in a project with no CLAUDE.md creates a starter CLAUDE.md template; running it where CLAUDE.md already exists does not replace or alter the file outside the sentinel block
**Plans**: TBD

### Phase 19: Polish
**Goal**: The CLI is fully wired as an executable, previews its actions safely, and communicates every file outcome clearly
**Depends on**: Phase 18
**Requirements**: INIT-06, INIT-07
**Success Criteria** (what must be TRUE):
  1. Running `viflo init --dry-run` (with any flag combination) prints every file action with its resolved absolute path and exits without writing, creating, or modifying any file
  2. Every file action in a real run emits a labelled result (`created`, `updated`, `skipped`, or `merged`) with the resolved absolute path on stdout
  3. `package.json` has a `"bin": { "viflo": "bin/viflo.cjs" }` field so the CLI is invocable via `npx` or a local `pnpm exec viflo` call from the repo
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 0. Foundation | v1.0 | — | Complete | 2026-02-23 |
| 1. Core Skills Development | v1.0 | — | Complete | 2026-02-23 |
| 2. Extended Skills | v1.0 | — | Complete | 2026-02-23 |
| 3. DevOps & Deployment | v1.0 | — | Complete | 2026-02-23 |
| 4. Polish & Community | v1.0 | 4/4 | Complete | 2026-02-23 |
| 5. CI & Security | v1.1 | 2/2 | Complete | 2026-02-23 |
| 6. Test Suite | v1.1 | 2/2 | Complete | 2026-02-23 |
| 7. Content Hygiene | v1.1 | 3/3 | Complete | 2026-02-23 |
| 8. Verification Closure | v1.1 | 2/2 | Complete | 2026-02-23 |
| 9. Workspace Tooling | v1.1 | 2/2 | Complete | 2026-02-24 |
| 10. Commit & Verify | v1.1 | 3/3 | Complete | 2026-02-24 |
| 11. Foundation Skills | v1.2 | 3/3 | Complete | 2026-02-24 |
| 12. RAG / Vector Search | v1.3 | 2/2 | Complete | 2026-02-24 |
| 13. Agent Architecture | v1.3 | 2/2 | Complete | 2026-02-24 |
| 14. Stripe Payments | v1.3 | 2/2 | Complete | 2026-02-24 |
| 15. Integration Review | 3/3 | Complete    | 2026-02-24 | - |
| 16. CLI Foundation | 1/2 | In Progress|  | - |
| 17. Minimal Mode | v1.4 | 0/TBD | Not started | - |
| 18. Full Mode | v1.4 | 0/TBD | Not started | - |
| 19. Polish | v1.4 | 0/TBD | Not started | - |
