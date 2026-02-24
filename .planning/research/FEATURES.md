# Feature Research

**Domain:** Skill file library — Stripe Payments, RAG/Vector Search, Agent Architecture (v1.3)
**Researched:** 2026-02-24
**Confidence:** HIGH (Stripe), HIGH (RAG), MEDIUM (Agent Architecture)

---

## Context

This research covers the three new skill areas for viflo v1.3. These are *documentation modules*
(SKILL.md + references/) that an AI coding assistant loads at task time. The audience is a solo
developer or small team using viflo with Claude Code or a similar agentic tool. The question for
each skill is: what must the skill cover to be immediately useful when the AI picks it up mid-task?

**Scope boundary:** Auth systems and Prompt Engineering were completed in v1.2. This document covers
ONLY the three skills active in v1.3: Stripe, RAG, and Agent Architecture.

**Depth standard:** The auth-systems skill (437 lines, v1.2) is the canonical reference. It provides:
Quick Start, numbered Setup/Configuration/Patterns/Gotchas sections, named pitfalls with warning
signs, and side-by-side comparisons. All three v1.3 skills must reach this structural benchmark.

**Current state of the three skills:** All three have SKILL.md files (~80–92 lines each) with the
four depth-standard sections (Decision Matrix, Implementation Patterns, Failure Modes, Version Context).
They pass the basic depth checklist but fall short of auth-systems depth in:
- No Quick Start section (zero-to-running code in <30 lines)
- No named, numbered Gotchas with warning signs
- No deeper pattern coverage in SKILL.md (too thin; auth carries 437 lines itself)

The v1.3 work is an upgrade, not a greenfield write.

---

## Skill 1: Stripe Payments

### Table Stakes (Users Expect These)

Features a developer assumes the skill covers. Missing these = skill feels useless.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Quick Start: working checkout in <30 lines | Auth skill has this; developers expect parity | LOW | `stripe.checkout.sessions.create()` + redirect; works on first read |
| Checkout Session (one-time + subscription) | Simplest Stripe flow; every payment skill must cover it | LOW | `mode: 'payment'` and `mode: 'subscription'` side-by-side |
| Webhook receiver with signature verification | Critical security step; the #1 production mistake | MEDIUM | `stripe.webhooks.constructEvent()` with raw body requirement |
| Idempotent webhook handler (dedup by event.id) | Stripe retries events; duplicate processing causes double billing | MEDIUM | Already in references/webhook-patterns.md — needs surfacing in SKILL.md |
| Subscription status sync (DB-first pattern) | Subscription state lives in Stripe; sync strategy is non-obvious | MEDIUM | Already in references/subscription-patterns.md |
| Customer Portal for self-serve billing | Users expect to update cards and cancel themselves | LOW | One redirect; already in SKILL.md |
| Storing Stripe IDs (not card data) in DB | PCI DSS: never store card data; store customer_id, subscription_id | LOW | Schema pattern already in references/ |
| Key events to handle (the four critical ones) | Devs don't know which events matter | LOW | checkout.session.completed, invoice.payment_failed, customer.subscription.updated/.deleted |
| Environment variable split (test vs live keys) | The #2 most common mistake; mixing keys corrupts production | LOW | STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY |

**Gap vs current skill:** Quick Start section is missing entirely. Gotchas section (named, numbered,
with warning signs) is absent. The current SKILL.md has 91 lines; the auth equivalent would be
~350–400 lines to reach full depth.

### Differentiators (Competitive Advantage)

Features that make this skill exceptional versus looking up official docs.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Named Gotchas with warning signs (auth-style) | Negative patterns are more memorable than positive rules | LOW | Gotcha 1: raw body parsing; Gotcha 2: test vs live key mismatch; Gotcha 3: checkout session expiry |
| Async webhook processing pattern | Stripe's 30-second timeout bites devs; return 200 fast then process | MEDIUM | Currently missing from SKILL.md; references/ exists but isn't surfaced |
| Stripe CLI local testing block | Devs spend hours debugging webhooks; `stripe listen --forward-to` solves it | LOW | Already in references/webhook-patterns.md — promote to SKILL.md |
| Test card cheat-sheet | Everyone needs `4242 4242 4242 4242` and failure scenarios | LOW | Declined, auth-required, and dispute test cards in a quick-reference table |
| Plan change proration pattern | Upgrade = immediate proration; downgrade = end-of-period | MEDIUM | Currently in references/subscription-patterns.md — needs summary in SKILL.md |
| Grace period pattern for failed payments | invoice.payment_failed → past_due state + cron downgrade after N days | MEDIUM | Currently in references/; pattern is high-value and widely mishandled |

### Anti-Features (Scope Creep to Avoid)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full PCI DSS compliance documentation | "We handle payments so we need this" | viflo already has a `pci-compliance` skill | Reference that skill; do not duplicate |
| Custom payment form (Stripe Elements) | Full UI control | Complex; Stripe Checkout covers 90% of use cases | One paragraph: use Checkout unless brand control is a hard requirement |
| Connect / marketplace payments | Multi-vendor payouts | Entirely different product; own skill territory | Out-of-scope callout in frontmatter |
| Tax calculation (Stripe Tax) | Automatic tax is attractive | Regulatory complexity changes frequently | Reference Stripe Tax docs only |
| Invoicing API deep dive | B2B invoicing is a valid use case | Niche; blows the 500-line SKILL.md budget | One-sentence mention with link |
| Usage-based / metered billing deep dive | AI products charge per token | High complexity; own references/ file at most | One callout in Decision Matrix; point to Stripe Meters docs |

---

## Skill 2: RAG / Vector Search

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Quick Start: embed one document + query in <30 lines | Auth skill has this pattern; devs expect a copy-pasteable start | MEDIUM | OpenAI embed → pgvector insert → cosine similarity query |
| Embedding pipeline: chunk → embed → store | The core RAG loop; skill is useless without it | MEDIUM | Already in references/embedding-pipelines.md — needs distilled version in SKILL.md Quick Start |
| pgvector setup and schema | viflo stack uses PostgreSQL; pgvector is the natural fit | MEDIUM | CREATE EXTENSION, vector(1536) column, ivfflat/hnsw index choice |
| Cosine similarity query with threshold | The retrieval half of RAG; equally important as ingestion | MEDIUM | Already in SKILL.md; min_score filter is important and present |
| Chunking strategy rules | Biggest performance lever; most tutorials skip it | MEDIUM | Already in references/embedding-pipelines.md |
| Embedding model consistency rule | Single most common RAG bug: query and index use different models | LOW | Currently mentioned in SKILL.md Failure Modes — needs promotion to named Gotcha |
| pgvector vs Pinecone decision rule | Devs need a decision rule, not a library survey | LOW | Already in Decision Matrix |
| Full RAG query loop (end-to-end) | Devs need to see embed → retrieve → prompt construction together | MEDIUM | RAG prompt assembly is in references/retrieval-patterns.md — promote to SKILL.md |

**Gap vs current skill:** Quick Start is missing. Gotchas section with named pitfalls is missing.
The embedding model consistency rule is buried in Failure Modes; it should be Gotcha #1 with a
bold warning. Current SKILL.md is 92 lines; auth equivalent would be ~350–400 lines.

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Named Gotchas with warning signs (auth-style) | Negative patterns are the most memorable content | LOW | Gotcha 1: model version mismatch (existing data becomes garbage); Gotcha 2: chunk-size too small (hallucinations); Gotcha 3: no similarity threshold (bad context) |
| Hybrid search (vector + BM25/full-text) | Consistently outperforms pure vector; most tutorials skip it | HIGH | Already in references/retrieval-patterns.md — promote summary to SKILL.md |
| Index synchronization strategy | Updating documents after ingestion is harder than first indexing | MEDIUM | Delete-and-reinsert vs update; model_version tag makes this safe |
| Similarity threshold calibration guide | "My RAG feels wrong" is not actionable; calibration gives a method | LOW | Log scores against 20 test queries; start at 0.75; already partially in references/ |
| Re-ranking (two-stage retrieval) overview | Higher precision for long documents; widely used in production | HIGH | Already in references/retrieval-patterns.md — one-paragraph summary in SKILL.md |
| Observability: log retrieved chunks per call | Without this, debugging RAG is guesswork | LOW | Pattern: log query, top-k chunks, and final prompt in same trace |

### Anti-Features (Scope Creep to Avoid)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Fine-tuning embedding models | "Custom embeddings will be better" | Requires ML expertise and GPU budget | Use text-embedding-3-small; it's excellent and cheap |
| Full LangChain integration deep dive | LangChain is popular | Changes rapidly; abstracts away understanding | Show the raw pattern first; mention LangChain as an option |
| Multimodal RAG (images, audio) | Emerging use case | Entirely different pipeline; no pgvector support | One-sentence future reference |
| GraphRAG / knowledge graphs | Interesting research topic | Production complexity 10x; no standard tooling | Out-of-scope callout |
| Pinecone as primary path | Some devs want a managed vector DB | viflo stack is PostgreSQL-first | Cover Pinecone in references/ file only; not primary path |
| Agentic RAG (tool-calling retrieval) | Agents calling RAG as a tool | Better covered in Agent Architecture skill | Cross-reference the agent skill; don't duplicate |

---

## Skill 3: Agent Architecture

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Quick Start: single agent with one tool in <30 lines | Devs expect a working example to copy-paste | MEDIUM | Tool definition + runAgentLoop call + executeTool dispatch |
| Core agent loop (tool_use → execute → tool_result) | The mechanism; everything else builds on it | MEDIUM | Already in references/multi-agent-patterns.md — needs condensed version in SKILL.md |
| Tool definition schema (Anthropic + OpenAI) | Agents are useless without tools | MEDIUM | Already in SKILL.md; both providers covered |
| Orchestrator–worker dispatch pattern | Most common multi-agent pattern; high practical value | MEDIUM | Already in SKILL.md and references/ |
| Memory types taxonomy | Agents without memory degrade; devs need the taxonomy | MEDIUM | Already in references/memory-orchestration.md |
| Loop guard (max depth counter) | Without this, agents loop indefinitely and burn API budget | LOW | Already in references/multi-agent-patterns.md as depth counter |
| Context window budget management | Long chains exhaust context; common production surprise | LOW | Already in references/memory-orchestration.md |
| When NOT to use agents | Agents are overused; this is genuinely valuable | LOW | Currently in Decision Matrix implicitly; needs explicit callout |

**Gap vs current skill:** Quick Start is missing. Gotchas section is missing. The agent loop guard
is buried in references/; it should be Gotcha #1 with a bold cost warning. Current SKILL.md is 80
lines; auth equivalent would be ~350–400 lines.

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Named Gotchas with warning signs (auth-style) | Multi-agent failures are silent and expensive | MEDIUM | Gotcha 1: agent loop without depth guard (runaway cost); Gotcha 2: handoff data loss (always send full context); Gotcha 3: parallel agents writing same record (race condition) |
| Anthropic's composable patterns overview | Vendor-aligned; matches viflo's Claude Code environment | MEDIUM | Prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer |
| Model tier strategy (Opus → Haiku) | Reserve expensive models for planning; cheap for execution | LOW | Already in SKILL.md Decision Matrix — needs explicit section |
| Prompt injection via tool results | Malicious content in tool output hijacks agent; often ignored | MEDIUM | Already in SKILL.md Failure Modes — promote to named Gotcha |
| Checkpointing long tasks | Agents fail partway through; resumability is critical | MEDIUM | Already in references/memory-orchestration.md |
| MCP overview (viflo already uses it) | Industry converging on MCP for agent-tool communication | MEDIUM | What it is; when it adds value vs direct tool calling |

### Anti-Features (Scope Creep to Avoid)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full LangGraph / LangChain deep dive | Popular framework | Framework-specific; changes rapidly; obscures core patterns | Show patterns in plain TypeScript; mention LangGraph as an option |
| AutoGen / CrewAI / other framework tutorials | "Which framework should I use?" | Framework churn is high; this is a patterns skill | One comparison table in references/ only |
| Autonomous long-running agent without human oversight | Seems powerful | High failure rate; safety risk | Always design for human-in-the-loop checkpoints |
| Agent fine-tuning | "I want a specialized agent" | Requires ML infrastructure; out of scope | Use system prompt engineering + tool definition instead |
| Full agent platform setup (Vertex AI Agents, etc.) | Managed convenience | Cloud-specific; violates viflo's tool-agnostic principle | Cover in cloud-deployment skill if needed |
| Streaming agent responses | Better UX for long tasks | Adds WebSocket/SSE complexity; separate concern | One-paragraph mention only |

---

## Feature Dependencies

```
Stripe skill
    └──depends on──> auth-systems (customer-to-user mapping requires authenticated user ID)
    └──references──> pci-compliance (existing skill; do not duplicate)
    └──uses pattern from──> fastapi-templates (webhook route handlers on FastAPI side)

RAG skill
    └──extends──> postgresql (pgvector type already mentioned in postgresql skill)
    └──enhances──> agent-architecture (RAG as the external memory/retrieval tool for agents)
    └──uses──> prompt-engineering (query-time prompt construction pattern)

Agent Architecture skill
    └──uses──> prompt-engineering (system prompts, tool descriptions, evaluator-optimizer pattern)
    └──uses──> rag-vector-search (external memory tool for agents — cross-reference both skills)
    └──references──> workflow-orchestration-patterns (existing skill)
```

### Dependency Notes

- **Stripe requires auth-systems:** The billing portal endpoint must look up stripeCustomerId via
  authenticated session — never trust a client-provided customerId. Auth must be live before
  Stripe integration is meaningful.
- **RAG and Agent are mutually reinforcing:** RAG is the standard external memory mechanism for
  agents. Both skills should cross-reference each other. Build RAG before Agent Architecture
  so the cross-reference is valid when the Agent skill is written.
- **Prompt Engineering is a prerequisite for Agent Architecture:** Agent system prompts, tool
  descriptions, and the evaluator-optimizer pattern are all prompt engineering. The agent skill
  can reference prompt-engineering instead of repeating the fundamentals.

---

## What "v1.2 Depth" Means for Each Skill (Gap Analysis)

The auth-systems skill (437 lines) is the canonical benchmark. These three skills currently range
from 80–92 lines — they have the four failure-mode sections but lack structural depth.

### Stripe Payments — current score: 3/4 failure modes mitigated

**What exists (keep):**
- Decision Matrix: comprehensive, has explicit defaults
- Implementation Patterns: Checkout Session + Customer Portal with annotated warnings
- Failure Modes: 7 scenarios covered including duplicate delivery, mid-cycle changes, trial end
- Version Context: versioned, recent (2025-01-27.acacia API)
- references/webhook-patterns.md: idempotency via Prisma @unique, Stripe CLI testing
- references/subscription-patterns.md: status mapping, plan changes, grace period

**What to add for v1.2 depth:**
- Quick Start section (zero-to-checkout in <20 lines, before any other content)
- Gotchas section (named, numbered) with these three at minimum:
  1. Raw body requirement (parsing JSON first corrupts signature verification)
  2. Test vs live key mismatch (silent; only fails in production)
  3. Checkout session expiry (URL-only success check is wrong)
- Stripe CLI testing block promoted from references/ into SKILL.md
- Test card quick-reference table in SKILL.md

### RAG / Vector Search — current score: 3/4 failure modes mitigated

**What exists (keep):**
- Decision Matrix: pgvector vs Pinecone vs Qdrant with explicit default
- Implementation Patterns: embed pipeline + cosine search with model_version filter
- Failure Modes: 6 scenarios including model change, threshold, cold start, rate limits
- Version Context: versioned libraries
- references/embedding-pipelines.md: chunking rules, batch retry, pgvector schema + index SQL
- references/retrieval-patterns.md: hybrid search SQL, RAG prompt assembly, re-ranking, threshold calibration

**What to add for v1.2 depth:**
- Quick Start section (embed one string + query back in <25 lines)
- Gotchas section (named, numbered) with these three at minimum:
  1. Embedding model version mismatch (existing index becomes garbage — bold warning)
  2. Chunk size too small (128-token chunks split mid-concept → hallucination)
  3. No similarity threshold (confident answers from irrelevant context)
- RAG prompt assembly snippet promoted from references/ into SKILL.md
- Hybrid search summary promoted from references/ into SKILL.md

### Agent Architecture — current score: 3/4 failure modes mitigated

**What exists (keep):**
- Decision Matrix: single-agent vs orchestrator vs event-driven with explicit default
- Implementation Patterns: tool definition (Anthropic) + orchestrator dispatch
- Failure Modes: 6 scenarios including loop, context overflow, handoff loss, prompt injection
- Version Context: Claude and GPT model names with use-case guidance
- references/multi-agent-patterns.md: full agent loop with depth guard, handoff context interface
- references/memory-orchestration.md: memory types table, checkpointing, context compression

**What to add for v1.2 depth:**
- Quick Start section (single agent + one tool, running in <25 lines)
- Gotchas section (named, numbered) with these three at minimum:
  1. No loop depth guard (runaway API costs — show the counter pattern inline)
  2. Handoff data loss (passing only the delta; always send full context)
  3. Prompt injection via tool results (malicious tool output hijacks agent)
- Explicit "When NOT to use agents" callout (single-step tasks, latency-sensitive paths,
  deterministic tasks)
- Anthropic composable patterns overview (5 patterns, one paragraph each)
- Model tier strategy section (Opus for planning, Haiku/Sonnet for execution)

---

## MVP Definition (What Ships in v1.3 Per Skill)

### Launch With (each skill's SKILL.md)

Sections required in every SKILL.md to meet auth-systems depth standard:

- [ ] Quick Start — working code in <30 lines, immediately copy-pasteable
- [ ] Decision Matrix — when-to-use-X-vs-Y with explicit recommended default
- [ ] Implementation Patterns — at least 2 annotated code examples with inline warnings
- [ ] Gotchas / Pitfalls — at minimum 3 named pitfalls with warning signs
- [ ] Failure Modes & Edge Cases — at least 5 concrete scenarios with handling strategy
- [ ] Version Context — last-verified library versions

SKILL.md must remain ≤500 lines. All code examples >30 lines go to references/.

### Retain in references/ (already exists — keep as-is)

- Stripe: webhook-patterns.md (idempotency, env vars, Stripe CLI testing)
- Stripe: subscription-patterns.md (status mapping, plan changes, grace period)
- RAG: embedding-pipelines.md (chunking function, batch retry, pgvector schema)
- RAG: retrieval-patterns.md (hybrid search SQL, RAG prompt assembly, re-ranking)
- Agent: multi-agent-patterns.md (full agent loop, handoff context)
- Agent: memory-orchestration.md (memory types, checkpointing, context compression)

### Future Consideration (v1.4+)

- Stripe: Connect / marketplace payments (own skill territory)
- Stripe: Usage-based metered billing deep dive (Stripe Meters API)
- RAG: Multimodal retrieval (images, audio) — different pipeline
- RAG: Agentic RAG (retrieval as a tool call inside an agent loop)
- Agent: Full LangGraph workflow patterns (framework-specific)
- Agent: MCP server implementation guide (currently one-paragraph overview)

---

## Feature Prioritization Matrix

| Skill / Feature | User Value | Implementation Cost | Priority |
|----------------|------------|---------------------|----------|
| Stripe: Quick Start section | HIGH | LOW | P1 |
| Stripe: Gotchas section (3 named pitfalls) | HIGH | LOW | P1 |
| Stripe: Checkout + subscription side-by-side | HIGH | LOW | P1 |
| Stripe: Webhook idempotency (promote from references/) | HIGH | LOW | P1 |
| Stripe: Stripe CLI testing block in SKILL.md | HIGH | LOW | P1 |
| Stripe: Test card table | MEDIUM | LOW | P2 |
| Stripe: Grace period pattern summary | MEDIUM | LOW | P2 |
| RAG: Quick Start section | HIGH | LOW | P1 |
| RAG: Gotchas section (3 named pitfalls) | HIGH | LOW | P1 |
| RAG: Model version mismatch warning (promote) | HIGH | LOW | P1 |
| RAG: RAG prompt assembly (promote from references/) | HIGH | LOW | P1 |
| RAG: Hybrid search summary (promote from references/) | MEDIUM | LOW | P2 |
| RAG: Similarity threshold calibration guide | MEDIUM | LOW | P2 |
| Agent: Quick Start section | HIGH | LOW | P1 |
| Agent: Gotchas section (3 named pitfalls) | HIGH | LOW | P1 |
| Agent: Loop depth guard (promote from references/) | HIGH | LOW | P1 |
| Agent: "When NOT to use agents" explicit callout | HIGH | LOW | P1 |
| Agent: Anthropic composable patterns overview | MEDIUM | LOW | P2 |
| Agent: Model tier strategy section | MEDIUM | LOW | P2 |
| Agent: MCP overview paragraph | LOW | LOW | P3 |

**Priority key:**
- P1: Must have to reach v1.2 depth standard
- P2: Should have, adds meaningful value without blowing 500-line budget
- P3: Nice to have, include only if room remains

---

## Sources

- Stripe: [Stripe webhooks official docs](https://docs.stripe.com/billing/subscriptions/webhooks), [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests), [Stripe Checkout docs](https://docs.stripe.com/payments/checkout)
- RAG: Current SKILL.md and references/ files (verified against pgvector 0.8.x and openai 4.x)
- RAG: [pgvector GitHub](https://github.com/pgvector/pgvector) — ivfflat vs hnsw guidance
- Agent: Current SKILL.md and references/ files (verified against @anthropic-ai/sdk 0.37.x)
- Agent: Anthropic agent patterns referenced in agent-architecture skill description
- Depth standard: `.agent/skills/skill-depth-standard/SKILL.md` (internal)
- Canonical reference: `.agent/skills/auth-systems/SKILL.md` (v1.2 benchmark, 437 lines)

---

*Feature research for: viflo v1.3 expert skills (Stripe, RAG, Agent Architecture)*
*Researched: 2026-02-24*
