# Requirements: Viflo v1.4

**Defined:** 2026-02-24
**Core Value:** A complete agentic dev environment you can install in one command — structured methodology, ready-made skills, and proven workflows so teams skip setup and ship faster.

## v1.4 Requirements

Requirements for the v1.4 Project Tooling milestone. Phases start from 15 (continuing from v1.3's Phase 14).

### Integration Review

- [ ] **INFRA-01**: INDEX.md is updated with entries for prompt-engineering, auth-systems, rag-vector-search, agent-architecture, and stripe-payments skills
- [ ] **INFRA-02**: All new/updated SKILL.md files are verified ≤500 lines with line counts recorded in VERIFICATION.md
- [ ] **INFRA-03**: Cross-reference links are added between RAG, Agent Architecture, and prompt-engineering skills at their integration seams

### viflo init CLI

- [ ] **INIT-01**: User can run `viflo init --minimal` to write a CLAUDE.md sentinel block with `@` import lines for all viflo skills
- [ ] **INIT-02**: User can run `viflo init --minimal` to write/merge `.claude/settings.json` with safe default `permissions.allow` entries
- [ ] **INIT-03**: User can run `viflo init --full` to scaffold a `.planning/` directory with GSD stub files (PROJECT.md, STATE.md, ROADMAP.md, config.json) — skips files that already exist
- [ ] **INIT-04**: User can run `viflo init --full` to write a starter CLAUDE.md template when no CLAUDE.md exists in the project
- [ ] **INIT-05**: Re-running `viflo init` on an existing project does not overwrite customized content (CLAUDE.md outside sentinel block, existing `.planning/` files, existing settings.json entries)
- [ ] **INIT-06**: User can run `viflo init --dry-run` to preview all file actions with resolved absolute paths without writing any files
- [ ] **INIT-07**: Each file action emits a labelled result (`created` / `updated` / `skipped` / `merged`) with the resolved absolute path

## Future Requirements

### CLI Enhancements (v1.5+)

- **INIT-08**: Stack-aware skill selection — detect project stack and inject a curated skill subset
- **INIT-09**: Interactive wizard mode — guided setup for new users
- **INIT-10**: npm publish / global install — run `viflo init` without cloning the repo

### Platform

- **PLAT-01**: WSL2 explicit detection and path resolution for Windows Claude Code installs
- **PLAT-02**: `packages/cli/` TypeScript workspace with compilation pipeline for npm registry publish

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full project scaffolding (package.json, git init, Makefile) | viflo init is config injection only, not a project bootstrapper |
| Semantic CLAUDE.md merge (section matching) | Fragile and unpredictable; sentinel block is the correct approach |
| Writing to `~/.claude/settings.json` (user scope) | Active Claude Code bug #5140 makes user-scope permissions unreliable; write project scope only |
| Auto-installing viflo if absent | Circular dependency; fail fast with install instructions |
| Skill selection wizard in v1.4 | Default to importing all skills; users trim manually |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 15 | Pending |
| INFRA-02 | Phase 15 | Pending |
| INFRA-03 | Phase 15 | Pending |
| INIT-01 | TBD | Pending |
| INIT-02 | TBD | Pending |
| INIT-03 | TBD | Pending |
| INIT-04 | TBD | Pending |
| INIT-05 | TBD | Pending |
| INIT-06 | TBD | Pending |
| INIT-07 | TBD | Pending |

**Coverage:**
- v1.4 requirements: 10 total
- Mapped to phases: 3 (INFRA-01–03 → Phase 15)
- Unmapped: 7 ⚠️ (roadmapper will assign)

---
*Requirements defined: 2026-02-24*
*Last updated: 2026-02-24 after initial definition*
