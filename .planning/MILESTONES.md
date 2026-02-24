# Milestones

## v1.0 MVP (Shipped: 2026-02-23)

**Phases completed:** 5 phases (0–4), 4 plans (Phase 4), 41 commits
**Timeline:** 2026-02-17 → 2026-02-23 (7 days)
**LOC:** ~60,775 (Markdown, JS, TS, JSON)

**Key accomplishments:**

- Complete 5-phase GSD methodology documentation with AGENTS.md reference guide
- Core skills library: Frontend (React/Next.js), Backend (FastAPI), Database (PostgreSQL), E2E testing (Playwright)
- GSD Workflow skill packaged with 12 helper scripts, reusable across projects
- DevOps skills: Docker/containerization, GitHub Actions CI/CD, cloud deployment (Vercel/AWS/Railway)
- Community infrastructure: CONTRIBUTING.md, CODE_OF_CONDUCT.md, GitHub issue templates, skill creation guide
- i18n implementation skill with next-i18next patterns, working Next.js example, translation workflow guides

**Archive:** `.planning/milestones/v1.0-ROADMAP.md`

---

## v1.1 Dogfooding (Shipped: 2026-02-24)

**Phases completed:** 6 phases (5–10), 14 plans, 33 commits
**Timeline:** 2026-02-23 → 2026-02-24 (2 days)
**Files changed:** 249 files (+24,137 / -10,832 lines)
**Git range:** dad66e3 (Phase 5 CI) → 219015a (Phase 10 summaries)

**Key accomplishments:**

- GitHub Actions CI pipeline live — push/PR triggers install → lint → type-check → test → build with branch protection
- Vitest test suite in `apps/web/` with coverage ratchet enforcing no regression between runs
- 12 oversized SKILL.md files modularized (534–1055 lines → 143–498 lines) with extracted `references/` guides
- VERIFICATION.md records created for all Phases 0–9 — full audit trail for methodology compliance
- pnpm workspace topology committed — fresh clones work without per-package install workarounds
- Developer onboarding automated via `scripts/setup-dev.sh` (prerequisites, pnpm install, pre-commit hook)

**Archive:** `.planning/milestones/v1.1-ROADMAP.md`

---


## v1.2 Foundation Skills (Shipped: 2026-02-24)

**Phases completed:** 1 phase (Phase 11), 3 plans
**Timeline:** 2026-02-24 → 2026-02-24 (1 day)
**Files changed:** 86 files (v1.1 tag → HEAD)
**LOC:** ~48,455 total in `.agent/skills/`
**Git range:** feat(11-01): rewrite SKILL.md → docs(phase-11): complete phase execution

**Key accomplishments:**
- Rewrote prompt-engineering skill to v1.2 depth — quick-start, numbered sections, applies-to schema for model-specific pattern tagging, 5-pattern anti-pattern catalogue with Before/After TypeScript code blocks, and golden-set evaluation architecture (eval.ts + 3 .md test cases)
- Rewrote auth-systems skill — Clerk quick-start, Better Auth as primary self-hosted alternative, side-by-side middleware patterns, DAL pattern with React cache(), CVE-2025-29927 documentation, Clerk webhook receiver for user lifecycle sync
- Fixed Anthropic SDK structured output API surface throughout prompt-engineering skill — replaced OpenAI-compatible `response_format` and `choices[0].message.parsed` with `output_config: { format: zodOutputFormat(...) }` and `.parsed_output`

**Scope note:** Scoped to Phase 11 (Foundation Skills) only. Phases 12–14 (AI/LLM Skills, Stripe Payments, Integration Review) deferred to v1.3.

**Archive:** `.planning/milestones/v1.2-ROADMAP.md`

---

