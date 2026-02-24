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


## v1.3 Expert Skills (Shipped: 2026-02-24)

**Phases completed:** 3 phases (12–14), 6 plans, 28 commits
**Timeline:** 2026-02-17 → 2026-02-24 (7 days)
**Files changed:** 32 files, ~5,509 net lines added
**Git range:** feat(12-01): rewrite SKILL.md → fix(tech-debt): resolve v1.0 audit documentation accuracy items

**Key accomplishments:**
- RAG/Vector Search SKILL.md expanded 92 → 416 lines: HNSW schema, RRF hybrid search SQL inline, 4 named Gotchas, and runnable eval.ts with recall@5/MRR golden-set evaluation
- RAG reference files updated: embedding-pipelines.md to `document_chunks` schema with HNSW+GIN indexes; retrieval-patterns.md with RRF CTE as recommended Option B
- Agent Architecture SKILL.md expanded 81 → 498 lines: MAX_TURNS/MAX_TOKENS_PER_RUN guardrails in every example, FastAPI SSE streaming to Next.js AI SDK v6, LangGraph 1.x, episodic memory via pgvector, MCP overview
- Agent Architecture references updated: LangGraph 1.x PostgresSaver + interrupt(), pgvector `agent_episodes` schema with embedding_model_version cross-referencing RAG skill
- Stripe Payments SKILL.md expanded 91 → 363 lines: raw-body webhook with `await req.text()`, atomic `ON CONFLICT` idempotency, four-event subscription lifecycle, Customer Portal, trial periods, 5 Gotchas
- Stripe reference files updated to stripe@20.3.1 / 2026-01-28.clover / Next.js 15: atomic SQL idempotency replacing Prisma P2002, all four subscription events in standalone handler

**Known gaps (deferred to v1.4):**
- INFRA-01: INDEX.md not updated with new skills
- INFRA-02: 500-line compliance not formally verified for new skills
- INFRA-03: Cross-skill references between RAG ↔ Agent ↔ prompt-engineering not added

**Archive:** `.planning/milestones/v1.3-ROADMAP.md`

---


## v1.4 Project Tooling (Shipped: 2026-02-24)

**Phases completed:** 2 phases (15–16), 5 plans
**Timeline:** 2026-02-24 → 2026-02-24 (1 day)
**Files changed:** 31 files (+3,165 / −25 lines)
**Git range:** feat(15-01): update INDEX.md → feat(16-02): create writers unit tests

**Key accomplishments:**
- Updated INDEX.md with intro paragraph and accurate v1.4 skill descriptions (Better Auth for auth-systems, HNSW hybrid search for rag-vector-search)
- Added bidirectional See Also cross-reference links across rag-vector-search, agent-architecture, and prompt-engineering skills at three named integration seams
- Created VERIFICATION.md with post-edit wc -l audit for all five v1.4 SKILL.md files (4/5 within 500-line limit; agent-architecture 503 lines accepted per locked decision)
- `bin/lib/paths.cjs` — deterministic `__dirname`-based repo root and target-path resolution with no process.cwd() dependency
- `bin/lib/writers.cjs` — idempotent CLAUDE.md sentinel merge (indexOf+slice) and settings.json deep-merge (Set dedup, existing-first order)
- Vitest CJS test suite with 23 passing tests for paths.cjs and writers.cjs, wired as `pnpm run test:cli`; INIT-05 idempotency regression gate active

**Scope note:** Scoped to Phases 15–16 (Integration Review + CLI Foundation). Phases 17–19 (viflo init --minimal, --full, polish) deferred to v1.5.

**Known tech debt:**
- writeIfChanged helper not exported from writers.cjs — Phase 17+ must extend writers.cjs or duplicate idempotency logic
- resolveViFloRoot() exported and tested but not yet called within bin/ tree — correctly deferred to Phase 17+
- ROADMAP.md Phase 17 success criterion still uses stale sentinel format (viflo:start/end); must update before Phase 17 planning
- research/ files reference stale viflo:start/viflo:end format — update before Phase 17 research begins

**Archive:** `.planning/milestones/v1.4-ROADMAP.md`

---

