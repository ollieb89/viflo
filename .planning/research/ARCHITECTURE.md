# Architecture Research

**Domain:** Skill file integration — viflo v1.3 Expert Skills (Stripe, RAG, Agent Architecture)
**Researched:** 2026-02-24
**Confidence:** HIGH (skill system from direct codebase inspection; domain integration from official docs + verified community sources)

---

## Part 1: Viflo Skill System Architecture (Unchanged from v1.2)

### Existing Skill System Overview

```
.agent/skills/
├── INDEX.md                        ← Central discovery file (MUST be updated)
├── <skill-name>/
│   ├── SKILL.md                    ← Required: YAML frontmatter + instructions (≤500 lines)
│   ├── references/                 ← Optional: Deep content loaded on demand
│   │   ├── guides/                 ← Detailed how-to content
│   │   └── <topic>.md              ← Domain-specific reference files
│   ├── assets/                     ← Optional: Templates/boilerplate (not loaded into context)
│   └── scripts/                    ← Optional: Executable helpers
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| SKILL.md frontmatter | Trigger matching — agent reads this to decide whether to load the skill | YAML with `name` and `description`; description doubles as "when to use" signal |
| SKILL.md body | Core instructions, quick-reference patterns, links to references | Markdown ≤500 lines; cross-references via skill name, not @ syntax |
| references/ | Detailed content loaded lazily when Claude determines it is needed | One file per sub-topic |
| assets/ | Boilerplate copied into user projects, not read into context | Templates, example configs, starter code |
| INDEX.md | Skill discovery — the top-level table of contents for all skills | Markdown tables by category; updated whenever a skill is added |

---

## Part 2: Domain Integration Architecture

This section answers: *how do Stripe Payments, RAG/Vector Search, and Agent Architecture integrate into a Next.js + FastAPI + PostgreSQL stack?* Each domain introduces specific new components, data flows, and database changes.

### 2A: Stripe Payments Integration

#### New Components Introduced

```
Next.js (frontend)
├── app/
│   ├── (billing)/
│   │   ├── checkout/page.tsx       ← Renders Stripe Checkout button
│   │   ├── success/page.tsx        ← Post-payment redirect page
│   │   └── portal/page.tsx         ← Customer billing portal redirect
│   └── api/
│       └── webhooks/
│           └── stripe/route.ts     ← Webhook endpoint (receives Stripe events)

FastAPI (backend)
├── routers/
│   └── billing.py                  ← POST /billing/checkout-session
│                                      POST /billing/portal-session
│                                      GET  /billing/subscription-status
├── webhooks/
│   └── stripe.py                   ← POST /webhooks/stripe (raw body, sig verify)
├── services/
│   └── stripe_service.py           ← Stripe SDK wrapper (checkout, subscriptions)
└── models/
    └── billing.py                  ← Customer, Subscription ORM models

PostgreSQL (new tables)
├── customers                       ← stripe_customer_id ↔ user_id mapping
└── subscriptions                   ← status, plan_id, period_start/end, cancel_at
```

**Key principle:** Stripe Checkout keeps card data entirely off your servers. No PAN, CVV, or raw card data touches FastAPI or PostgreSQL. Your backend only stores Stripe-issued IDs (`cus_xxx`, `sub_xxx`, `pi_xxx`).

#### Data Flow: Checkout Session

```
User clicks "Subscribe"
    ↓
Next.js → POST /billing/checkout-session (with user_id)
    ↓
FastAPI → stripe.checkout.sessions.create(...)
    ↓
Stripe returns session_id + checkout URL
    ↓
FastAPI returns { url } to Next.js
    ↓
Next.js redirects to stripe.com/pay/...
    ↓
User pays on Stripe-hosted page
    ↓
Stripe fires checkout.session.completed webhook
    ↓
FastAPI /webhooks/stripe verifies sig → updates subscriptions table
    ↓
Next.js /success page — reads subscription status from DB
```

**Never fulfill on redirect URL alone.** The redirect fires even when payment fails in edge cases. Always use the `checkout.session.completed` webhook as the source of truth for order fulfillment.

#### Data Flow: Webhook Handling

```
Stripe POST /webhooks/stripe
    ↓
FastAPI reads raw request body (not parsed JSON)
    ↓
stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    ↓
Check processed_webhook_events table for event.id (idempotency gate)
    ↓
Switch on event.type:
  checkout.session.completed    → create/activate subscription row
  customer.subscription.updated → update status, plan, period dates
  customer.subscription.deleted → set status = 'canceled'
  invoice.payment_failed        → flag subscription, trigger retry email
    ↓
Save event.id to processed_webhook_events
    ↓
Return 200 immediately (Stripe retries up to 72h on non-200)
```

**Critical:** Read raw body with `await request.body()` in FastAPI before any JSON parsing. Framework JSON parsing changes whitespace and breaks signature verification.

#### PostgreSQL Schema (New Tables)

```sql
-- Maps your users to Stripe customers (1:1)
CREATE TABLE customers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255) NOT NULL UNIQUE,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Mirrors Stripe subscription state
CREATE TABLE subscriptions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id),
    stripe_subscription_id  VARCHAR(255) NOT NULL UNIQUE,
    stripe_price_id         VARCHAR(255) NOT NULL,
    status                  VARCHAR(50) NOT NULL,  -- active, past_due, canceled, ...
    current_period_start    TIMESTAMPTZ,
    current_period_end      TIMESTAMPTZ,
    cancel_at               TIMESTAMPTZ,
    created_at              TIMESTAMPTZ DEFAULT now(),
    updated_at              TIMESTAMPTZ DEFAULT now()
);

-- Idempotency gate for webhook events
CREATE TABLE processed_webhook_events (
    stripe_event_id VARCHAR(255) PRIMARY KEY,
    processed_at    TIMESTAMPTZ DEFAULT now()
);
```

#### Integration Points with Existing Stack

| Existing Component | Change | Why |
|-------------------|--------|-----|
| `auth-systems` skill | **Prerequisite** — Stripe requires authenticated user_id to associate charges | Cannot bill anonymously |
| `backend-dev-guidelines` | Add billing router, webhook endpoint, raw body middleware | New FastAPI routes |
| `pci-compliance` | No change needed — Stripe Checkout handles card data | Your scope is SAQ A |
| `database-design` | Add 3 new tables (customers, subscriptions, webhook events) | Stripe state mirror |

---

### 2B: RAG / Vector Search Integration

#### New Components Introduced

```
Next.js (frontend)
├── app/
│   └── (search)/
│       └── page.tsx                ← Search input → streaming results display

FastAPI (backend)
├── routers/
│   └── search.py                   ← POST /search/query (retrieval + generation)
│       ingest.py                   ← POST /ingest/document (async ingestion)
├── services/
│   ├── embedding_service.py        ← Wraps embedding model API (OpenAI/local)
│   ├── retrieval_service.py        ← pgvector similarity + hybrid search queries
│   └── generation_service.py      ← LLM call with retrieved context (RAG step)
├── workers/
│   └── ingest_worker.py            ← Background: chunk → embed → upsert
└── models/
    └── documents.py                ← Document, Chunk ORM models with vector column

PostgreSQL (extensions + new tables)
├── pgvector extension              ← CREATE EXTENSION vector
├── documents                       ← source metadata (url, title, type, created_at)
└── document_chunks                 ← text, embedding vector(1536), tsvector column
```

#### Data Flow: Document Ingestion

```
POST /ingest/document { url | text, metadata }
    ↓
FastAPI enqueues to background worker (returns 202 Accepted immediately)
    ↓
Worker: load raw text (HTTP fetch / PDF parse / etc.)
    ↓
Worker: chunk text (fixed-size or semantic — 512 tokens, 50-token overlap)
    ↓
Worker: batch call embedding model API → float[1536] per chunk
    ↓
Worker: bulk INSERT into document_chunks (text, embedding, tsvector)
    ↓
Index updated automatically (HNSW index covers new rows without rebuild)
```

**HNSW vs IVFFlat:** Use HNSW for production. No training step, better recall/speed trade-off, handles incremental inserts without performance cliff. IVFFlat requires a training step and degrades as data grows beyond the initial clustering.

#### Data Flow: RAG Query

```
User submits query
    ↓
POST /search/query { query: "...", top_k: 5 }
    ↓
FastAPI: embed query → float[1536]
    ↓
Retrieval service: run BOTH searches in parallel:
  [A] Vector search: SELECT ... ORDER BY embedding <=> $1 LIMIT 20
  [B] Full-text:     SELECT ... WHERE ts @@ plainto_tsquery($2) LIMIT 20
    ↓
Merge results with RRF (Reciprocal Rank Fusion):
  score = Σ 1 / (k + rank_i) for each result list
    ↓
Take top_k merged results as context
    ↓
LLM call: system prompt + retrieved chunks + user query
    ↓
Stream response back to Next.js (SSE or chunked transfer)
```

**Why hybrid search?** Pure vector search achieves ~62% retrieval precision; adding full-text search + RRF fusion raises it to ~84% (DEV Community, 2025 benchmark). Keyword queries like "PostgreSQL 17 performance" need exact match that vector search alone misses.

#### PostgreSQL Schema (New Tables + Extension)

```sql
-- Enable pgvector extension (once per database)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url  TEXT,
    title       TEXT,
    doc_type    VARCHAR(50),        -- 'webpage', 'pdf', 'markdown', etc.
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE document_chunks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text        TEXT NOT NULL,
    embedding   vector(1536),       -- dimension matches your embedding model
    ts          tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- HNSW index for approximate nearest neighbor search
CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- GIN index for full-text search
CREATE INDEX ON document_chunks USING gin(ts);
```

**SQLAlchemy 2.0 vector column** uses `pgvector.sqlalchemy.VECTOR` type:

```python
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.orm import mapped_column

class DocumentChunk(Base):
    embedding: Any = mapped_column(VECTOR(1536), nullable=True)
```

#### Integration Points with Existing Stack

| Existing Component | Change | Why |
|-------------------|--------|-----|
| `database-design` skill | **Prerequisite** — pgvector is a PostgreSQL extension; migrations add vector columns | Core data model change |
| `postgresql` skill | Add `CREATE EXTENSION vector` to migration; HNSW index syntax | New index type |
| `backend-dev-guidelines` | Add search + ingest routers; async background worker pattern | New FastAPI routes |
| `api-patterns` | SSE streaming for generation responses | LLM output is streamed, not buffered |

---

### 2C: Agent Architecture Integration

#### New Components Introduced

```
Next.js (frontend)
├── app/
│   └── (agent)/
│       └── chat/page.tsx           ← Agent chat UI with SSE stream reader

FastAPI (backend)
├── routers/
│   └── agent.py                    ← POST /agent/run (sync or streaming)
│       agent_stream.py             ← GET  /agent/stream/{run_id} (SSE)
├── agents/
│   ├── orchestrator.py             ← Root agent: routes tasks to sub-agents
│   ├── tools/
│   │   ├── search_tool.py          ← Calls /search/query (RAG integration point)
│   │   ├── code_tool.py            ← Code execution sandbox
│   │   └── web_tool.py             ← HTTP fetch for live data
│   └── memory/
│       ├── short_term.py           ← In-context window management
│       ├── long_term.py            ← pgvector episodic memory queries
│       └── procedural.py           ← PostgreSQL-stored learned instructions
├── services/
│   └── llm_service.py              ← LLM client (Anthropic SDK / OpenAI)
└── models/
    └── agent_state.py              ← AgentRun, AgentMessage, AgentMemory ORM

PostgreSQL (new tables, reuses pgvector if RAG is present)
├── agent_runs                      ← Run metadata: id, status, input, output
├── agent_messages                  ← Per-run message history (thread storage)
└── agent_memories                  ← Long-term episodic memory + vector embeddings
```

**Framework choice for early 2026:** LangGraph is the recommended orchestration layer for multi-agent systems in a FastAPI context. LangGraph 1.0 shipped October 2025 (first stable release). PydanticAI is viable for single-agent type-safe workflows but lacks ergonomic depth for complex multi-agent graphs. Both integrate cleanly with FastAPI.

#### Data Flow: Single Agent Run

```
User submits task via POST /agent/run
    ↓
FastAPI creates AgentRun record (status=running)
    ↓
Orchestrator agent receives task
    ↓
LLM decides which tool to call (tool_use block)
    ↓
FastAPI executes tool (search, code, web fetch, etc.)
    ↓
Tool result returned to LLM context
    ↓
LLM continues reasoning (may call more tools)
    ↓
LLM produces final response (end_turn)
    ↓
FastAPI updates AgentRun record (status=complete, output=response)
    ↓
Stream events to client via SSE throughout (each LLM step fires a stream event)
```

#### Data Flow: Multi-Agent Orchestration (Orchestrator/Worker)

```
Orchestrator receives complex task
    ↓
Orchestrator routes sub-tasks to specialized workers:
  Worker A: search/retrieval agent (wraps RAG skill)
  Worker B: code generation agent (sandboxed execution)
  Worker C: summarization agent (long context reduction)
    ↓
Workers run in parallel (LangGraph: parallel node execution)
    ↓
Orchestrator collects results
    ↓
Orchestrator synthesizes final response
    ↓
Single streamed output to user
```

#### Agent Memory Architecture (Three-Layer)

```
┌────────────────────────────────────────────────────────────┐
│  SHORT-TERM: context window (in-memory, per-run)           │
│  Tool: sliding window pruner, token budget enforcer        │
│  Storage: none (lost on run end)                           │
├────────────────────────────────────────────────────────────┤
│  EPISODIC: past interaction summaries (persistent)         │
│  Tool: embedding search over agent_memories table          │
│  Storage: PostgreSQL + pgvector (reuses RAG extension)     │
│  Retrieve: "find memories similar to current task"         │
├────────────────────────────────────────────────────────────┤
│  PROCEDURAL: learned instructions / user preferences       │
│  Tool: direct PostgreSQL lookup by user_id                 │
│  Storage: PostgreSQL agent_memories (type='procedural')    │
│  Retrieve: on every run start (low-latency key lookup)     │
└────────────────────────────────────────────────────────────┘
```

**Key observation:** If the RAG skill is present (pgvector extension installed), the agent memory episodic layer reuses the same vector infrastructure at zero added operational cost. The `agent_memories` table uses the same `vector(1536)` column type.

#### Streaming: Server-Sent Events (SSE) Pattern

LangGraph agents stream per-step events. FastAPI exposes them as SSE:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.get("/agent/stream/{run_id}")
async def stream_agent(run_id: str):
    async def event_generator():
        async for event in agent_graph.astream(run_id):
            yield f"data: {event.model_dump_json()}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

Next.js frontend reads the SSE stream and renders progressively — no polling needed.

#### PostgreSQL Schema (New Tables)

```sql
CREATE TABLE agent_runs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    status      VARCHAR(20) DEFAULT 'running',  -- running, complete, failed
    input       TEXT NOT NULL,
    output      TEXT,
    started_at  TIMESTAMPTZ DEFAULT now(),
    finished_at TIMESTAMPTZ
);

CREATE TABLE agent_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id      UUID NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    role        VARCHAR(20) NOT NULL,           -- user, assistant, tool
    content     JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE agent_memories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    memory_type VARCHAR(20) NOT NULL,           -- episodic, procedural, semantic
    content     TEXT NOT NULL,
    embedding   vector(1536),                   -- reuses pgvector if installed
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ON agent_memories USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

#### Integration Points with Existing Stack

| Existing Component | Change | Why |
|-------------------|--------|-----|
| `prompt-engineering` skill | **Prerequisite** — agent system prompts require structured prompt design | Agent behavior is entirely prompt-driven |
| `rag-vector-search` skill | **Synergistic** — agents use RAG as a tool; episodic memory reuses pgvector | Shared infrastructure |
| `workflow-orchestration-patterns` | Reference for durable multi-step agent loops | Temporal patterns apply to long-running agents |
| `backend-dev-guidelines` | Add agent router + SSE streaming endpoint | New FastAPI patterns |

---

## Part 3: Build Order Across All Three v1.3 Skills

### Dependency Graph

```
prompt-engineering (v1.2 — already shipped)
    └── agent-architecture depends on prompt-engineering

auth-systems (v1.2 — already shipped)
    └── stripe-payments depends on auth-systems

database-design (v1.0 — already shipped)
postgresql (v1.0 — already shipped)
    └── rag-vector-search depends on both (pgvector extension, vector columns)

rag-vector-search
    └── agent-architecture benefits from RAG (search tool, episodic memory)
```

### Recommended Build Order (v1.3)

```
Phase 1 — RAG / Vector Search
  Reason: No dependency on other v1.3 skills. Depends only on already-shipped
  database-design and postgresql skills. Produces reusable infrastructure
  (pgvector, embedding pipeline) that agent-architecture will reference.

Phase 2 — Agent Architecture
  Reason: Depends on prompt-engineering (v1.2, shipped). Benefits from
  rag-vector-search being complete (can reference its pgvector patterns for
  episodic memory). Build second so cross-references point to complete content.

Phase 3 — Stripe Payments
  Reason: Depends on auth-systems (v1.2, shipped). Has no dependency on RAG
  or agent skills. Build last to keep billing concerns isolated. Could be
  built in parallel with Phase 1 if needed — no cross-dependency with RAG.
```

**Rationale for RAG before Agent:**
Agent architecture benefits from RAG being complete because: (1) agents use RAG as a tool, (2) episodic memory references pgvector patterns. Building in this order lets the agent skill make concrete references instead of forward-referencing incomplete content.

**Rationale for Stripe last:**
Stripe has no dependency on RAG or agents. It depends only on already-shipped auth-systems. Building it last avoids any coupling to the AI stack and lets the author focus on payment-specific concerns without interleaving LLM infrastructure questions.

---

## Part 4: New vs Modified Files

### New Files (create from scratch)

```
.agent/skills/rag-vector-search/SKILL.md
.agent/skills/rag-vector-search/references/embedding-pipelines.md
.agent/skills/rag-vector-search/references/pgvector-setup.md
.agent/skills/rag-vector-search/references/retrieval-patterns.md

.agent/skills/agent-architecture/SKILL.md
.agent/skills/agent-architecture/references/multi-agent-patterns.md
.agent/skills/agent-architecture/references/memory-systems.md
.agent/skills/agent-architecture/references/tool-use-patterns.md

.agent/skills/stripe-payments/SKILL.md
.agent/skills/stripe-payments/references/checkout-sessions.md
.agent/skills/stripe-payments/references/subscriptions.md
.agent/skills/stripe-payments/references/webhooks.md
```

Total: 3 SKILL.md files + 9 reference files = **12 new files**

### Modified Files (update existing)

```
.agent/skills/INDEX.md
  — Add "Payments" category with stripe-payments row
  — Add "AI / LLM" category with rag-vector-search + agent-architecture rows
  — Add Quick Selection Guide entries

.agent/skills/pci-compliance/SKILL.md
  — Add forward-reference: "For complete Stripe integration patterns see stripe-payments"

.agent/skills/postgresql/SKILL.md
  — Add forward-reference: "For RAG/embedding pipeline patterns see rag-vector-search"

.agent/skills/workflow-orchestration-patterns/SKILL.md
  — Add forward-reference: "For LLM agent orchestration see agent-architecture"
```

Total: **4 modified files**

---

## Part 5: Architectural Patterns (Cross-Domain)

### Pattern 1: Progressive Disclosure

**What:** SKILL.md holds only decision logic, selection guidance, and quick-reference tables. Implementation details live in `references/`.

**When to use:** Always. This is the viflo skill architecture invariant.

**Trade-offs:** Requires explicit reference navigation; prevents context bloat on trigger.

### Pattern 2: Cross-Skill References via Skill Name

**What:** Skill dependencies named in SKILL.md body prose, not loaded via `@` path syntax.

**When to use:** Whenever a skill assumes prerequisite knowledge from another skill.

**Example (agent-architecture SKILL.md):**
```markdown
## Prerequisites

- `prompt-engineering` — system prompt design for agent personas and tool descriptions
- `rag-vector-search` — pgvector patterns for episodic memory (if memory layer needed)
```

### Pattern 3: Domain-Split References

**What:** One reference file per provider variant or major sub-topic, loaded only when that specific path is chosen.

**When to use:** Skills covering mutually exclusive provider variants or major independent sub-domains.

**Example (stripe-payments):**
```
references/
├── checkout-sessions.md   # One-time payments
├── subscriptions.md       # Recurring billing + customer portal
└── webhooks.md            # Event handling + idempotency
```

---

## Part 6: Anti-Patterns

### Anti-Pattern 1: Fulfilling Orders on Redirect URL

**What people do:** Mark a payment complete when the user lands on `/success?session_id=...`

**Why it's wrong:** The redirect fires even for failed/abandoned payments in some edge cases. Network drops after payment mean the user never reaches the success page.

**Do this instead:** Use `checkout.session.completed` webhook as the single source of truth. The redirect page should *read* subscription status from the DB, not *write* it.

### Anti-Pattern 2: Parsing JSON Before Webhook Signature Verification

**What people do:** Use FastAPI's automatic `Body` JSON parsing before calling `stripe.Webhook.construct_event()`.

**Why it's wrong:** JSON parsing normalizes whitespace. Stripe's signature covers the exact raw bytes it sent. Any transformation breaks HMAC verification.

**Do this instead:** Read `await request.body()` directly and pass the bytes to `construct_event()`.

### Anti-Pattern 3: Loading All Document Chunks Into Context for RAG

**What people do:** Retrieve 100+ chunks and stuff them all into the LLM prompt.

**Why it's wrong:** Context window overflow, increased cost, and degraded quality — "lost in the middle" effect means the model ignores chunks in the middle of a long context.

**Do this instead:** Retrieve 20 candidates via hybrid search, apply RRF fusion, pass only the top 5 to the LLM. This outperforms larger context stuffing on precision.

### Anti-Pattern 4: Blocking FastAPI on LLM Generation

**What people do:** Run the full LLM generation call synchronously and return the entire response as a JSON body.

**Why it's wrong:** LLM generation takes 5-30 seconds. Blocking a FastAPI worker thread that long under any real load causes timeouts and terrible UX.

**Do this instead:** Use `StreamingResponse` with `text/event-stream` for SSE. The frontend reads progress as it arrives; the server never blocks.

### Anti-Pattern 5: Splitting One Skill Across Multiple SKILL.md Files

**What people do:** Create `rag-openai/SKILL.md` and `rag-pgvector/SKILL.md` as separate top-level skills.

**Why it's wrong:** Doubles INDEX.md surface area for one conceptual domain. Agents must choose between two skills at discovery time instead of at implementation time.

**Do this instead:** Single `rag-vector-search/SKILL.md` with provider selection table at top, then "for pgvector see references/pgvector-setup.md / for Pinecone see references/pinecone-setup.md."

---

## Sources

- Direct inspection of `.agent/skills/` directory — HIGH confidence (first-party)
- Stripe official documentation (docs.stripe.com/billing, docs.stripe.com/webhooks) — HIGH confidence
- Implementing Stripe Subscriptions with FastAPI — [Medium, Ojas Kapre](https://medium.com/@ojasskapre/implementing-stripe-subscriptions-with-supabase-next-js-and-fastapi-666e1aada1b5) — MEDIUM confidence
- Stripe webhooks idempotency and reliability — [Stigg blog](https://www.stigg.io/blog-posts/best-practices-i-wish-we-knew-when-integrating-stripe-webhooks) — MEDIUM confidence
- pgvector official README — [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) — HIGH confidence
- pgvector-python SQLAlchemy integration — [github.com/pgvector/pgvector-python](https://github.com/pgvector/pgvector-python) — HIGH confidence
- Building Hybrid Search with pgvector + RRF — [DEV Community, lpossamai](https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk) — MEDIUM confidence
- FastAPI + RAG backend with pgvector — [Medium, fredyriveraacevedo13](https://medium.com/@fredyriveraacevedo13/building-a-fastapi-powered-rag-backend-with-postgresql-pgvector-c239f032508a) — MEDIUM confidence
- Streaming AI Agent with FastAPI + LangGraph — [DEV Community, kasi_viswanath](https://dev.to/kasi_viswanath/streaming-ai-agent-with-fastapi-langgraph-2025-26-guide-1nkn) — MEDIUM confidence
- LangGraph 1.0 release (October 2025) — [langwatch.ai framework comparison](https://langwatch.ai/blog/best-ai-agent-frameworks-in-2025-comparing-langgraph-dspy-crewai-agno-and-more) — MEDIUM confidence
- AI Agent Memory Architecture — [MarkTechPost, Feb 2026](https://www.marktechpost.com/2026/02/01/how-to-build-memory-driven-ai-agents-with-short-term-long-term-and-episodic-memory/) — MEDIUM confidence
- Agent persistent memory into PostgreSQL — [Tiger Data](https://www.tigerdata.com/learn/building-ai-agents-with-persistent-memory-a-unified-database-approach) — MEDIUM confidence
- AI Agent Architecture patterns — [Redis blog, 2026](https://redis.io/blog/ai-agent-architecture/) — MEDIUM confidence
- Azure Architecture Center: AI Agent Design Patterns — [Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) — HIGH confidence

---

*Architecture research for: viflo v1.3 Expert Skills (Stripe, RAG, Agent Architecture)*
*Researched: 2026-02-24*

---
---

# Architecture Research — v1.4 Addition: `viflo init` CLI

**Domain:** CLI tooling — `viflo init` command for an existing agentic dev methodology toolkit
**Researched:** 2026-02-24
**Confidence:** HIGH

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        viflo repo (source of truth)                  │
│                                                                       │
│  bin/viflo.cjs          .agent/skills/          scripts/             │
│  ┌─────────────┐        ┌──────────────┐        ┌──────────────┐    │
│  │ CLI entry   │        │ 42 SKILL.md  │        │ setup-dev.sh │    │
│  │ --minimal   │        │ dirs         │        │ log-telemetry│    │
│  │ --full      │        │ INDEX.md     │        └──────────────┘    │
│  │ idempotency │        └──────────────┘                            │
│  └──────┬──────┘                                                     │
│         │ resolves self via __dirname                                │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          │ invoked from target project directory (process.cwd())
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     target project (cwd)                             │
│                                                                       │
│  CLAUDE.md              .claude/                  .planning/         │
│  ┌─────────────┐        ┌──────────────────────┐  ┌──────────────┐  │
│  │ @import     │        │ settings.json        │  │ PROJECT.md   │  │
│  │ stanza for  │        │ merged permissions   │  │ ROADMAP.md   │  │
│  │ viflo skills│        │ + env keys           │  │ STATE.md     │  │
│  │             │        └──────────────────────┘  │ config.json  │  │
│  └─────────────┘                                  └──────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Option Decision: Where Does `viflo init` Live?

**Recommendation: Option B — `bin/viflo.cjs` with package.json bin field.**

| Option | Verdict | Rationale |
|--------|---------|-----------|
| A: `scripts/viflo-init.sh` | Reject | Cannot safely manipulate JSON. No cross-platform guarantee for sed/awk between BSD and GNU. No test path. |
| B: `bin/viflo.cjs` | **Choose this** | Matches gsd-tools.cjs pattern already proven in this ecosystem. Node.js is already the runtime. JSON.parse/stringify is native and safe. Testable via Vitest. `__dirname` gives self-referential path resolution. |
| C: `packages/cli/` | Defer | Adds TypeScript compilation, build pipeline, and workspace publish step before the CLI shape is proven. Premature complexity. Extract here in a future milestone if warranted. |

## Recommended Project Structure

```
viflo/
├── bin/
│   ├── viflo.cjs              # CLI entry: #!/usr/bin/env node, argument routing
│   └── lib/
│       ├── init.cjs           # init command logic (--minimal, --full)
│       ├── paths.cjs          # viflo install dir resolution, OS path utilities
│       └── writers.cjs        # file write/merge operations
├── package.json               # add "bin": { "viflo": "bin/viflo.cjs" }
│                              # add "files": ["bin/", ".agent/"] for npm publish
├── .agent/
│   └── skills/                # source of truth, referenced by absolute path
├── scripts/                   # existing shell scripts — no changes
└── apps/, packages/           # existing workspace members — no changes
```

### Structure Rationale

- **bin/viflo.cjs:** Mirrors gsd-tools.cjs pattern. `#!/usr/bin/env node` shebang, CommonJS (not ESM), no compilation required. Executable via `node bin/viflo.cjs` during development and `viflo` after `npm link`.
- **bin/lib/:** Keeps the entry point thin (routing only). Individual modules are single-concern. Tests can `require()` individual lib modules without loading the full CLI.
- **`packages/` NOT used:** bin/ is not a workspace package. pnpm-workspace.yaml covers `apps/*` and `packages/*` — bin/ sits outside workspace scope, which is correct for a root-level CLI tool.

## Component Responsibilities

| Component | Responsibility | Communicates With |
|-----------|----------------|-------------------|
| `bin/viflo.cjs` | Argument parsing, subcommand routing, user-facing stdout | bin/lib/init.cjs |
| `bin/lib/init.cjs` | Orchestrates --minimal and --full flows, idempotency logic | paths.cjs, writers.cjs |
| `bin/lib/paths.cjs` | Self-referential viflo root resolution via `__dirname`, OS-agnostic path construction | Node.js `path`, `os` |
| `bin/lib/writers.cjs` | CLAUDE.md sentinel-aware merge, settings.json JSON merge, .planning/ scaffold | Node.js `fs` |

## Architectural Patterns

### Pattern 1: Self-Referential Install Dir Resolution

**What:** The CLI derives the viflo repo root from `__dirname` at runtime — no env variable, no config file.

**When to use:** At startup, before any writes. Compute once, pass down to all writers.

**Trade-offs:** `__dirname` only works in CommonJS (`.cjs`), not ESM (`.mjs`). This is the primary reason the file must be `.cjs`. After `npm install -g viflo`, `__dirname` points to the npm global install location, and `.agent/skills/` ships inside the package via the `"files"` key — so the path resolution remains correct post-install.

```javascript
// bin/lib/paths.cjs
const path = require('path');

function getVifloRoot() {
  // bin/lib/paths.cjs → up two levels to repo root
  return path.resolve(__dirname, '..', '..');
}

function getSkillsDir() {
  return path.join(getVifloRoot(), '.agent', 'skills');
}

function getTargetClaudeSettingsPath(targetDir) {
  // Project-level: <target>/.claude/settings.json
  // Per Claude Code docs: https://code.claude.com/docs/en/settings
  return path.join(targetDir, '.claude', 'settings.json');
}

function getTargetClaudeMdPath(targetDir) {
  // Write to CLAUDE.md at project root (most visible, most conventional)
  // Claude Code also supports .claude/CLAUDE.md but root is preferred
  return path.join(targetDir, 'CLAUDE.md');
}
```

### Pattern 2: Idempotent Sentinel-Based CLAUDE.md Merge

**What:** The CLI wraps its CLAUDE.md stanza in HTML comment sentinels. On re-run, it detects the markers and replaces the block rather than appending again.

**When to use:** Every write to CLAUDE.md. Satisfies INIT-04 (idempotency).

**Trade-offs:** The sentinel format must be stable across viflo versions. Adding a version to the sentinel (e.g. `<!-- viflo:v1.4:start -->`) enables future migration between versions but adds complexity. Start without versioning.

```javascript
// bin/lib/writers.cjs
const VIFLO_SENTINEL_START = '<!-- viflo:start -->';
const VIFLO_SENTINEL_END = '<!-- viflo:end -->';

function mergeClaudeMd(existingContent, vifloStanza) {
  const wrappedStanza = `${VIFLO_SENTINEL_START}\n${vifloStanza}\n${VIFLO_SENTINEL_END}`;

  if (existingContent.includes(VIFLO_SENTINEL_START)) {
    // Replace existing viflo block in-place (idempotent re-run)
    const pattern = new RegExp(
      `${VIFLO_SENTINEL_START}[\\s\\S]*?${VIFLO_SENTINEL_END}`,
      'g'
    );
    return existingContent.replace(pattern, wrappedStanza);
  }
  // First run: append to existing content (preserves all non-viflo content)
  return existingContent.trimEnd() + '\n\n' + wrappedStanza + '\n';
}
```

### Pattern 3: CLAUDE.md @import Stanza for Viflo Skills

**What:** Claude Code supports `@path/to/file` syntax in CLAUDE.md to import external skill files at session start. `viflo init` writes a stanza with the absolute path to each skill's SKILL.md in the viflo install directory.

**When to use:** This is the primary integration mechanism. It makes viflo skills available in any target project without copying files.

**Trade-offs:**
- Absolute paths tie the stanza to the current viflo install location. If the user moves the viflo repo, the stanza breaks. `viflo init` is idempotent (re-running updates the stanza with the new path).
- Claude Code shows a one-time approval dialog when it first encounters `@` imports from an external absolute path. This is documented behavior. The CLI should warn the user about this with a note in stdout.
- Imports are not evaluated inside markdown code spans or code blocks — the sentinel HTML comments do not interfere.

**Example output written to target project CLAUDE.md:**
```markdown
<!-- viflo:start -->
## Viflo Skills

Access the full viflo skill library:

@/home/user/tools/viflo/.agent/skills/gsd-workflow/SKILL.md
@/home/user/tools/viflo/.agent/skills/frontend/SKILL.md
@/home/user/tools/viflo/.agent/skills/backend-dev-guidelines/SKILL.md
@/home/user/tools/viflo/.agent/skills/database-design/SKILL.md
<!-- viflo:end -->
```

**Note:** The stanza can list all 42 skill SKILL.md files, or a curated subset. Listing all is simpler and avoids a skills selection UX. Claude Code loads files lazily (child CLAUDE.md files only when Claude reads in that directory), so listing all 42 does not bloat every context window.

### Pattern 4: settings.json JSON Merge

**What:** `.claude/settings.json` in the target project is a standard JSON file. The CLI reads it if it exists, merges viflo-required keys, deduplicates the `permissions.allow` array, and writes it back.

**When to use:** Every run. The merge is safe to repeat (idempotent).

**Trade-offs:** Write atomically (write to temp file, `fs.renameSync` to final path) to avoid corrupt JSON if the process is killed mid-write.

```javascript
// bin/lib/writers.cjs
const VIFLO_PERMISSIONS = [
  // Allow reading viflo skill files via WebFetch if needed
  // (Claude Code uses file:// for local paths — usually no permission needed)
  // Primary use: ensure no restrictive default blocks skill file access
];

function mergeClaudeSettings(existingJson, vifloRoot) {
  const existing = existingJson ? JSON.parse(existingJson) : {};
  const merged = { ...existing };

  // Ensure permissions key exists
  if (!merged.permissions) merged.permissions = {};
  if (!merged.permissions.allow) merged.permissions.allow = [];

  // Deduplicate: add viflo entries not already present
  const currentAllow = new Set(merged.permissions.allow);
  for (const entry of VIFLO_PERMISSIONS) {
    currentAllow.add(entry);
  }
  merged.permissions.allow = [...currentAllow];

  return JSON.stringify(merged, null, 2) + '\n';
}
```

## Settings.json and CLAUDE.md Paths — Platform Reference

**Confidence: HIGH.** Sourced from [Claude Code official docs](https://code.claude.com/docs/en/settings) and [memory docs](https://code.claude.com/docs/en/memory), verified 2026-02-24.

| Platform | Global user settings (DO NOT write here) | Project settings (viflo init writes here) |
|----------|------------------------------------------|-------------------------------------------|
| Linux | `~/.claude/settings.json` | `<target>/.claude/settings.json` |
| macOS | `~/.claude/settings.json` | `<target>/.claude/settings.json` |
| Windows | `~/.claude/settings.json` | `<target>/.claude/settings.json` |

| Platform | CLAUDE.md project location (viflo init writes here) |
|----------|-----------------------------------------------------|
| Linux / macOS / Windows | `<target>/CLAUDE.md` (preferred) or `<target>/.claude/CLAUDE.md` |

`viflo init` writes only to project-level files in `process.cwd()`. It never touches `~/.claude/settings.json` or `~/.claude/CLAUDE.md`.

## Data Flow

### --minimal mode

```
viflo init --minimal
    │ (run from target project directory)
    │
    ▼
[paths.cjs] getVifloRoot() via __dirname
    │  → vifloRoot = /path/to/viflo
    │  → skillsDir  = /path/to/viflo/.agent/skills
    │  → targetDir  = process.cwd()
    │
    ▼
[writers.cjs] read targetDir/CLAUDE.md (create empty string if absent)
    │  → detect VIFLO_SENTINEL_START
    │  → replace or append viflo stanza with @import lines per SKILL.md
    │  → write CLAUDE.md
    │
    ▼
[writers.cjs] read targetDir/.claude/settings.json (create {} if absent)
    │  → fs.mkdirSync('.claude', { recursive: true })
    │  → merge permissions.allow (deduplicate)
    │  → write atomically via tmp + rename
    │
    ▼
stdout:
  "viflo init complete.
   CLAUDE.md: updated with viflo skill imports.
   .claude/settings.json: permissions merged.
   Note: Claude Code will show a one-time approval dialog for @imports on first use."
```

### --full mode (superset of --minimal)

```
[same as --minimal — CLAUDE.md + settings.json]
    │
    ▼
[init.cjs] scaffold .planning/ directory
    │  → fs.mkdirSync('.planning', { recursive: true })
    │  → for each template file:
    │      if file does not exist: write stub from viflo template
    │      if file exists: skip (idempotent — never overwrite)
    │  → files written: PROJECT.md, ROADMAP.md, STATE.md, config.json
    │
    ▼
[init.cjs] write starter CLAUDE.md project section (if CLAUDE.md is brand new)
    │  → only if CLAUDE.md did not exist before this run
    │  → prepends project-specific sections above the viflo sentinel block
    │
    ▼
stdout:
  "viflo init --full complete.
   .planning/ scaffolded with GSD template stubs.
   Run 'viflo init --minimal' on subsequent runs to update skill paths only."
```

## Integration Points

### New Files in Viflo Repo

| File | Type | Purpose |
|------|------|---------|
| `bin/viflo.cjs` | NEW | CLI entry point with argument parsing |
| `bin/lib/init.cjs` | NEW | --minimal/--full orchestration, idempotency logic |
| `bin/lib/paths.cjs` | NEW | Path resolution — viflo root, skills dir, target paths |
| `bin/lib/writers.cjs` | NEW | File write/merge — CLAUDE.md sentinel merge, settings.json JSON merge |

### Modified Files in Viflo Repo

| File | Change | Why |
|------|--------|-----|
| `package.json` | Add `"bin": { "viflo": "bin/viflo.cjs" }` | Registers CLI as npm executable |
| `package.json` | Add `"files": ["bin/", ".agent/", "scripts/"]` | Ensures skills ship in npm package |

### Files Written to Target Project by viflo init

| File | Mode | Action |
|------|------|--------|
| `CLAUDE.md` | --minimal + --full | Sentinel merge: adds/updates viflo @import block |
| `.claude/settings.json` | --minimal + --full | JSON merge: adds viflo permissions to allow array |
| `.planning/PROJECT.md` | --full only | Create-if-absent: GSD project stub |
| `.planning/ROADMAP.md` | --full only | Create-if-absent: GSD roadmap stub |
| `.planning/STATE.md` | --full only | Create-if-absent: GSD state stub |
| `.planning/config.json` | --full only | Create-if-absent: GSD config with model defaults |

### Files Never Modified by viflo init

- `~/.claude/settings.json` — user-level, out of scope
- `~/.claude/CLAUDE.md` — user-level, out of scope
- Any CLAUDE.md content outside the `<!-- viflo:start -->` / `<!-- viflo:end -->` block
- Any existing `.planning/` files (create-if-absent, never overwrite)

## Build Order for v1.4 Implementation

Dependencies flow from bottom up:

1. **`bin/lib/paths.cjs`** — No dependencies. Path utilities only. All other lib modules depend on this.

2. **`bin/lib/writers.cjs`** — Depends on paths.cjs. Implements CLAUDE.md merge and settings.json merge.

3. **`bin/lib/init.cjs`** — Depends on paths.cjs + writers.cjs. Implements --minimal and --full orchestration with idempotency.

4. **`bin/viflo.cjs`** — Depends on init.cjs. CLI entry point: `#!/usr/bin/env node`, `process.argv` parsing, routes to init.

5. **`package.json` modification** — Wire `"bin"` field. Can be done at step 4 but logically final.

6. **Tests** — Vitest tests for each lib module. `require()` individual modules. Test paths.cjs with mock `__dirname`, test writers.cjs with temp directories, test init.cjs end-to-end against a temp project dir.

## Anti-Patterns

### Anti-Pattern 1: Shell Script for JSON Manipulation

**What people do:** Implement as `scripts/viflo-init.sh` using sed/awk to write settings.json.

**Why it's wrong:** JSON manipulation in shell is fragile — no safe array deduplication, special characters in paths break sed patterns, BSD vs GNU awk behavioral differences.

**Do this instead:** `bin/viflo.cjs` with `JSON.parse` / `JSON.stringify`. The runtime exists; use it.

### Anti-Pattern 2: Hardcoding the Viflo Install Path

**What people do:** Document "set VIFLO_DIR=~/tools/viflo" and read from env.

**Why it's wrong:** Breaks when users clone to non-standard paths. Adds setup friction. Env var is undiscoverable.

**Do this instead:** Use `__dirname` in `bin/lib/paths.cjs`. The file is always at `<viflo-root>/bin/lib/paths.cjs`, so `path.resolve(__dirname, '..', '..')` is the viflo root with zero configuration.

### Anti-Pattern 3: Appending CLAUDE.md Without Sentinel Guards

**What people do:** Append the stanza on every run without checking for existing content.

**Why it's wrong:** Violates INIT-04. Running `viflo init` twice produces duplicate blocks. Moving the viflo repo and re-running leaves stale paths alongside fresh ones.

**Do this instead:** Sentinel markers `<!-- viflo:start -->` / `<!-- viflo:end -->`. Detect on read, replace in-place on write.

### Anti-Pattern 4: Writing to ~/.claude/settings.json

**What people do:** Modify global user settings to grant skill permissions.

**Why it's wrong:** Wrong scope. Pollutes settings that apply to all projects. `viflo init` is a per-project operation.

**Do this instead:** Write only to `<target-project>/.claude/settings.json`. Per Claude Code docs, this is the correct project-level location.

### Anti-Pattern 5: Premature packages/cli/ Package (Option C)

**What people do:** Create a TypeScript workspace package with compilation and publish pipeline before the CLI shape is proven.

**Why it's wrong:** Compilation step, tsconfig, build scripts, and CI changes before requirements are stable. Over-engineering relative to the problem.

**Do this instead:** Start with `bin/viflo.cjs`. The gsd-tools.cjs reference pattern confirms plain CJS is production-sufficient. Migrate to `packages/cli/` in a future milestone when TypeScript type safety or complexity justifies it.

## Invocation Patterns

```bash
# Development (from within viflo repo, targeting any project)
cd /path/to/my-project
node /path/to/viflo/bin/viflo.cjs init --minimal
node /path/to/viflo/bin/viflo.cjs init --full

# After npm link (recommended for local development)
# Run once from viflo repo root:
npm link
# Then from any project:
viflo init --minimal
viflo init --full

# After npm install -g (end-user install)
npm install -g viflo
# or install from local path:
npm install -g /path/to/viflo
viflo init --minimal
viflo init --full
```

**Target directory:** Always `process.cwd()`. The user runs `viflo init` from inside their project — standard shell convention. No `--target-dir` flag needed at this stage.

## Scaling Considerations

| Scenario | Adjustment Needed |
|----------|-------------------|
| Single developer, local clone | Current design is complete. `npm link` for development use. |
| Team with shared viflo fork | Add optional `--skills-dir <path>` flag to override. Low effort addition. |
| Distributed npm package | Ensure `.agent/` is in `"files"` in package.json. `__dirname` resolves to npm install location. Skills ship with the package. No change to core logic. |
| Multiple viflo versions in use | Extend sentinel to `<!-- viflo:v1.4:start -->` for version-aware updates. Defer until needed. |

## Sources

- Claude Code settings file paths: [https://code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings) — HIGH confidence (official docs, 2026-02-24)
- Claude Code CLAUDE.md memory and @import syntax: [https://code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) — HIGH confidence (official docs, 2026-02-24)
- gsd-tools.cjs reference CLI pattern: `/home/ollie/.claude/get-shit-done/bin/gsd-tools.cjs` — HIGH confidence (direct inspection)
- viflo existing repo structure: `/home/ollie/Development/Tools/viflo/` — HIGH confidence (direct inspection)
- Node.js `__dirname` in CommonJS vs ESM: stable behavior, HIGH confidence

---

*Architecture research for: viflo init CLI (v1.4)*
*Researched: 2026-02-24*
