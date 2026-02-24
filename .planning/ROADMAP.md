# Viflo Roadmap

## Milestones

- ✅ **v1.0 MVP** — Phases 0–4 (shipped 2026-02-23) — [Archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Dogfooding** — Phases 5–10 (shipped 2026-02-24) — [Archive](milestones/v1.1-ROADMAP.md)
- 🚧 **v1.2 Skills Expansion** — Phases 11–14 (in progress)

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

### 🚧 v1.2 Skills Expansion (In Progress)

**Milestone Goal:** Expand the skills library with five high-demand domain skills — Auth Systems, Prompt Engineering, RAG/Vector Search, Agent Architecture, and Stripe Payments — authored in dependency order with a final integration review pass.

- [ ] **Phase 11: Foundation Skills** - Prompt Engineering + Auth Systems (no inter-dependencies; downstream skills depend on both)
- [ ] **Phase 12: AI/LLM Skills** - RAG/Vector Search + Agent Architecture (agent depends on prompt engineering from Phase 11)
- [ ] **Phase 13: Stripe Payments** - Full payments skill (depends on auth-systems from Phase 11 for user identity handoff)
- [ ] **Phase 14: Integration Review** - Cross-skill audit, INDEX.md completion, 500-line compliance check

## Phase Details

### Phase 11: Foundation Skills
**Goal**: Two complete, shippable skills are published — developers can follow structured guidance for Prompt Engineering and Auth Systems without needing any other v1.2 skill to be complete.
**Depends on**: Phase 10 (committed codebase baseline)
**Requirements**: PROMPT-01, PROMPT-02, PROMPT-03, PROMPT-04, PROMPT-05, AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06
**Success Criteria** (what must be TRUE):
  1. Developer can write a structured prompt using role/context/task/output anatomy with model-appropriate technique selection (instruction-tuned vs reasoning models tagged in frontmatter)
  2. Developer can apply chain-of-thought, few-shot, and output format specification patterns and evaluate them against a golden set without an external platform
  3. Developer can follow the Clerk quick-start to add sign-up, sign-in, and protected routes to a Next.js App Router app (proxy.ts middleware)
  4. Developer can configure Better Auth as a self-hosted alternative with the same protected-route pattern and OAuth provider wiring (GitHub, Google)
  5. Skill documents the App Router cache pitfall and DAL re-validation pattern, and covers the Clerk webhook receiver for user lifecycle sync
**Plans**: 2 plans

Plans:
- [ ] 11-01-PLAN.md — Upgrade prompt-engineering skill: quick-start, numbered sections, applies-to schema, Before/After anti-patterns, golden-set eval architecture
- [ ] 11-02-PLAN.md — Upgrade auth-systems skill: Better Auth replaces Auth.js, quick-start, side-by-side middleware, webhook handler, DAL/cache pitfall

### Phase 12: AI/LLM Skills
**Goal**: The complete AI/LLM skill cluster is published — developers can implement semantic search pipelines with pgvector and build multi-step agent workflows using the Claude API.
**Depends on**: Phase 11 (prompt engineering complete; agent skill references it)
**Requirements**: RAG-01, RAG-02, RAG-03, RAG-04, RAG-05, AGENT-01, AGENT-02, AGENT-03, AGENT-04, AGENT-05
**Success Criteria** (what must be TRUE):
  1. Developer can implement the full embed → store → query loop using pgvector, including chunking strategy with appropriate chunk size and overlap
  2. Developer can implement hybrid search (pgvector cosine + PostgreSQL tsvector BM25 + RRF merge) and evaluate retrieval quality against a golden test set
  3. Developer can implement the perceive→reason→act agent loop with Claude API using the orchestrator–worker pattern for multi-step task decomposition
  4. Developer can wire tool/function calling with error handling and partial failure recovery, and understands memory taxonomy (in-context, external, procedural)
  5. Skill enforces embedding model consistency and chunk observability, and documents token budget awareness to prevent runaway agent loops
**Plans**: TBD

### Phase 13: Stripe Payments
**Goal**: A complete payments skill is published — developers can implement one-time checkout, subscription billing, and webhook handling for standard SaaS billing without referencing external docs for the core patterns.
**Depends on**: Phase 11 (auth-systems complete; Auth→Stripe handoff cross-references it)
**Requirements**: STRIPE-01, STRIPE-02, STRIPE-03, STRIPE-04, STRIPE-05
**Success Criteria** (what must be TRUE):
  1. Developer can create a Stripe Checkout session for one-time and subscription payments and set up subscription management with the Stripe customer portal
  2. Developer can implement an idempotent webhook handler with event.id deduplication and async processing (acknowledge fast, process asynchronously)
  3. Developer can test webhooks locally using Stripe CLI and understands the test card cheat sheet
  4. Skill documents the Auth→Stripe handoff (signup → Customer → stripe_customer_id → subscription gate) so neither skill has a cross-skill integration gap
**Plans**: TBD

### Phase 14: Integration Review
**Goal**: All five v1.2 skills are coherent as a set — cross-skill integration gaps are closed, INDEX.md is complete with new categories, and every SKILL.md file passes the ≤500 line constraint.
**Depends on**: Phase 13 (all five skills authored)
**Requirements**: INFRA-01, INFRA-02
**Success Criteria** (what must be TRUE):
  1. INDEX.md contains new Payments and AI/LLM categories with all 5 new skill entries and Quick Selection Guide entries for each
  2. All 5 new SKILL.md files measure ≤500 lines (CONTENT-01 constraint from v1.1 satisfied)
  3. Auth and Stripe skills each contain a "Cross-skill integration" section documenting the user identity → Stripe Customer handoff seam
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
| 11. Foundation Skills | v1.2 | 0/TBD | Not started | - |
| 12. AI/LLM Skills | v1.2 | 0/TBD | Not started | - |
| 13. Stripe Payments | v1.2 | 0/TBD | Not started | - |
| 14. Integration Review | v1.2 | 0/TBD | Not started | - |
