# Viflo: Universal Agentic Development Environment

## Current State: v1.6 Planning

`viflo init` CLI is fully functional. Developers can wire any project to viflo in one command:
- `viflo init --minimal` — CLAUDE.md sentinel + `.claude/settings.json` permissions
- `viflo init --full` — also scaffolds `.planning/` with GSD stubs + starter CLAUDE.md template
- `viflo init --dry-run` — filesystem-safe preview of all file actions with resolved absolute paths
- Unified labelled output (`created`/`updated`/`skipped`/`merged`) with absolute paths
- `npx viflo` / `pnpm exec viflo` invocable via `package.json` bin field

## Current Milestone: v1.6 Infrastructure Hardening & Quality Gates

**Goal:** Operationalize and harden repository-level quality/safety gates so contributors cannot merge insecure or unverified changes.

**Target features:**
- CI/CD gate hardening (live GitHub Actions with enforced lint/typecheck/test/build checks)
- Security enforcement hardening (pre-commit secret scanning + consistent bootstrap/install path)
- Testing reliability hardening (web Vitest baseline + coverage ratchet enforcement)
- Database operationalization for integration testing (single migration command + CI integration flow)
- Cost-controlled LLM testing gates (optional and explicitly restricted to low-cost/local profiles)

**Next step:** `/gsd-plan-phase 20` after roadmap approval.

## What This Is

Viflo is a comprehensive development methodology and toolchain that standardizes and accelerates agentic software development. It ships as 35+ reusable skill packages, a structured 5-phase lifecycle, and GSD workflow tooling for hybrid AI-human development teams. With v1.1, viflo applies its own methodology to itself — the repo has live CI, Vitest test coverage, pre-commit security scanning, and modular skill documentation, proving the toolkit by dogfooding it.

## Core Value

A complete agentic dev environment you can install in one command — structured methodology, ready-made skills, and proven workflows so teams skip setup and ship faster.

## Goals

1. **Standardize Methodology**: Provide a consistent approach to AI-assisted development across projects
2. **Accelerate Delivery**: Reduce setup time and decision fatigue with pre-defined workflows
3. **Improve Quality**: Built-in planning, verification, and best practices ensure high-quality output
4. **Enable Collaboration**: Clear documentation and artifacts facilitate human-AI teamwork

## Requirements

### Validated

- ✓ Complete 5-phase methodology documentation (R1) — v1.0
- ✓ Agent configuration structure (skills, rules, workflows) (R2) — v1.0
- ✓ GSD Workflow skill with helper scripts (R3) — v1.0
- ✓ Project templates (PROJECT, REQUIREMENTS, ROADMAP, PLAN) (R4) — v1.0
- ✓ AGENTS.md reference guide (R5) — v1.0
- ✓ Frontend development skill (React/Next.js) (R6) — v1.0
- ✓ Backend development skill (FastAPI) (R7) — v1.0
- ✓ Database design skill (PostgreSQL) (R8) — v1.0
- ✓ E2E testing skill (Playwright) (R9) — v1.0
- ✓ Example project templates (R10) — v1.0
- ✓ CI/CD integration guides (R11) — v1.0
- ✓ Docker/containerization skill (R12) — v1.0
- ✓ Cloud deployment skill (AWS/Vercel) (R13) — v1.0
- ✓ Multi-language support (i18n) (R14) — v1.0
- ✓ CI pipeline active — blocks bad merges (CI-01, CI-02, CI-03) — v1.1
- ✓ Pre-commit hooks enforce secret detection via gitleaks + detect-secrets (QUAL-01, QUAL-02) — v1.1
- ✓ `apps/web/` has live Vitest test suite enforced in CI (QUAL-03, QUAL-04) — v1.1
- ✓ Coverage ratchet prevents regression (QUAL-05) — v1.1
- ✓ Telemetry script logs LLM calls (timestamp, model, tokens, success) to CSV (CONTENT-03) — v1.1
- ✓ All SKILL.md files ≤500 lines — oversized content extracted to `references/` (CONTENT-01) — v1.1
- ✓ VERIFICATION.md exists for Phases 0–9 (CONTENT-02) — v1.1
- ✓ Prompt engineering skill at v1.2 depth — quick-start, applies-to schema, 5-pattern anti-pattern catalogue, golden-set eval architecture (PROMPT-01–05) — v1.2
- ✓ Auth systems skill at v1.2 depth — Clerk quick-start, Better Auth self-hosted path, DAL pattern, CVE-2025-29927 docs, webhook receiver (AUTH-01–06) — v1.2
- ✓ RAG/Vector Search skill at v1.3 depth — HNSW schema, RRF hybrid search SQL, 4 Gotchas, runnable eval.ts with recall@5/MRR (RAG-01–05) — v1.3
- ✓ Agent Architecture skill at v1.3 depth — MAX_TURNS guardrails in every example, FastAPI SSE streaming, LangGraph 1.x, pgvector episodic memory, MCP overview (AGENT-01–05) — v1.3
- ✓ Stripe Payments skill at v1.3 depth — raw-body webhooks, atomic ON CONFLICT idempotency, four-event subscription lifecycle, Customer Portal, trial periods (STRIPE-01–05) — v1.3
- ✓ INDEX.md updated with intro paragraph and accurate descriptions for all five v1.4 skills (INFRA-01) — v1.4
- ✓ All v1.4 SKILL.md files verified ≤500 lines with VERIFICATION.md audit table (INFRA-02) — v1.4 (agent-architecture 503 lines, accepted per decision)
- ✓ Bidirectional See Also cross-references across RAG ↔ Agent Architecture ↔ prompt-engineering at three named seams (INFRA-03) — v1.4
- ✓ `viflo init` library layer idempotent — CLAUDE.md sentinel merge and settings.json deep-merge safe to re-run (INIT-05) — v1.4
- ✓ `viflo init --minimal` writes CLAUDE.md sentinel block with `@` import lines for all viflo skills (INIT-01) — v1.5
- ✓ `viflo init --minimal` writes/merges `.claude/settings.json` with safe default `permissions.allow` entries (INIT-02) — v1.5
- ✓ `viflo init --full` scaffolds `.planning/` directory with GSD stub files — skips files that already exist (INIT-03) — v1.5
- ✓ `viflo init --full` writes starter CLAUDE.md template when no CLAUDE.md exists (INIT-04) — v1.5
- ✓ `viflo init --dry-run` previews all file actions with resolved absolute paths without writing any files (INIT-06) — v1.5
- ✓ Each file action emits a labelled result (`created`/`updated`/`skipped`/`merged`) with resolved absolute path (INIT-07) — v1.5
- ✓ `package.json` bin wiring — `npx viflo` / `pnpm exec viflo` invocable (INIT-08) — v1.5

### Active

- [ ] GATE-01: Maintainer can rely on push/PR checks to block merges when lint, typecheck, unit tests, or build fail
- [ ] SEC-01: Contributor commits are blocked locally when staged changes contain detected secrets
- [ ] TEST-01: `apps/web` test suite and coverage ratchet are enforced in CI, preventing regression
- [ ] DBOP-01: Contributor can run one workspace command to provision/update development DB schema for integration testing
- [ ] COST-01: Optional LLM test paths run only behind explicit low-cost/local model gating

### Out of Scope

- AI model training/fine-tuning
- Proprietary/closed-source components
- Non-agentic development workflows
- IDE plugins/extensions (high complexity, revisit v1.2)
- Live PostgreSQL provisioning (INFRA-01) — requires runtime infrastructure decisions
- Cost dashboard UI (OBS-01) — defer until telemetry data exists
- Automated prompt anti-pattern library (AUTO-01)
- Level 3 escalation webhooks (AUTO-02)

## Constraints

- **Documentation-First**: All methodology must be thoroughly documented
- **Tool Agnostic**: Support multiple AI coding assistants (Claude Code, Kimi CLI, etc.)
- **Modular**: Skills and rules should be composable and reusable
- **Practical**: Real-world tested workflows, not theoretical
- All skills must follow SKILL.md specification
- Scripts must work on macOS, Linux, and WSL
- Documentation must be AI and human readable
- No external dependencies beyond standard tools

## Tech Stack

| Layer           | Technology                            |
| --------------- | ------------------------------------- |
| Documentation   | Markdown                              |
| Package Manager | pnpm (>=10.0.0) with workspace        |
| Structure       | Monorepo (TurboRepo)                  |
| Languages       | TypeScript 5.7+, Python 3.11+         |
| Frontend        | Next.js 16, React 19, Tailwind CSS v4 |
| Backend         | FastAPI, SQLAlchemy 2.0               |
| Database        | PostgreSQL, Redis                     |
| CI              | GitHub Actions                        |
| Testing         | Vitest (unit), coverage ratchet       |
| Security        | gitleaks, detect-secrets (pre-commit) |
| Telemetry       | CSV-based LLM call logging            |

## Target Users

- **Solo Developers**: Using AI for rapid prototyping and production
- **Small Teams**: 2-10 person teams adopting AI-assisted development
- **AI-Native Agencies**: Teams building exclusively with AI tools

## Context

Shipped v1.0 with 35 skill packages, ~60,775 LOC across Markdown/JS/TS/JSON (7 days, 5 phases).
Shipped v1.1 with CI pipeline, Vitest coverage, skill modularization, and VERIFICATION.md audit trail (2 days, 6 phases, 33 commits).
Shipped v1.2 (Foundation Skills) with prompt-engineering and auth-systems rewrites at v1.2 depth standard (1 day, 1 phase, 3 plans).
Shipped v1.3 (Expert Skills) with RAG/Vector Search, Agent Architecture, and Stripe Payments skills at v1.3 depth standard (7 days, 3 phases, 6 plans, 28 commits).
Shipped v1.4 (Project Tooling) with integration review (INDEX.md, VERIFICATION.md, See Also links) and CLI library layer (paths.cjs, writers.cjs, 23 Vitest tests) (1 day, 2 phases, 5 plans, +3,165 lines).
Shipped v1.5 (viflo init CLI) with `viflo init --minimal/--full/--dry-run`, unified labelled output, and `npx viflo` bin wiring (1 day, 3 phases, 6 plans, 574 CJS LOC, 55/55 tests).

Tech stack: Claude Code / GSD methodology, Markdown-first, Node.js/CommonJS CLI tooling, pnpm workspace, Vitest.
~53,000 LOC estimated in `.agent/skills/` (v1.3 baseline ~48,455 + v1.4 additions).
CLI: 574 lines of CJS (bin/viflo.cjs, bin/lib/writers.cjs, bin/lib/skills.cjs, bin/lib/paths.cjs).

Known tech debt:
- Makefile `make setup` target (09-CONTEXT.md specified Makefile; execution used `scripts/setup-dev.sh` instead — different mechanism, same function)
- 07-VERIFICATION.md checked off telemetry commit before verifying against `git ls-files` — future verifications should use `git ls-files` to confirm committed state
- agent-architecture SKILL.md is 503 lines (over 500-line limit) — accepted per locked Phase 15 decision; 4/5 skills within limit is the accepted outcome
- User-scope `~/.claude/settings.json` writes deferred — Claude Code bug #5140 not resolved; project-scope only for v1.5

## Key Decisions

| Date       | Decision                          | Outcome                                       |
| ---------- | --------------------------------- | --------------------------------------------- |
| 2026-02-23 | Adopt GSD methodology             | ✓ Good — structured workflow proved effective |
| 2026-02-23 | Create gsd-workflow skill         | ✓ Good — reusable across projects             |
| 2026-02-23 | Use Python for helper scripts     | ✓ Good — portable, no compilation needed      |
| 2026-02-23 | Use Contributor Covenant 2.1      | ✓ Good — industry standard                    |
| 2026-02-23 | next-i18next over next-intl       | ✓ Good — Pages Router compatibility           |
| 2026-02-23 | Native Intl API for formatting    | ✓ Good — zero dependencies                    |
| 2026-02-23 | Namespace translations by domain  | ✓ Good — stable under refactoring             |
| 2026-02-23 | triggers: as standard frontmatter | ✓ Good — consistent across 35 skills          |
| 2026-02-23 | INDEX.md at .agent/skills/        | ✓ Good — central skill discovery              |
| 2026-02-23 | Defer oversized SKILL.md refactor | ✓ Resolved — completed in v1.1 Phase 7/8      |
| 2026-02-23 | Vitest for web unit testing       | ✓ Good — fast, TypeScript-native, CI-friendly |
| 2026-02-23 | pnpm workspace topology           | ✓ Good — single install, filter-based CI      |
| 2026-02-23 | gitleaks + detect-secrets         | ✓ Good — dual scanner catches more patterns   |
| 2026-02-23 | CSV for telemetry output          | ✓ Good — zero-dep, spreadsheet-compatible     |
| 2026-02-24 | setup-dev.sh instead of Makefile  | ⚠️ Revisit — CONTEXT.md specified Makefile    |
| 2026-02-24 | Phase 10 gap-closure pattern      | ✓ Good — explicit commit-and-verify phase prevents disk/committed drift |
| 2026-02-24 | Better Auth replaces Auth.js      | ✓ Good — Auth.js is maintenance-mode since Sept 2025; Better Auth is the active project |
| 2026-02-24 | applies-to frontmatter schema     | ✓ Good — model-specific technique tagging proven useful in prompt-engineering skill |
| 2026-02-24 | Scope v1.2 to Phase 11 only       | ✓ Good — foundation skills independently valuable; AI/LLM + Stripe deferred to v1.3 |
| 2026-02-24 | HNSW as default pgvector index     | ✓ Good — no training step, better recall than IVFFlat; pattern adopted in both RAG and Agent skills |
| 2026-02-24 | RRF rank-based hybrid search fusion | ✓ Good — no score normalization needed; SQL inline in SKILL.md body (not only in references/) |
| 2026-02-24 | MAX_TURNS/MAX_TOKENS_PER_RUN as named constants | ✓ Good — guardrails in every agent example; grep-able, explicit, non-optional |
| 2026-02-24 | Next.js API route proxy for SSE streaming | ✓ Good — keeps API key server-side, avoids CORS, simpler than direct FastAPI-to-useChat bridge |
| 2026-02-24 | pg.Pool raw SQL for Stripe idempotency | ✓ Good — atomic ON CONFLICT DO NOTHING preferred over Prisma P2002 try/catch; consistent across SKILL.md and references/ |
| 2026-02-24 | Defer Phase 15 (INFRA) to v1.4    | ✓ Good — 15/18 requirements satisfied; INDEX.md/compliance/cross-refs are housekeeping, not blockers |
| 2026-02-24 | Scope v1.4 to Phases 15–16 only    | ✓ Good — Phases 17–19 (viflo init CLI) deferred to v1.5; library layer ships independently as a clean foundation |
| 2026-02-24 | Sentinel format: `<!-- BEGIN VIFLO -->` / `<!-- END VIFLO -->` | ✓ Good — HTML comment delimiters safe in any Markdown context; indexOf+slice avoids regex escaping pitfalls |
| 2026-02-24 | resolveViFloRoot() uses `__dirname` not `process.cwd()` | ✓ Good — deterministic regardless of where node is invoked from |
| 2026-02-24 | existing-first Set spread for array dedup in settings.json merge | ✓ Good — stable ordering preserves user entries at front |
| 2026-02-24 | vitest installed at workspace root (not apps/web) | ✓ Good — `pnpm exec vitest` resolves from repo root; web app tests unaffected |
| 2026-02-24 | Real temp directories (fs.mkdtempSync) for writers tests | ✓ Good — real I/O is what the tests are designed to verify; filesystem mocking would defeat the purpose |
| 2026-02-24 | agent-architecture 503 lines accepted, trimming ruled out | ✓ Good — See Also section addition was post-baseline; 4/5 within limit is valid pass state |
| 2026-02-24 | Named seam annotations in See Also links (not just destination) | ✓ Good — "episodic memory pattern (pgvector-backed recall)" tells readers what they'll find, not just where |
| 2026-02-24 | scanSkills accepts rootDir explicitly — caller passes resolveViFloRoot() | ✓ Good — pure function, easy to test with any temp directory, decoupled from install path |
| 2026-02-24 | writePlanningScaffold uses fs.existsSync (skip-if-exists) not writeIfChanged | ✓ Good — planning files preserve user edits; writers.cjs skip-if-unchanged semantics differ by file type |
| 2026-02-24 | `merged` label at CLI call-site (not in writers) — writers return `updated`, CLI maps to `merged` | ✓ Good — writers.cjs stays single-responsibility; CLI applies semantic context |
| 2026-02-24 | No shebang required — npm bin wiring uses node implicitly for .cjs files | ✓ Good — bin field alone sufficient; fewer moving parts |
| 2026-02-24 | User-scope ~/.claude/settings.json writes deferred (bug #5140) | — Pending — re-evaluate at v1.6 planning |

---

_Last updated: 2026-02-24 after v1.6 milestone kickoff_
