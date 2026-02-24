# Project Research Summary

**Project:** viflo v1.3 Expert Skills
**Domain:** Skill documentation library — Stripe Payments, RAG/Vector Search, Agent Architecture
**Researched:** 2026-02-24
**Confidence:** HIGH

## Executive Summary

Viflo v1.3 is a documentation upgrade project, not a greenfield application. Three existing skill files (Stripe Payments, RAG/Vector Search, Agent Architecture) each sit at 80–92 lines with the four required depth-standard sections present but lacking the structural depth established by the auth-systems benchmark (437 lines). The work is expansion and restructuring: adding Quick Start sections, promoting the most critical patterns out of `references/` into SKILL.md, and adding named Gotchas sections with warning signs. Every skill already has the hard content in references/ files; the gap is surfacing it correctly in the main SKILL.md body so it appears at agent load time.

The recommended approach is dependency-ordered authoring within a strict 500-line cap: RAG first (no v1.3 dependencies; produces pgvector infrastructure the Agent skill will reference for episodic memory), then Agent Architecture (depends on prompt-engineering which shipped in v1.2; benefits from RAG being complete), then Stripe (independent of the AI stack; depends only on already-shipped auth-systems). All three skills have verified library versions and complete references/ content. The primary technical risks are documentation quality failures — missing the security-critical raw body webhook pattern, omitting mandatory agent guardrails, scope creep past 500 lines — rather than any infrastructure or integration uncertainty.

The highest-stakes pitfalls are categorically "invisible in development, catastrophic in production": Stripe's raw body requirement for webhook signature verification must appear in the first code example, not a footnote; agent examples must include hard `MAX_TURNS` and `MAX_TOKENS_PER_RUN` limits or risk runaway API bills documented at $47,000; RAG skills must include an `embedding_model_version` column in every schema or risk silent retrieval corruption on model upgrade. These are not edge cases — they are the industry's most commonly shipped mistakes in these three domains.

---

## Key Findings

### Recommended Stack

All library versions are confirmed against live npm/PyPI as of 2026-02-24. The full stack is compatible with the existing viflo environment (Next.js, React 19, TypeScript 5.7+, Python 3.11+, Node 20+, SQLAlchemy 2.0). No new managed services are required unless scale pushes RAG beyond ~50M vectors (use Pinecone then) or the project requires managed auth (Clerk is already in the v1.2 stack).

See `.planning/research/STACK.md` for full version compatibility matrix and installation commands.

**Core technologies:**

- `stripe` ^20.3.1 (Node) / ^14.3.0 (Python): Official SDK; handles checkout, subscriptions, webhook signature verification; pinned to API version `2026-01-28` in Node v20
- `@stripe/react-stripe-js` ^5.6.0: React 19-compatible Stripe Elements; use only when embedding checkout in-page — hosted Checkout is simpler for the majority of use cases
- `pgvector` ^0.4.2 (Python) / ^0.2.1 (Node): Vector search inside existing PostgreSQL; no extra managed service required; integrates with SQLAlchemy 2.0 via `pgvector.sqlalchemy.VECTOR`
- `text-embedding-3-small` (OpenAI, 1536 dims, ~$0.02/1M tokens): Default embedding model; must be pinned by version and stored alongside every vector row
- `@anthropic-ai/sdk` ^0.78.0: Direct Claude API client for TypeScript agents; use `client.messages.stream()` for streaming
- `anthropic` ^0.83.0 (Python): Claude client for FastAPI backends — use `AsyncAnthropic` exclusively; synchronous client blocks the event loop
- `ai` (Vercel AI SDK) ^6.x + `@ai-sdk/anthropic` ^1.x: Best DX for streaming agent UI in Next.js; handles tool execution, real-time tool result rendering, multi-provider switching
- `@langchain/langgraph` ^1.1.5: Stateful multi-agent graph orchestration; use only when the workflow has conditional branches and persistent state requirements — adds significant complexity for simpler pipelines

**Critical version notes:**

- `stripe` < 16 locks to deprecated API surfaces — use ^20
- `@stripe/stripe-js` < 8 type definitions misalign with stripe Node SDK v20 — use ^8.8.0
- `langchain` Python v0.1.x (pre-LCEL) is being deprecated in 2026 — use ^0.5.x with LCEL interface
- `text-embedding-ada-002` is deprecated — `text-embedding-3-small` outperforms it at lower cost

### Expected Features

The v1.3 work upgrades existing SKILL.md files to match the auth-systems depth standard (437 lines). The feature research defines exactly what each expansion must contain.

See `.planning/research/FEATURES.md` for full per-skill feature tables, dependency graph, and gap analysis.

**Must have (P1 — required to reach auth-systems depth standard):**

- Quick Start section for each skill: working code in <30 lines, immediately copy-pasteable, appearing before any other content
- Named Gotchas section with at minimum 3 pitfalls per skill, each with an explicit warning signs list
- Stripe: raw body webhook handler (`await req.text()`), idempotency via `stripe_events` table, all four critical events documented (`checkout.session.completed`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`), test/live key startup validation
- RAG: HNSW index creation in schema, `embedding_model_version` column in vector table, similarity threshold check in retrieval pipeline, chunking strategies plural (not fixed-size-only as the recommendation), retrieval evaluation section in main SKILL.md
- Agent: `max_turns` + `max_tokens` guardrails with code in every agent example, typed handoff schema interface, "When NOT to use agents" explicit callout, sub-agent context scoping pattern

**Should have (P2 — adds value without blowing 500-line budget):**

- Stripe: test card cheat-sheet table, grace period pattern summary promoted from references/, plan change proration summary
- RAG: hybrid search summary (vector + BM25 + RRF) promoted from references/, similarity threshold calibration guide
- Agent: Anthropic composable patterns overview (5 patterns, one paragraph each), model tier strategy (Opus for planning, Haiku/Sonnet for execution), MCP overview paragraph

**Defer to v1.4+:**

- Stripe: Connect/marketplace payments (own skill territory), usage-based metered billing deep dive (Stripe Meters API)
- RAG: Multimodal retrieval (images, audio), Agentic RAG as a distinct cross-skill topic
- Agent: Full LangGraph workflow patterns as a dedicated skill, MCP server implementation guide, streaming agent responses as a first-class topic

### Architecture Approach

The viflo skill system uses progressive disclosure: SKILL.md holds decision logic, quick-reference tables, and links (≤500 lines enforced); detail lives in `references/` and is loaded on demand when Claude determines it is needed. All three v1.3 skills already have complete `references/` files — the upgrade work is entirely in SKILL.md: promoting high-value content into the main body, adding structural sections, and updating cross-references.

See `.planning/research/ARCHITECTURE.md` for full directory layout, data flow diagrams, database schemas, integration patterns, and anti-patterns.

**Major components per skill:**

1. **Stripe integration:** Next.js billing pages + webhook route → FastAPI billing router + Stripe service → PostgreSQL `customers`, `subscriptions`, `processed_webhook_events` tables; Stripe Checkout keeps card data entirely off your servers
2. **RAG integration:** Next.js search UI → FastAPI ingest worker (background) + retrieval service + generation service → PostgreSQL `documents` + `document_chunks` (with `vector(1536)` column, tsvector column, HNSW index, GIN index for hybrid search)
3. **Agent integration:** Next.js chat UI (SSE stream reader) → FastAPI agent router + SSE streaming endpoint → LangGraph orchestrator + tool services → PostgreSQL `agent_runs`, `agent_messages`, `agent_memories` (reuses pgvector if RAG is installed — zero additional operational cost)

**Key architectural insight:** RAG and Agent share infrastructure. If pgvector is installed for RAG, the agent episodic memory layer reuses the same `vector(1536)` column pattern and HNSW index at no additional cost. This is the primary reason to build RAG before Agent Architecture.

**Firm build order (from dependency analysis):**

```
Phase 1: RAG / Vector Search
  — No v1.3 dependencies; extends only shipped postgresql + database-design skills
  — Produces pgvector + embedding pipeline that agent-architecture will reference

Phase 2: Agent Architecture
  — Depends on prompt-engineering (v1.2, shipped)
  — Benefits from RAG complete: episodic memory can reference pgvector patterns

Phase 3: Stripe Payments
  — Depends only on auth-systems (v1.2, shipped)
  — No dependency on AI stack; can be built in parallel with Phase 1 if staffed
```

**Files affected:** 3 SKILL.md upgrades + 4 existing skills gain forward-reference links (`INDEX.md`, `pci-compliance`, `postgresql`, `workflow-orchestration-patterns`)

### Critical Pitfalls

See `.planning/research/PITFALLS.md` for full descriptions, warning signs, recovery strategies, and a "Looks Done But Isn't" verification checklist.

1. **Stripe: `await req.json()` in webhook handler destroys raw body** — Stripe signature verification throws a cryptic error; developers spend hours debugging. Fix: always use `await req.text()` in Next.js App Router webhook handlers. No `export const config` needed (and that Pages Router config is silently ignored in App Router). This pattern must be the first code example in the webhook section, not a footnote.

2. **Stripe: No idempotency on webhook processing causes duplicate fulfillment** — Stripe retries for up to 72 hours; concurrent invocations without atomic deduplication cause double charges and duplicate subscription activations. Fix: `INSERT INTO stripe_events ... ON CONFLICT (stripe_event_id) DO NOTHING`; verify and return 200 immediately; process async from queue. Must be in main SKILL.md, not references/.

3. **RAG: Embedding model version mismatch silently corrupts retrieval** — Upgrading the embedding model makes all existing vectors meaningless; cosine similarity scores become noise with no runtime error; hallucinations follow. Fix: store `embedding_model_version` alongside every vector; assert match at query time; use blue/green index strategy on upgrade. The column must appear in the schema in the main SKILL.md, not just references/.

4. **Agent: No loop depth guard enables runaway API bills** — An agent that cannot resolve a tool failure loops indefinitely; documented real-world incidents have produced $47,000 bills. Fix: hard `MAX_TURNS` and `MAX_TOKENS_PER_RUN` constants in every agent code example in SKILL.md, with a circuit breaker after N consecutive tool failures.

5. **Agent: Untyped sub-agent handoffs cause context explosion and 17x error multiplication** — Passing full conversation history to sub-agents fills their context windows before they begin working; the "bag of agents" anti-pattern multiplies errors across agents rather than adding them. Fix: typed `AgentHandoff` TypeScript interface; sub-agents receive only task + required artifacts; supervisor/coordinator topology with no cycles.

---

## Implications for Roadmap

The three-skill upgrade has a clear phase structure driven by dependencies, shared infrastructure, and security risk profile. Each phase is a self-contained authoring unit.

### Phase 1: RAG / Vector Search Skill Upgrade

**Rationale:** No dependency on other v1.3 skills. Depends only on already-shipped `database-design` and `postgresql` skills. Producing the pgvector + embedding pipeline first means the Agent Architecture skill (Phase 2) can make concrete references to complete content rather than forward-referencing work in progress. The pgvector HNSW schema from this phase is also reused verbatim by the agent episodic memory layer.

**Delivers:** Upgraded `rag-vector-search/SKILL.md` at auth-systems depth (target 350–400 lines), with Quick Start, three named Gotchas, hybrid search summary and RAG prompt assembly promoted from references/, HNSW index in schema with filter-interaction notes, retrieval evaluation as a first-class section.

**Addresses (P1 features):** Quick Start, Gotchas section, embedding model mismatch as Gotcha #1 with bold warning, RAG prompt assembly visible in SKILL.md, HNSW index creation in schema.

**Avoids:** Embedding model drift (Pitfall 6), fixed-size chunking as the default recommendation (Pitfall 5), missing HNSW index causing sequential scans at scale (Pitfall 8), no retrieval evaluation layer (Pitfall 7).

**Research flag:** Standard patterns — skip `/gsd:research-phase`. pgvector, HNSW indexing, OpenAI embedding API, and hybrid search with RRF are well-documented with stable APIs. All versions verified 2026-02-24.

---

### Phase 2: Agent Architecture Skill Upgrade

**Rationale:** Depends on `prompt-engineering` (v1.2, shipped) and benefits significantly from RAG being complete (Phase 1). The episodic memory section can reference the pgvector patterns established in Phase 1 without forward-referencing. Agent Architecture is the highest-complexity skill and the one with the highest documentation risk — build it second with the RAG foundation in place.

**Delivers:** Upgraded `agent-architecture/SKILL.md` at auth-systems depth (target 350–400 lines), with Quick Start, mandatory guardrails section with code examples (loop depth guard as Gotcha #1 with cost warning), typed `AgentHandoff` interface, "When NOT to use agents" callout, Anthropic composable patterns overview, model tier strategy section.

**Addresses (P1 features):** Quick Start, Gotchas section, loop depth guard promoted from references/ to Gotcha #1, sub-agent context scoping pattern with code, "When NOT to use agents" explicit callout.

**Avoids:** Runaway API cost from no loop limit (Pitfall 9, $47k incident), context explosion and reasoning failure from full history forwarding (Pitfall 10), bag-of-agents 17x error multiplication (Pitfall 11).

**Research flag:** Partial research recommended. The core Anthropic tool-use loop and composable patterns are fully stable — no research needed. The MCP overview paragraph and LangGraph 1.1.5 checkpointing specifics may benefit from a focused research pass: LangGraph 1.0 shipped in October 2025 and some patterns around human-in-the-loop checkpointing may have shifted from 0.x. Validate before writing the multi-agent section.

---

### Phase 3: Stripe Payments Skill Upgrade

**Rationale:** Depends only on `auth-systems` (v1.2, shipped). Has no dependency on the AI stack. Could be built in parallel with Phase 1 if there are multiple authors — the research confirms no cross-dependency between Stripe and RAG. Building it last in a single-author scenario keeps payment concerns isolated from AI stack authoring.

**Delivers:** Upgraded `stripe-payments/SKILL.md` at auth-systems depth (target 350–400 lines), with Quick Start (zero-to-checkout in <20 lines), three named Gotchas (raw body, test/live key mismatch, checkout session expiry), test card cheat-sheet table, Stripe CLI testing block promoted from references/, and idempotent webhook pattern visible in main SKILL.md.

**Addresses (P1 features):** Quick Start, Gotchas section, webhook idempotency pattern in SKILL.md body, Stripe CLI testing block visible, checkout + subscription side-by-side comparison.

**Avoids:** Webhook body parsing failure (Pitfall 1 — the #1 Stripe production mistake), duplicate fulfillment from missing idempotency (Pitfall 2), event ordering assumptions breaking subscription state machine (Pitfall 3), test keys silently shipped to production (Pitfall 4).

**Research flag:** No research needed — skip `/gsd:research-phase`. Stripe's documentation is industry-leading and among the most thoroughly documented payment integration topics. Stack versions verified from npm/PyPI on 2026-02-24.

---

### Phase 4: Index and Cross-Reference Update

**Rationale:** After all three skills are upgraded, `INDEX.md` and four existing skills need forward-reference links. This is a coordination and QA phase — not content creation — but it is mandatory. Skipping it leaves the skill discovery layer incomplete and the integration seams between skills undocumented.

**Delivers:** Updated `INDEX.md` with "Payments" and "AI / LLM" categories (three new rows); `pci-compliance`, `postgresql`, and `workflow-orchestration-patterns` skills gain forward-reference links; cross-reference audit confirms each skill pair mentions the other at integration seams; 500-line check on all three new SKILL.md files.

**Avoids:** Integration cross-reference gap discovered post-release (auth + Stripe integration gap pattern from v1.2; agent + RAG integration seam); INDEX.md not updated (verification checklist item in PITFALLS.md).

**Research flag:** No research needed. This is internal documentation work against a first-party codebase with a well-understood architecture. Use the "Looks Done But Isn't" checklist from `.planning/research/PITFALLS.md` as the verification gate.

---

### Phase Ordering Rationale

- **RAG before Agent:** The agent skill's episodic memory section references pgvector patterns established in Phase 1. Building in dependency order ensures all cross-references point to complete, accurate content.
- **Stripe last (or parallel):** Stripe is architecturally isolated from the AI stack. There is no benefit to building Stripe before RAG or Agent from a content quality perspective. In a single-author scenario, last is simplest; with multiple authors, parallel with Phase 1 is valid.
- **500-line discipline is a phase-level concern:** The pitfalls research documents scope creep past 500 lines as a recurring v1.x issue. Plan the `references/` split in the outline at the start of each phase — not after the body is written.
- **Index update after content is final:** Updating INDEX.md last ensures all skill frontmatter (name, description, when-to-use) is finalized before the discovery table is written. Mid-authoring updates risk the description drifting from the final scope.

---

### Research Flags

Phases likely needing deeper research during planning:

- **Phase 2 (Agent Architecture — partial):** LangGraph 1.1.5 checkpointing patterns and human-in-the-loop integration. LangGraph 1.0 shipped in October 2025; some workflow patterns may have shifted between 0.x and 1.0. The core Anthropic tool-use loop is fully stable and needs no research.

Phases with standard patterns (skip `/gsd:research-phase`):

- **Phase 1 (RAG):** pgvector, HNSW indexing, OpenAI embedding API, and hybrid search with RRF fusion are all stable and well-documented with multiple corroborating sources. Versions verified.
- **Phase 3 (Stripe):** Stripe webhook and subscription patterns are the most thoroughly documented payment integration topic in existence. Versions verified. No ambiguity.
- **Phase 4 (Index update):** Internal documentation QA against a first-party codebase. No external research required.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All library versions verified against live npm/PyPI on 2026-02-24. Full version compatibility with existing viflo stack (React 19, Node 20+, Python 3.11+, SQLAlchemy 2.0, TypeScript 5.7+) confirmed. |
| Features | HIGH | Gap analysis grounded in direct codebase inspection of existing skills against the 437-line auth-systems benchmark. Scope boundaries are specific, measurable, and well-reasoned. |
| Architecture | HIGH | Stripe and RAG architecture sourced from official documentation; Agent architecture patterns sourced from official Anthropic docs + high-confidence secondary sources. Skill system architecture from direct first-party codebase inspection. |
| Pitfalls | HIGH (Stripe) / MEDIUM (RAG, Agent) | Stripe pitfalls corroborated by official Stripe docs, Next.js issue tracker, and multiple independent community sources. RAG and Agent pitfalls are well-sourced but the field is evolving — some calibration figures (62% → 84% hybrid search precision) are from specific benchmarks that may not generalize. |

**Overall confidence:** HIGH

### Gaps to Address

- **LangGraph 1.0+ pattern stability:** LangGraph 1.0 shipped October 2025 as the first stable release. Validate LangGraph 1.1.5 patterns for stateful checkpointing and human-in-the-loop before writing the Agent skill's multi-agent section. The core tool-use loop is stable.
- **Hybrid search RRF precision figure:** The 62% → 84% retrieval precision improvement figure is from a 2025 benchmark on a specific corpus (DEV Community, lpossamai). Present this as a "typical improvement seen in practice" rather than a guarantee. Calibration guide in the RAG skill should instruct developers to validate on their own query set.
- **Agent MCP overview scope:** Vercel AI SDK v6 supports MCP natively. The scope of the MCP overview paragraph in the Agent skill is undefined. Keep it to one paragraph with an external link unless the roadmapper decides to expand — MCP server implementation is explicitly deferred to v1.4+.

---

## Sources

### Primary (HIGH confidence)

- Official `stripe` npm changelog + npmjs.com — v20.3.1 confirmed current
- PyPI stripe — v14.3.0 confirmed, released 2026-01-28
- Stripe Webhook Docs (docs.stripe.com/webhooks) — raw body requirement, `constructEvent()` 5-minute signature window
- Stripe Idempotency Docs (docs.stripe.com) — auto-retry with idempotency keys in Node SDK v17+
- Stripe API Keys best practices (docs.stripe.com/keys-best-practices) — test vs. live key management
- pgvector GitHub (github.com/pgvector/pgvector) — HNSW index recommendation, scale guidance, filter interaction issues
- pgvector-python GitHub — SQLAlchemy 2.0 `VECTOR` type, `mapped_column` usage
- OpenAI text-embedding-3 docs — 1536 dims, $0.02/1M tokens, `dimensions` parameter
- Vercel AI SDK 6 announcement (vercel.com/blog/ai-sdk-6) — v6 stable, MCP support, tool execution
- LangGraph JS docs — TypeScript StateGraph pattern, checkpointing verified
- Anthropic "Building Effective Agents" — orchestrator/subagent model, context scoping
- Direct inspection of `.agent/skills/` codebase — skill system architecture (first-party)
- Next.js issue #54090 (github.com/vercel/next.js) — `export const config` unsupported in App Router

### Secondary (MEDIUM confidence)

- npmjs.com package pages — @stripe/stripe-js v8.8.0, @stripe/react-stripe-js v5.6.0, pgvector Node 0.2.1, @anthropic-ai/sdk 0.78.0, @langchain/langgraph 1.1.5, ai v6.0.x confirmed
- instaclustr.com — pgvector 2026 guide; scale thresholds (~50M vector limit for pgvector)
- DEV Community (lpossamai) — hybrid search with pgvector + RRF; 62% → 84% precision figure from 2025 benchmark
- DEV Community (belazy) — Stripe webhook race condition; queue architecture pattern
- Stigg blog — Stripe webhook best practices; event ordering caveat; signature window
- Crunchy Data blog — HNSW indexes with pgvector; query planner behavior with combined WHERE filters
- Toward Data Science — "17x error trap" bag of agents anti-pattern; error multiplication vs. addition
- Medium (Micheal-Lanham) — $47k agent cost runaway incident; token guardrail patterns
- factory.ai — context rot research on 18 LLMs; effective context window 30–50% of advertised limit
- Google Developers Blog — architecting efficient context-aware multi-agent framework
- langwatch.ai — LangGraph 1.0 October 2025 release date confirmed
- DataCamp — CrewAI vs LangGraph 2026 comparison; LangGraph recommended for stateful conditional workflows
- Redis blog (2026) — RAG at scale production patterns; embedding drift monitoring
- DEV Community (kuldeep_paul) — Ten failure modes of RAG; context position bias, citation hallucination

### Tertiary (LOW confidence — validate during authoring)

- Weaviate blog — chunking strategies; 9% recall gap for fixed-size vs. semantic chunking (benchmark-specific)
- mastra.ai — @mastra/core v1.6.0 as TypeScript-first alternative to LangGraph; noted for evaluation but not yet widely adopted

---

*Research completed: 2026-02-24*
*Ready for roadmap: yes*
