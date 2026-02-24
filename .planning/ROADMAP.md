# Viflo Roadmap

## Milestones

- ✅ **v1.0 MVP** — Phases 0–4 (shipped 2026-02-23) — [Archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Dogfooding** — Phases 5–10 (shipped 2026-02-24) — [Archive](milestones/v1.1-ROADMAP.md)
- ✅ **v1.2 Foundation Skills** — Phase 11 (shipped 2026-02-24) — [Archive](milestones/v1.2-ROADMAP.md)
- 🚧 **v1.3 Expert Skills** — Phases 12–15 (in progress)

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

### 🚧 v1.3 Expert Skills (In Progress)

**Milestone Goal:** Deliver Stripe Payments, RAG/Vector Search, and Agent Architecture skills at v1.2 depth standard, with full INDEX.md update, 500-line compliance verification, and cross-skill integration references.

- [x] **Phase 12: RAG / Vector Search** — Upgrade RAG skill to auth-systems depth with Quick Start, HNSW schema, hybrid search, and Gotchas (completed 2026-02-24)
- [x] **Phase 13: Agent Architecture** — Upgrade Agent skill to auth-systems depth with mandatory guardrails, typed handoffs, episodic memory, and streaming (completed 2026-02-24)
- [ ] **Phase 14: Stripe Payments** — Upgrade Stripe skill to auth-systems depth with Quick Start, raw-body webhook, subscription lifecycle, and Gotchas
- [ ] **Phase 15: Integration Review** — Update INDEX.md, verify 500-line compliance, and add cross-skill references across all three new skills

## Phase Details

### Phase 12: RAG / Vector Search
**Goal**: A developer can follow the RAG skill Quick Start, embed documents into pgvector, and retrieve them with hybrid search — all with production-safe schema (model version column, HNSW index) in place from the first commit.
**Depends on**: Phase 11 (database-design and postgresql skills shipped in v1.0/v1.1)
**Requirements**: RAG-01, RAG-02, RAG-03, RAG-04, RAG-05
**Success Criteria** (what must be TRUE):
  1. Developer can follow the Quick Start section and have a working embed-and-retrieve loop running against pgvector in under 15 minutes
  2. The SKILL.md schema includes `embedding_model_version` column and HNSW index creation — visible in the main body, not only in references/
  3. Developer can read about chunking strategies (fixed-size vs semantic, overlap rules, token budgets) and choose one with documented tradeoffs
  4. Developer can follow the hybrid search section and understand RRF fusion combining vector similarity and full-text search
  5. The Gotchas section names at least 3 pitfalls (embedding model drift, missing HNSW index, chunking pitfalls) each with explicit warning signs and fixes
**Plans**: 2 plans

Plans:
- [ ] 12-01-PLAN.md — Rewrite SKILL.md to auth-systems depth (Quick Start, Schema, Chunking, Hybrid Search, Evaluation, Gotchas)
- [ ] 12-02-PLAN.md — Create eval.ts runnable evaluation script; update references/ with HNSW schema and RRF CTE

---

### Phase 13: Agent Architecture
**Goal**: A developer can follow the Agent skill Quick Start, build a tool-using agent with guardrails, stream its output to a browser, and understand when agents are inappropriate — with loop depth limits present in every code example.
**Depends on**: Phase 12 (episodic memory cross-references pgvector patterns from RAG skill)
**Requirements**: AGENT-01, AGENT-02, AGENT-03, AGENT-04, AGENT-05
**Success Criteria** (what must be TRUE):
  1. Developer can follow the Quick Start and have a tool-using Claude agent running via Anthropic SDK in under 15 minutes
  2. Every agent code example in SKILL.md includes hard `MAX_TURNS` and `MAX_TOKENS_PER_RUN` constants — no example ships without guardrails
  3. Developer can follow the streaming section and wire SSE output from a FastAPI StreamingResponse to a Next.js client using Vercel AI SDK v6
  4. The Gotchas section names at least 3 pitfalls (runaway costs, untyped sub-agent handoffs, bag-of-agents error multiplication) with warning signs and fixes
  5. Developer can read a "When NOT to use agents" callout and make an informed build-vs-agent decision
**Plans**: 2 plans

Plans:
- [ ] 13-01-PLAN.md — Rewrite SKILL.md to auth-systems depth (Quick Start, Guardrails, Streaming, LangGraph, Memory/MCP, When NOT to use, Gotchas)
- [ ] 13-02-PLAN.md — Update references/ — multi-agent-patterns.md (LangGraph 1.x) and memory-orchestration.md (pgvector episodic memory)

---

### Phase 14: Stripe Payments
**Goal**: A developer can follow the Stripe skill Quick Start, accept a payment via Checkout, handle webhooks idempotently, and manage subscription lifecycle — without introducing PCI scope creep or webhook processing bugs.
**Depends on**: Phase 11 (auth-systems skill shipped in v1.2; independent of Phases 12–13)
**Requirements**: STRIPE-01, STRIPE-02, STRIPE-03, STRIPE-04, STRIPE-05
**Success Criteria** (what must be TRUE):
  1. Developer can follow the Quick Start and accept a one-time payment via Stripe Checkout in under 15 minutes with fewer than 30 lines of code
  2. The webhook handler section uses `await req.text()` (raw body) as the first code example — not a footnote — with `constructEvent()` signature verification shown
  3. The idempotency section shows atomic deduplication via `INSERT ... ON CONFLICT (stripe_event_id) DO NOTHING` in the main SKILL.md body
  4. Developer can read the subscription lifecycle section covering create, update, cancel, and status sync to the database for all four critical events
  5. The Gotchas section names at least 3 pitfalls (raw body destruction, non-atomic idempotency, PCI scope creep) with warning signs and fixes
**Plans**: 2 plans

Plans:
- [ ] 14-01-PLAN.md — Rewrite SKILL.md to auth-systems depth (Quick Start, Webhooks, Idempotency, Subscriptions, Customer Portal, Gotchas)
- [ ] 14-02-PLAN.md — Update references/ files to stripe v20 and Next.js 15 (webhook-patterns.md, subscription-patterns.md)

---

### Phase 15: Integration Review
**Goal**: All three new skills are discoverable via INDEX.md, cross-linked at integration seams, and verified compliant with the 500-line cap — so the v1.3 milestone leaves no orphaned references or discovery gaps.
**Depends on**: Phases 12, 13, 14 (all skill content must be final before index and cross-references are written)
**Requirements**: INFRA-01, INFRA-02, INFRA-03
**Success Criteria** (what must be TRUE):
  1. INDEX.md contains entries for all five skills touched in v1.2–v1.3 (prompt-engineering, auth-systems, rag-vector-search, agent-architecture, stripe-payments) with correct categories and descriptions
  2. All new and updated SKILL.md files are verified at or under 500 lines, with line counts recorded in VERIFICATION.md
  3. The RAG, Agent Architecture, and prompt-engineering skills each contain a cross-reference to the other skills at their integration seams (RAG ↔ Agent for episodic memory; Agent ↔ prompt-engineering for system prompt patterns)
**Plans**: TBD

Plans:
- [ ] 15-01: TBD

---

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
| 12. RAG / Vector Search | 2/2 | Complete    | 2026-02-24 | - |
| 13. Agent Architecture | 2/2 | Complete    | 2026-02-24 | - |
| 14. Stripe Payments | v1.3 | 0/TBD | Not started | - |
| 15. Integration Review | v1.3 | 0/TBD | Not started | - |
