# Project Research Summary

**Project:** viflo v1.2 Skills Expansion
**Domain:** Skill file library — Auth, Stripe, RAG/Vector Search, Agent Architecture, Prompt Engineering
**Researched:** 2026-02-24
**Confidence:** HIGH (stack verified against live npm/PyPI; architecture from direct codebase inspection)

## Executive Summary

viflo v1.2 adds five new skill domains to an established skill file system. These are not product features — they are documentation modules (SKILL.md + references/) that an AI coding assistant loads at task time. The challenge is not building software but authoring high-quality, scoped, correctly ordered skill files that fit within the existing architecture constraints (≤500 lines per SKILL.md, progressive disclosure via references/, no @ syntax for cross-references, flat reference directory structure).

The recommended approach is dependency-ordered authoring: prompt-engineering and auth-systems first (foundation skills with no inter-dependencies), then rag-vector-search and agent-architecture (agent depends on prompt engineering), then stripe-payments last (depends on auth-systems for user identity). All five skills have well-understood stack requirements with verified library versions. The primary technical risks are documentation quality failures — incorrect library recommendations, missing idempotency patterns, scope creep — rather than infrastructure or integration uncertainty.

The most critical risk is the Auth.js ecosystem shift: the Auth.js team joined Better Auth in September 2025, making Auth.js maintenance-mode. The auth-systems skill must lead with Clerk (managed) and Better Auth (self-hosted) rather than Auth.js v5. A secondary systemic risk is cross-skill integration gaps: Auth and Stripe must explicitly document the user identity → Stripe Customer handoff, and Agent must document how to pass auth context through tool calls. Both gaps are predictable and must be addressed in a final integration review phase, not discovered after individual skills ship.

## Key Findings

### Recommended Stack

All library versions are confirmed against live npm/PyPI as of 2026-02-24. The stack is fully compatible with the existing viflo environment (Next.js 16, React 19, TypeScript 5.7+, Python 3.11+, Node 20+, SQLAlchemy 2.0).

See `.planning/research/STACK.md` for full version compatibility matrix and installation commands.

**Core technologies:**

- `@clerk/nextjs` ^6.38.0: Managed auth — fastest path to production for SaaS, ships MFA and org management out of the box
- `next-auth@beta` (v5): Self-hosted auth — use when full data ownership is required; widely used in production despite beta tag
- `stripe` ^20.3.1 + `@stripe/react-stripe-js` ^5.6.0: Official Stripe SDK pair — server-side API client + React Elements for PCI-compliant checkout UI
- `pgvector` (Python ^0.4.2 / Node ^0.2.1): Vector search inside existing PostgreSQL — no extra managed service required for ≤50M vectors
- `@anthropic-ai/sdk` ^0.78.0 + `ai` (Vercel) ^6.0.97: Direct Claude API + streaming UI layer for Next.js agent interfaces
- `@langchain/langgraph` ^1.1.5: Stateful multi-agent graph orchestration — use only for complex workflows with explicit state transitions
- `anthropic` Python ^0.83.0: Async Claude client for FastAPI backends; use `AsyncAnthropic` — synchronous client blocks the event loop

**Critical version notes:**

- Auth.js v4 is unmaintained — must use v5 (`next-auth@beta`) or Better Auth for new projects
- `@clerk/nextjs` < v6 / Core 1 is deprecated — use ^6 only
- `stripe` < 16 locks to outdated API surfaces — use ^20
- Next.js 16 renames `middleware.ts` → `proxy.ts`; Clerk's `clerkMiddleware()` must live there

### Expected Features

See `.planning/research/FEATURES.md` for full feature tables per skill.

**Must have (table stakes — required for each skill to be useful):**

- Auth: Clerk quick-start for App Router, Auth.js v5 setup, protected routes via proxy.ts, OAuth provider wiring, session access in server components
- Stripe: Checkout session creation, subscription setup with Billing, webhook receiver with signature verification, idempotent webhook handler (dedup by event.id), customer portal
- RAG: Full embed → store → query loop, pgvector schema and index setup, cosine similarity query, chunking strategy with overlap, embedding model consistency rule
- Agent: Core perceive→reason→act loop, tool/function calling pattern, orchestrator–worker pattern, memory taxonomy, handoff pattern, guardrails
- Prompt: Prompt anatomy (role/context/task/output), system vs user vs prefill mechanics, few-shot examples, chain-of-thought, output format specification, prompt versioning in files

**Should have (differentiators that elevate the skill above raw docs):**

- Auth: App Router cache pitfall for authenticated content (leaks user data across sessions), DAL re-validation pattern, Clerk webhook receiver for user lifecycle sync
- Stripe: Async webhook processing pattern (acknowledge fast, process asynchronously), Stripe CLI local testing workflow, test card cheat sheet
- RAG: Hybrid search (vector + BM25 RRF), retrieval evaluation with golden test set, observability pattern (log retrieved chunks per LLM call)
- Agent: Anthropic's 6 composable patterns, MCP protocol overview, failure budget / partial failure handling, token budget awareness
- Prompt: Anti-pattern catalogue (top 5), golden set evaluation without a platform, LLM-as-judge pattern, prompt injection awareness

**Defer to v1.3+:**

- Auth: Full RBAC library integration (CASL), SAML/enterprise SSO, multi-tenancy/org management deep dive
- Stripe: Connect/marketplace payments, invoicing API deep dive, Stripe Tax
- RAG: Multimodal retrieval (images/audio), GraphRAG/knowledge graphs, fine-tuned embedding models
- Agent: Full LangGraph workflow patterns skill, autonomous agents without human oversight
- Prompt: Automated evaluation CI pipeline, red-teaming infrastructure, multimodal prompting

### Architecture Approach

The viflo skill system uses progressive disclosure: SKILL.md holds only decision logic, quick-reference tables, and links (≤500 lines enforced); detail lives in `references/` and is loaded on demand. Each new skill follows the established pattern of one SKILL.md per domain with 3 reference files covering major sub-topics or provider variants. INDEX.md must be updated to add three new categories (Payments, AI/LLM) and update the Security category.

See `.planning/research/ARCHITECTURE.md` for full directory layout, anti-patterns, and build order rationale.

**Major components:**

1. `SKILL.md` (per skill) — frontmatter triggers for agent discovery, core decision logic, quick-reference tables, links to references; hard 500-line limit
2. `references/` (3 files per skill) — detailed how-to content loaded lazily; one file per provider variant or major sub-topic (e.g., `clerk-setup.md`, `nextauth-setup.md`, `oauth-patterns.md`)
3. `INDEX.md` (modified) — central discovery table; must gain 3 new categories and 5 new rows plus 4 Quick Selection Guide entries
4. 4 existing skills (modified) — `api-patterns/auth.md`, `pci-compliance/SKILL.md`, `postgresql/SKILL.md` need forward-references to avoid content duplication

Total file count: 20 new files + 4 modified files.

### Critical Pitfalls

See `.planning/research/PITFALLS.md` for full pitfall descriptions, warning signs, and recovery strategies.

1. **Auth.js deprecation** — Auth.js team joined Better Auth in Sept 2025; the skill must recommend Clerk (managed) or Better Auth (self-hosted) as primary paths, not Auth.js v5. Scope Auth.js coverage to existing projects only, and document the v4 → v5 cookie rename that silently logs users out.

2. **Stripe webhook not idempotent** — Stripe retries for up to 3 days; inline processing causes duplicate order fulfillment. The correct pattern is: verify signature → store raw event with `event.id` as unique key → return 200 immediately → process asynchronously. This must be in the main SKILL.md body, not a references file.

3. **RAG hallucinations blamed on the LLM** — Low retrieval quality (wrong chunks, embedding model mismatch, too-small chunk sizes) causes hallucinations that are misdiagnosed as generation failures. The skill must cover retrieval evaluation separately from generation quality, and must include a score-threshold fallback ("I don't know" if top result similarity is below threshold).

4. **Agent skill scope creep** — The agent domain is wide enough to blow the 500-line limit and produce an abstract skill that cannot be applied. Scope is defined in the outline phase: focus on task decomposition, handoffs, context budget management, and failure modes. Framework comparisons and memory store setup go to references/ from day one.

5. **Prompt engineering staleness** — Prompt techniques are model-family specific. CoT prompting actively degrades output on reasoning models (o3, DeepSeek R1) that already reason internally. Every technique must be tagged with `Applies to:` (instruction-tuned / reasoning / both) and the skill must carry a `last-verified-against:` frontmatter field.

6. **Auth + Stripe integration gap** — Neither skill individually covers the handoff: user signup → create Stripe Customer → store `stripe_customer_id` → subscription-gate protected routes. Both skills need a "Cross-skill integration" section documenting their shared seam.

## Implications for Roadmap

Based on combined research, the dependency graph determines phase order. Skills must be authored in dependency order to ensure cross-references point to complete, accurate content.

### Phase 1: Foundation Skills

**Rationale:** Prompt-engineering has no new-skill dependencies and is referenced by agent-architecture. Auth-systems has no new-skill dependencies and is referenced by stripe-payments. Build both first so downstream skills can reference finished content.

**Delivers:** Two complete, shippable skills — the most standalone and the most foundational of the five domains.

**Implements features:** Full prompt anatomy, anti-pattern catalogue, versioning conventions; Clerk + Better Auth quick-starts, protected routes, DAL pattern, cache pitfall callout.

**Avoids:** Prompt skill model staleness (model tagging in frontmatter established before any content written); Auth.js deprecation (Better Auth positioned as primary self-hosted path from day one).

**Research flag:** Standard patterns — both skills have well-documented library choices and clear scope boundaries. No phase-level research needed.

### Phase 2: RAG and Agent Architecture

**Rationale:** RAG has no new-skill dependencies (it extends existing postgresql/database-design skills). Agent-architecture depends on prompt-engineering being complete (Phase 1). Both belong in the same phase: they cross-reference each other (RAG is an external memory tool for agents) and share the AI/LLM INDEX.md category.

**Delivers:** The complete AI/LLM skill cluster — enables semantic search, agent construction, and multi-step workflows in developer projects.

**Implements features:** Full embed → store → query loop with pgvector, hybrid search, retrieval evaluation; orchestrator–worker pattern, MCP overview, tool calling, memory taxonomy, token budget guidance.

**Avoids:** RAG hallucination trap (retrieval evaluation section required in SKILL.md outline before writing begins); Agent scope creep (outline capped at 6 top-level sections).

**Research flag:** RAG hybrid search (vector + BM25 RRF) and agent failure budget patterns are moderately complex — consider `/gsd:research-phase` if implementation guidance feels thin during authoring.

### Phase 3: Stripe Payments

**Rationale:** Stripe depends on auth-systems (Phase 1) for user identity → Stripe Customer mapping. Must come after auth-systems is complete so cross-references point to accurate patterns.

**Delivers:** Complete payments skill covering one-time checkout, subscription billing, webhook handling, and customer portal.

**Implements features:** Checkout session creation, subscription setup, idempotent webhook handler, async processing pattern, Stripe CLI testing workflow, test card cheat sheet.

**Avoids:** Webhook idempotency failure (event.id deduplication pattern in main SKILL.md, not references); hardcoded price IDs (always use env vars in examples).

**Research flag:** Standard patterns — Stripe's official docs are comprehensive and well-maintained. No phase-level research needed.

### Phase 4: Integration Review

**Rationale:** Cross-skill integration gaps are predictable and invisible until all five skills are drafted. This phase exists specifically to audit and close those gaps before the milestone is marked complete.

**Delivers:** Cross-reference audit, integration sections added to Auth + Stripe skill pair, INDEX.md completeness verification, 500-line check on all SKILL.md files.

**Addresses pitfalls:** Auth + Stripe integration gap (user identity → Stripe Customer handoff); Agent auth context pattern (how agents pass auth through tool calls); INDEX.md update completeness.

**Research flag:** No research needed — this is a QA and linkage phase. Use the "Looks Done But Isn't" checklist from PITFALLS.md as the verification gate.

### Phase Ordering Rationale

- Dependency order (prompt → agent, auth → stripe) prevents cross-references from pointing at incomplete content.
- RAG and Agent are batched together because they share the AI/LLM INDEX category and cross-reference each other — authoring them in the same phase avoids one-way references.
- Integration review is a mandatory final phase, not optional polish — the Auth + Stripe seam and the 500-line constraint are the two highest-probability failure modes for this milestone.

### Research Flags

Phases needing `/gsd:research-phase` during planning:
- **Phase 2 (RAG):** Hybrid search (pgvector + PostgreSQL tsvector + RRF merge) — moderately complex, sparse examples in official docs
- **Phase 2 (Agent):** Failure budget patterns and partial failure recovery — documented in theory, fewer concrete code examples available

Phases with standard patterns (skip research-phase):
- **Phase 1 (Prompt Engineering):** Core techniques are well-documented; model tagging convention is a structural decision, not a research question
- **Phase 1 (Auth Systems):** Clerk and Better Auth both have thorough official docs; stack is verified
- **Phase 3 (Stripe):** Stripe's documentation is industry-leading; webhook idempotency pattern is a known, documented solution
- **Phase 4 (Integration Review):** Checklist-driven QA phase; no research required

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All library versions verified against live npm/PyPI on 2026-02-24; version compatibility matrix confirmed against existing viflo stack |
| Features | HIGH (Auth, Stripe) / MEDIUM (RAG, Agent, Prompt) | Auth and Stripe feature sets are stable and well-defined; RAG, Agent, and Prompt engineering are evolving domains with some uncertainty around best practices |
| Architecture | HIGH | Based on direct inspection of existing `.agent/skills/` codebase; conventions are explicit and enforced by prior v1.1 requirements |
| Pitfalls | MEDIUM | Most pitfalls are verified against official sources; Auth.js deprecation is confirmed via GitHub discussion; prompt engineering model-staleness is inference from known model behavior differences |

**Overall confidence:** HIGH for execution decisions; MEDIUM for RAG/Agent content depth

### Gaps to Address

- **Better Auth coverage:** STACK.md covers Auth.js v5 in detail but PITFALLS.md flags the team's move to Better Auth. Auth skill authoring must resolve whether to cover Better Auth directly or treat it as a reference-only callout. Recommendation: cover Better Auth's install and `auth()` API as the self-hosted path; keep Auth.js as a "migration from" section.
- **Hybrid search implementation depth:** FEATURES.md marks hybrid search as HIGH complexity. STACK.md does not cover BM25/tsvector tooling. If Phase 2 includes hybrid search in the main SKILL.md (recommended), verify the specific pgvector + tsvector + RRF pattern against viflo's SQLAlchemy 2.0 stack before writing.
- **Agent token budget enforcement:** PITFALLS.md identifies multi-agent token runaway as a HIGH-cost recovery scenario. STACK.md does not specify which SDK surfaces `max_turns` / `max_tokens_per_run` controls. Verify against `@langchain/langgraph` and Vercel AI SDK v6 docs during Phase 2 authoring.
- **INDEX.md category naming:** ARCHITECTURE.md recommends "AI / LLM" as the new category name. Verify this matches existing INDEX.md formatting conventions before creating the section.

## Sources

### Primary (HIGH confidence)

- [npmjs.com — package registry] — all npm package versions verified live
- [PyPI — package registry] — Python package versions verified live
- Direct inspection of `.agent/skills/` codebase — architecture patterns and conventions
- `.planning/PROJECT.md` — v1.1 CONTENT-01 constraint (≤500 lines), v1.2 requirements
- [Clerk Docs](https://clerk.com/docs) — v6 breaking changes, middleware patterns
- [Auth.js Docs](https://authjs.dev) — v5 API, session management
- [Stripe Webhook Docs](https://docs.stripe.com/webhooks) — raw body requirement, constructEvent()
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — multi-agent patterns

### Secondary (MEDIUM confidence)

- [Auth.js → Better Auth migration discussion](https://github.com/nextauthjs/next-auth/discussions/13252) — team transition confirmed via GitHub
- [Stripe webhook best practices — Stigg](https://www.stigg.io/blog-posts/best-practices-i-wish-we-knew-when-integrating-stripe-webhooks) — idempotency pattern
- [RAG at Scale — Redis 2026](https://redis.io/blog/rag-at-scale/) — retrieval evaluation methodology
- [Optimizing RAG with hybrid search — Superlinked](https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking) — BM25 + vector RRF pattern
- [The Economics of Autonomy — Alps Agility](https://www.alpsagility.com/cost-control-agentic-systems) — token runaway prevention
- [Prompt engineering 2025 state — Aakash G](https://www.news.aakashg.com/p/prompt-engineering) — reasoning model CoT anti-pattern

### Tertiary (LOW confidence — needs validation during authoring)

- Better Auth install and `auth()` API surface — not covered in STACK.md; verify against Better Auth official docs before writing auth-systems skill
- pgvector + tsvector hybrid search with RRF merge — pattern confirmed conceptually; specific SQLAlchemy 2.0 implementation needs verification

---
*Research completed: 2026-02-24*
*Ready for roadmap: yes*
