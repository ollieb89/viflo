# Viflo: Universal Agentic Development Environment

## What This Is

Viflo is a comprehensive development methodology and toolchain that standardizes and accelerates agentic software development. It ships as 35 reusable skill packages, a structured 5-phase lifecycle, and GSD workflow tooling for hybrid AI-human development teams.

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

### Active

<!-- v1.1 Dogfooding — viflo applies its own methodology to itself -->

- [ ] CI pipeline is active and blocks bad merges (G-01)
- [ ] Pre-commit hooks enforce secret detection (G-02)
- [ ] `apps/web/` has a live Vitest test suite enforced in CI (G-03)
- [ ] Coverage ratchet prevents regression (G-04)
- [ ] Basic telemetry logs LLM calls (tokens, model, success) to CSV (G-07)
- [ ] Oversized SKILL.md files (>500 lines) are modularized with reference sub-guides (G-08)
- [ ] VERIFICATION.md exists for Phases 0–3 (G-10)

### Out of Scope

- AI model training/fine-tuning
- Proprietary/closed-source components
- Non-agentic development workflows
- IDE plugins/extensions (revisit in v1.1)
- Oversized SKILL.md refactoring >500 lines (deferred to v1.1)

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
| Package Manager | pnpm (>=10.0.0)                       |
| Structure       | Monorepo (TurboRepo)                  |
| Languages       | TypeScript 5.7+, Python 3.11+         |
| Frontend        | Next.js 16, React 19, Tailwind CSS v4 |
| Backend         | FastAPI, SQLAlchemy 2.0               |
| Database        | PostgreSQL, Redis                     |

## Target Users

- **Solo Developers**: Using AI for rapid prototyping and production
- **Small Teams**: 2-10 person teams adopting AI-assisted development
- **AI-Native Agencies**: Teams building exclusively with AI tools

## Context

Shipped v1.0 with 35 skill packages, ~60,775 LOC across Markdown/JS/TS/JSON.
Tech stack: Claude Code / GSD methodology, Markdown-first, Node.js tooling.
All 14 v1.0 requirements delivered in 7 days across 5 phases, 41 commits.

Known tech debt:

- SKILL.md files >500 lines need modular reference file structure
- VERIFICATION.md missing for Phases 0–3 (predated GSD plan tracking)

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
| 2026-02-23 | Defer oversized SKILL.md refactor | ⚠️ Revisit — needs dedicated v1.1 plan        |

## Current Milestone: v1.1 Dogfooding

**Goal:** Apply viflo's own methodology, CI templates, testing patterns, and security scanning to the viflo repository itself — proving the toolkit with its own toolkit.

**Target features:**

- Active GitHub Actions CI pipeline (using ci-cd-pipelines skill output)
- Pre-commit hooks with secret detection (gitleaks/detect-secrets)
- Live Vitest test suite for `apps/web/` with coverage ratchet
- Basic LLM telemetry logging to CSV
- Modularized SKILL.md files for skills >500 lines
- VERIFICATION.md backfill for Phases 0–3

---

_Last updated: 2026-02-23 after v1.1 milestone started_
