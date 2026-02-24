# Viflo: Universal Agentic Development Environment

## Current Milestone: v1.4 (Planning)

**Goal:** TBD — likely Integration Review (Phase 15: INDEX.md update, 500-line compliance verification, cross-skill references) plus any new skill work.

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

### Active

- [ ] INDEX.md updated with prompt-engineering, auth-systems, rag-vector-search, agent-architecture, stripe-payments (INFRA-01)
- [ ] All new/updated SKILL.md files verified ≤500 lines with line counts in VERIFICATION.md (INFRA-02)
- [ ] Cross-references between RAG ↔ Agent Architecture ↔ prompt-engineering skills at integration seams (INFRA-03)

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
Shipped v1.3 (Expert Skills) with RAG/Vector Search, Agent Architecture, and Stripe Payments skills at v1.2 depth standard (7 days, 3 phases, 6 plans, 28 commits).

Tech stack: Claude Code / GSD methodology, Markdown-first, Node.js tooling, pnpm workspace.
~48,455 LOC in `.agent/skills/` (pre-v1.3 baseline; v1.3 added ~5,500 net lines).

Known tech debt:
- Makefile `make setup` target (09-CONTEXT.md specified Makefile; execution used `scripts/setup-dev.sh` instead — different mechanism, same function)
- 07-VERIFICATION.md checked off telemetry commit before verifying against `git ls-files` — future verifications should use `git ls-files` to confirm committed state
- INDEX.md not yet updated with v1.2/v1.3 skills (INFRA-01 — deferred to v1.4)
- 500-line compliance not formally verified for v1.3 skills (INFRA-02 — deferred to v1.4)
- Cross-skill references between RAG ↔ Agent ↔ prompt-engineering not added (INFRA-03 — deferred to v1.4)

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

---

_Last updated: 2026-02-24 after v1.3 milestone completion_
