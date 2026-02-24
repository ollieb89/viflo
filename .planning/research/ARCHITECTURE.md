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
