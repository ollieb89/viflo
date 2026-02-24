# Viflo: Universal Agentic Development Environment

## Current Milestone: v1.2 Skills Expansion

**Goal:** Expand the skills library with high-demand domain integration and AI/LLM pattern skills

**Target features:**
- Auth systems skill (Clerk + Auth.js/NextAuth — session handling, protected routes, OAuth)
- Stripe payments skill (checkout, subscriptions, webhooks, billing patterns)
- RAG / vector search skill (embedding pipelines, pgvector/Pinecone, retrieval patterns)
- Agent architecture skill (multi-agent systems, handoffs, memory, orchestration)
- Prompt engineering skill (templates, evaluation, iteration workflows, anti-patterns)

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

### Active

- [ ] Auth systems skill covering Clerk and Auth.js/NextAuth patterns (AUTH-01)
- [ ] Stripe payments skill covering checkout, subscriptions, and webhooks (STRIPE-01)
- [ ] RAG / vector search skill covering embedding pipelines and retrieval patterns (RAG-01)
- [ ] Agent architecture skill covering multi-agent systems and orchestration (AGENT-01)
- [ ] Prompt engineering skill covering templates, evaluation, and iteration workflows (PROMPT-01)

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

Tech stack: Claude Code / GSD methodology, Markdown-first, Node.js tooling, pnpm workspace.
All 11 v1.1 requirements delivered with audit-verified committed state.

Known tech debt:
- Makefile `make setup` target (09-CONTEXT.md specified Makefile; execution used `scripts/setup-dev.sh` instead — different mechanism, same function)
- 07-VERIFICATION.md checked off telemetry commit before verifying against `git ls-files` — future verifications should use `git ls-files` to confirm committed state

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

---

_Last updated: 2026-02-24 — v1.2 milestone started_
