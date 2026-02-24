# Phase 7: Content Hygiene — Discussion Context

## Overview

**Phase Goal**: Clean up oversized content, backfill verification records, and add telemetry logging
**Requirements**: CONTENT-01, CONTENT-02, CONTENT-03
**Depends on**: Phase 6 (Test Suite)

## Current State Analysis

### Oversized Skills (>500 lines)

| Skill                     | Lines | Excess | Action Needed                                    |
| ------------------------- | ----- | ------ | ------------------------------------------------ |
| nodejs-backend-patterns   | 1,055 | 555    | Move detailed patterns to `references/`          |
| typescript-advanced-types | 731   | 231    | Move type recipes to `references/`               |
| writing-skills            | 721   | 221    | Move templates/guides to `references/`           |
| error-handling-patterns   | 648   | 148    | Move language-specific sections to `references/` |
| monorepo-management       | 630   | 130    | Move tool-specific guides to `references/`       |
| microservices-patterns    | 602   | 72     | Move pattern details to `references/`            |
| fastapi-templates         | 573   | 73     | Move template examples to `references/`          |
| e2e-testing-patterns      | 551   | 51     | Move framework guides to `references/`           |
| code-review-excellence    | 544   | 44     | Move checklists to `references/`                 |
| debugging-strategies      | 543   | 43     | Move technique deep-dives to `references/`       |
| api-design-principles     | 534   | 34     | Move examples to `references/`                   |
| architecture-patterns     | 501   | 1      | Minor trim or reference extraction               |

**Total**: 12 skills need modularization

### VERIFICATION.md Backfill Needed

| Phase                    | Status  | Content to Capture                   |
| ------------------------ | ------- | ------------------------------------ |
| Phase 0: Foundation      | Missing | Repo structure, base configs, README |
| Phase 1: Core Skills     | Missing | First 10 skills created              |
| Phase 2: Extended Skills | Missing | Skills 11-25, examples               |
| Phase 3: DevOps          | Missing | Docker, CI/CD, deployment skills     |

### Telemetry Logging

**Requirements**:

- CSV-based storage (spreadsheet-compatible)
- Schema: timestamp, model, prompt_tokens, completion_tokens, task_success
- Append-only log
- At least one sample row demonstrating schema

## Questions for Discussion

### 1. Skill Modularization Strategy

**Q1**: For oversized skills, what content stays in SKILL.md vs moves to `references/`?

Options:

- A) SKILL.md = overview + quick reference only; everything else in `references/`
- B) SKILL.md = core content; move extended examples and edge cases to `references/`
- C) Keep SKILL.md as primary guide; extract only very large sections (>100 lines)

**Q2**: Should we create a standard `references/` structure?

Options:

- `references/` — flat file structure
- `references/guides/` — extended guides
- `references/examples/` — code examples
- `references/checklists/` — verification checklists

### 2. VERIFICATION.md Scope

**Q3**: What level of detail for historical VERIFICATION.md files?

Options:

- A) Summary only (what was built, key decisions, links to commits)
- B) Full verification checklist (what was verified, how, results)
- C) Hybrid (summary + key verification points)

**Q4**: Where to store VERIFICATION.md files?

Options:

- A) `.planning/verifications/phase-{N}-VERIFICATION.md`
- B) `.planning/phase-{N}/VERIFICATION.md`
- C) Root-level `VERIFICATION.md` with sections per phase

### 3. Telemetry Implementation

**Q5**: What triggers telemetry logging?

Options:

- A) Manual script invocation only (`scripts/log_telemetry.sh`)
- B) CI integration (GitHub Actions logs model usage)
- C) Wrapper script for LLM calls (if we had a unified LLM client)

**Q6**: Where to store telemetry CSV?

Options:

- A) `.telemetry/usage.csv` (git-ignored, manual aggregation)
- B) `.telemetry/usage.csv` (committed, append-only)
- C) `docs/telemetry/usage.csv` (committed, historical record)

## Proposed Plan Structure

Based on discussions, I expect **3 plans**:

1. **07-01-PLAN.md** — Skill Modularization (CONTENT-01)
   - Identify oversized skills
   - Create `references/` structure
   - Move excess content
   - Update SKILL.md with links

2. **07-02-PLAN.md** — VERIFICATION.md Backfill (CONTENT-02)
   - Create verification records for Phases 0-3
   - Document what was built
   - Capture key decisions

3. **07-03-PLAN.md** — Telemetry Logging (CONTENT-03)
   - Create telemetry CSV schema
   - Build logging script
   - Add sample data row
   - Document usage

## Success Criteria

1. No SKILL.md exceeds 500 lines
2. VERIFICATION.md exists for Phases 0-3
3. Telemetry CSV exists with sample row
4. All content remains functional after modularization

## Open Decisions

| Decision                 | Status  | Options                           |
| ------------------------ | ------- | --------------------------------- |
| Modularization approach  | Pending | A / B / C                         |
| References structure     | Pending | flat / guides+examples+checklists |
| VERIFICATION.md detail   | Pending | summary / full / hybrid           |
| VERIFICATION.md location | Pending | verifications/ / phase-N/ / root  |
| Telemetry trigger        | Pending | manual / CI / wrapper             |
| Telemetry storage        | Pending | gitignored / committed            |
