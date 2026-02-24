# Stack Research

**Domain:** viflo v1.3 Expert Skills — Stripe Payments, RAG/Vector Search, Agent Architecture
**Researched:** 2026-02-24
**Confidence:** HIGH (all versions verified against npm/PyPI/official sources on 2026-02-24)

> **Scope note:** This file covers only the three NEW skill domains for v1.3. Auth Systems and Prompt Engineering are already shipped at v1.2 depth; their stack entries were retained in the previous revision but are excluded here to keep this document tightly scoped to what the skill authors need for v1.3.

---

## Skill 1: Stripe Payments

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `stripe` (Node.js) | ^20.3.1 | Server-side Stripe API client | Official SDK; handles checkout sessions, subscriptions, invoices, webhook signature verification. Full TypeScript types included. Pinned to API version `2026-01-28` by default in v20. |
| `@stripe/stripe-js` | ^8.8.0 | Client-side Stripe.js CDN loader | Lazy-loads Stripe.js from Stripe's CDN; required for PCI-compliant payment UI. v8 is the current major — do NOT use v5 or earlier (old types). |
| `@stripe/react-stripe-js` | ^5.6.0 | React wrapper for Stripe Elements | Provides `<Elements>`, `<CardElement>`, `<PaymentElement>` components compatible with React 19 and Next.js 16. |
| `stripe` (Python) | ^14.3.0 | Server-side Stripe API for FastAPI backends | Official Stripe Python SDK; use for webhook processing in FastAPI or async billing logic. Released 2026-01-28. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Raw body config | n/a (config, not a package) | Webhook signature verification requires raw request body | ALWAYS — in Next.js App Router use `await request.text()` before parsing; in FastAPI use `Request.body()` before JSON decode |
| `stripe[async]` (Python) | ^14.3.0 | Async HTTP support for the Python SDK | Install with `pip install stripe[async]` when using `AsyncStripe` in FastAPI async handlers |

### Installation

```bash
# Server-side (Next.js Route Handlers)
npm install stripe

# Client-side (React checkout UI)
npm install @stripe/stripe-js @stripe/react-stripe-js

# Server-side (FastAPI)
pip install stripe          # sync
pip install "stripe[async]" # async handlers
```

### Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `stripe` official SDK | `@lemonsqueezy/lemonsqueezy.js` | Lemon Squeezy for digital products with simpler pricing; Stripe is required for custom billing logic and global coverage |
| Stripe hosted Checkout | Custom payment form with `CardElement` | Hosted Checkout simplest to launch; custom form needed when checkout must be embedded in-app |
| Stripe Customer Portal | Custom subscription management UI | Portal handles plan changes/cancellations for free; build custom UI only when brand consistency is critical |

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `stripe@<16` | Locks to deprecated API versions; missing TypeScript improvements and idempotency auto-retry | `stripe@^20` |
| `@stripe/stripe-js@<8` | v5/v6 types misalign with `stripe` Node SDK v20 APIs | `@stripe/stripe-js@^8.8.0` |
| Parsing webhook body as JSON before verification | Destroys raw buffer; `stripe.webhooks.constructEvent()` will throw | `await request.text()` (Next.js) or `await request.body()` (FastAPI) before verification |
| Storing card numbers or CVV anywhere | PCI DSS violation — Stripe Elements keeps card data off your servers | Always use `<PaymentElement>` or hosted Checkout |
| Trusting `payment_intent.succeeded` from the client | Client can be spoofed | Verify only from Stripe webhook events server-side |

### Stack Patterns by Variant

**One-time payments (e-commerce checkout):**
- Use Stripe Checkout (hosted) for fastest launch, or `<PaymentElement>` embedded for in-page feel
- `payment_intent` flow: create intent server-side → client confirms → webhook fulfills

**Recurring subscriptions (SaaS billing):**
- Use `subscription` objects with Stripe `price` IDs
- Combine with `stripe.billingPortal.sessions.create()` for self-serve plan management
- Sync subscription state to your DB on `customer.subscription.updated` and `customer.subscription.deleted` webhook events

**Webhooks in Next.js App Router (current viflo stack):**
```typescript
// app/api/webhooks/stripe/route.ts
export async function POST(request: Request) {
  const body = await request.text(); // raw body — critical
  const sig = request.headers.get('stripe-signature')!;
  const event = stripe.webhooks.constructEvent(
    body, sig, process.env.STRIPE_WEBHOOK_SECRET!
  );
  // route on event.type
}
```

**Webhooks in FastAPI:**
```python
@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()  # raw bytes
    sig = request.headers.get("stripe-signature", "")
    event = stripe.Webhook.construct_event(body, sig, STRIPE_WEBHOOK_SECRET)
    # route on event["type"]
```

### Version Compatibility

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| `stripe` (Node.js) | ^20.3.1 | Node.js 16+ | Node 20+ recommended; matches viflo stack |
| `@stripe/react-stripe-js` | ^5.6.0 | React 16.8+, React 19 | Compatible with viflo's React 19 |
| `@stripe/stripe-js` | ^8.8.0 | All modern browsers | v8 required to match stripe Node SDK v20 type signatures |
| `stripe` (Python) | ^14.3.0 | Python 3.7+ | viflo uses Python 3.11+ — fully compatible |

---

## Skill 2: RAG / Vector Search

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `pgvector` (Python) | ^0.4.2 | pgvector driver for Python (SQLAlchemy, asyncpg, psycopg3) | Keeps vector search inside existing PostgreSQL — no extra managed service for projects under ~50M vectors. Integrates directly with FastAPI/SQLAlchemy 2.0 already in the viflo stack. |
| `pgvector` (Node.js) | ^0.2.1 | pgvector driver for Node.js/TypeScript | For Next.js Route Handler retrieval pipelines that query vectors without a Python service hop |
| `openai` (Python) | ^1.x (latest: 6.22.0 via npm; Python package uses separate versioning) | OpenAI Embeddings API | Standard embedding provider — `text-embedding-3-small` is the default recommendation (1536 dims, ~$0.02/1M tokens) |
| `@pinecone-database/pinecone` | ^7.1.0 | Managed Pinecone vector DB client | Use when scale exceeds pgvector's sweet spot (>50M vectors) or when fully managed latency SLAs are required |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `langchain-community` (Python) | ^0.3.x | PGVector `VectorStore` integration for LangChain RAG chains | When building full LangChain RAG pipelines — wraps pgvector in LangChain's retriever interface |
| `langchain-openai` (Python) | ^0.3.x | LangChain OpenAI embedding wrapper | Needed when using LangChain's `OpenAIEmbeddings` class in a chain |
| `anthropic` (Python) | ^0.83.0 | Claude as the generator in RAG retrieve-then-generate | When using Claude Sonnet/Opus as the generation step |
| `ai` (Vercel AI SDK) | ^6.x | Streaming RAG responses in Next.js | `useChat` + `streamText` with retrieval tool calls gives real-time streaming UX for RAG chatbots |

### Embedding Model Recommendation

| Model | Dimensions | Cost (per 1M tokens) | When to Use |
|-------|------------|----------------------|-------------|
| `text-embedding-3-small` | 1536 | ~$0.02 | Default — strong performance, low cost, fits pgvector well at small-to-medium scale |
| `text-embedding-3-large` | 3072 | ~$0.13 | High-recall use cases (legal, medical, support) where cost is secondary to retrieval precision |

Both models support the `dimensions` API parameter to shorten embeddings without losing concept representation — useful for reducing storage.

### Installation

```bash
# Python (FastAPI RAG backend)
pip install pgvector anthropic openai langchain-community langchain-openai

# Node.js (Next.js retrieval helpers)
npm install pgvector

# Pinecone (optional — use only when pgvector is insufficient)
npm install @pinecone-database/pinecone
# or
pip install pinecone
```

### Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| pgvector (default for viflo stack) | Pinecone | >50M vectors, managed SLA required, no Postgres ops available |
| pgvector | Qdrant | Complex metadata filtering at scale — Qdrant's payload filtering is best-in-class and maintains recall under selective filters; pgvector recall degrades with complex filters |
| pgvector | Weaviate | Hybrid search (dense + BM25 keyword) in a single query — Weaviate supports this natively; not worth the ops overhead at small scale |
| `text-embedding-3-small` | `text-embedding-3-large` | When retrieval recall is critical (legal/medical/enterprise search) and the 6.5x cost increase is justified |

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| pgvector with `ivfflat` index beyond 1M vectors without `pgvectorscale` | `ivfflat` index degrades at scale — recall drops and exact KNN is slow | Add `pgvectorscale` extension or migrate to Pinecone/Qdrant |
| Embedding entire documents as a single vector | Long chunks reduce retrieval precision — a 10K-token document gets averaged into noise | Chunk to 512–1024 tokens with 10–15% overlap |
| Storing raw LLM-generated text in the vector store | Embeddings should represent source content, not generated text | Embed original document chunks only |
| `text-embedding-ada-002` | Deprecated; `text-embedding-3-small` outperforms it at lower cost | `text-embedding-3-small` |
| Cosine similarity without normalizing vectors first | Produces subtly wrong results unless vectors are normalized | Normalize at embed time or use pgvector's `<=>` cosine operator which handles it |

### Stack Patterns by Variant

**Building on existing viflo PostgreSQL stack (recommended for MVP):**
- Use pgvector Python client + SQLAlchemy 2.0 async
- Add `CREATE EXTENSION IF NOT EXISTS vector;` to your first migration
- Store embeddings as `VECTOR(1536)` column alongside existing data
- Use HNSW index for production (better recall vs IVFFlat): `CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);`

**When scale or managed infra is required:**
- Replace pgvector with `@pinecone-database/pinecone` v7 or `pinecone` Python SDK
- Keep the same retrieval interface — the pattern is identical, only the client changes

**RAG pipeline stages (standard pattern):**
1. Ingest: chunk documents → embed chunks → store in pgvector
2. Retrieve: embed query → cosine search top-k → return chunks with metadata
3. Generate: inject chunks into prompt context → call LLM → stream response

### Version Compatibility

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| `pgvector` (Python) | ^0.4.2 | SQLAlchemy 2.0, psycopg3, asyncpg | Matches viflo's SQLAlchemy 2.0 stack |
| `pgvector` (Node.js) | ^0.2.1 | Node.js 18+, TypeScript 5+ | Works with `pg` driver (node-postgres) |
| `@pinecone-database/pinecone` | ^7.1.0 | TypeScript >=5.2, Node.js >=20 | Fits viflo's TS 5.7+ and Node 20+ |
| `langchain-community` | ^0.3.x | Python >=3.10 | viflo uses Python 3.11+ — compatible |

---

## Skill 3: Agent Architecture

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `@anthropic-ai/sdk` (TypeScript) | ^0.78.0 | Anthropic Claude API — tools, streaming, multi-turn | Official SDK; supports tool use, extended thinking, streaming, vision. Use for direct Claude-based agent construction without framework overhead. Async-native. |
| `anthropic` (Python) | ^0.83.0 | Same as above for FastAPI agent backends | `AsyncAnthropic` client works natively with FastAPI's async handlers. DO NOT use synchronous `Anthropic` client in async FastAPI routes. |
| `@anthropic-ai/claude-agent-sdk` | ^0.2.49 | Programmatic Claude Code / agentic SDK | Specialized SDK for agents that control file systems and run commands. Powers Claude Code itself. Relevant for viflo's own GSD workflow agentic tooling. |
| `ai` (Vercel AI SDK) | ^6.x | Unified LLM SDK for Next.js streaming + agents | Best DX for streaming agent UI in Next.js — `useChat`, `useCompletion`, `streamText`, tool execution, MCP support. Abstracts over Anthropic/OpenAI/Gemini SDKs. |
| `@langchain/langgraph` | ^1.1.5 | Stateful multi-agent graph orchestration | Use for complex multi-step agent workflows requiring explicit state transitions, checkpointing, and human-in-the-loop. Production-ready as of 2026. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `@ai-sdk/anthropic` | ^1.x | Vercel AI SDK Anthropic provider | Required when using Vercel AI SDK with Claude models — sits between `ai` and `@anthropic-ai/sdk` |
| `@langchain/langgraph-sdk` | ^1.6.2 | LangGraph client SDK | When running LangGraph server separately from the Next.js app; connect to hosted graph endpoint |
| `langchain` (Python) | ^0.5.x | Python orchestration for agent chains | FastAPI agent backends needing complex chain composition or LangChain's built-in tool library |
| `langchain-core` (Python) | ^0.3.x | Core primitives for LangChain (runnable, schema) | Always install with `langchain` — it's the shared interface layer |
| `openai` (npm) | ^4.x | OpenAI API client | When agents need to use GPT-4o or o3 alongside Claude (multi-model agent patterns) |

### Installation

```bash
# TypeScript / Next.js — direct Claude agents
npm install @anthropic-ai/sdk

# TypeScript / Next.js — streaming agent UI
npm install ai @ai-sdk/anthropic

# TypeScript / Next.js — stateful multi-step agents
npm install @langchain/langgraph @langchain/langgraph-sdk

# TypeScript — autonomous code/file-system agents (viflo GSD tooling)
npm install @anthropic-ai/claude-agent-sdk

# Python / FastAPI — Claude agents
pip install anthropic

# Python / FastAPI — LangChain agent pipelines
pip install langchain langchain-core
```

### Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Vercel AI SDK (`ai`) for Next.js agent UI | Direct `@anthropic-ai/sdk` | Use direct SDK when you don't need streaming hooks, multi-provider switching, or built-in tool call rendering |
| `@langchain/langgraph` for multi-agent | CrewAI | CrewAI ships production faster for role-based team workflows (40% less boilerplate); LangGraph is better for stateful, conditional branching pipelines where you need control |
| `@langchain/langgraph` for multi-agent | Custom orchestrator | Build custom only if LangGraph's graph model doesn't map to your workflow — LangGraph's checkpointing and human-in-the-loop are hard to replicate |
| `anthropic` SDK direct | OpenAI Agents SDK | Use OpenAI SDK if the project is committed to GPT-4o / o3; Anthropic SDK for Claude-first development |
| Mastra (`@mastra/core`) | — | Mastra v1.6 is production-ready (Feb 2026, Gatsby team) — worth evaluating as an alternative to LangGraph for TypeScript-first workflows; not yet as widely adopted |

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `langchain` (Python or JS) for simple single-turn completions | Massive abstraction overhead for a 5-line API call; debugging is painful | Direct `@anthropic-ai/sdk` or `ai` |
| Synchronous `Anthropic` Python client in FastAPI | Blocks the async event loop — kills concurrency and throughput | `AsyncAnthropic` client |
| Storing full conversation history in process memory | Agent state lost on restart; in multi-user apps, sessions corrupt each other | PostgreSQL-backed session store or LangGraph checkpointer |
| LangGraph for every agent use case | LangGraph adds significant complexity — state machines, graph topology, edge conditions | Use LangGraph only when the workflow has multiple conditional branches and persistent state; use Vercel AI SDK tools for simpler pipelines |
| `langchain` v0.1.x (Python) | Old API surface (pre-LCEL), being deprecated in 2026 | `langchain` ^0.5.x with LCEL (`RunnableSequence`) |

### Stack Patterns by Variant

**Building agent UI in Next.js (streaming chat, live tool call display):**
- Use Vercel AI SDK v6 (`ai` + `@ai-sdk/anthropic`)
- `useChat` hook + `streamText` with tool definitions handles 90% of streaming agent UX
- Tool results render in real-time as the agent executes

**Building a stateful multi-step agent pipeline (research, code review, multi-hop Q&A):**
- Use `@langchain/langgraph` with typed state schema
- Define nodes as tool-calling steps, edges as conditional transitions
- Use LangGraph's checkpointer with PostgreSQL for durable state across requests

**Building autonomous coding/file-system agents (viflo GSD workflow tooling):**
- Use `@anthropic-ai/claude-agent-sdk` (the same SDK that powers Claude Code)
- `query()` function returns an async iterator — consume the stream to react to tool calls as Claude works

**Anthropic multi-agent recommended pattern (2026):**
- Orchestrator: Claude Opus 4 (`claude-opus-4-5` or latest) — plans and delegates
- Subagents: Claude Sonnet 4 (`claude-sonnet-4-5` or latest) — execute tasks
- ~15x token cost vs single-agent; only viable when task complexity justifies the cost
- Keep subagent context windows small — each subagent should receive only the context it needs

**Simple RAG + agent hybrid (most common viflo use case):**
- Vercel AI SDK `streamText` with a `retrieve` tool definition
- Tool calls pgvector endpoint, injects chunks into assistant context, streams final answer
- No LangGraph needed — tool-calling handles the retrieve step inline

### Version Compatibility

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| `@anthropic-ai/sdk` | ^0.78.0 | Node.js 18+, TypeScript 5+ | Use `AsyncAnthropic` / `client.messages.stream()` for streaming |
| `anthropic` (Python) | ^0.83.0 | Python 3.9+ | viflo uses Python 3.11+ — fully compatible |
| `ai` (Vercel AI SDK) | ^6.x | Next.js 14+, React 18+ | AI SDK 6 stable; includes MCP support and Agent abstraction |
| `@ai-sdk/anthropic` | ^1.x | Same as `ai` | Provider adapter — must match major version of `ai` |
| `@langchain/langgraph` | ^1.1.5 | Node.js 18+, TypeScript 5+ | Use alongside Vercel AI SDK for stateful agents |
| `langchain` (Python) | ^0.5.x | Python >=3.10 | viflo uses Python 3.11+ — compatible; use LCEL interface |

---

## Full Installation Reference

```bash
# ── STRIPE SKILL ────────────────────────────────────────────────
# Node.js / Next.js
npm install stripe @stripe/stripe-js @stripe/react-stripe-js

# Python / FastAPI
pip install stripe
pip install "stripe[async]"  # if using async handlers

# ── RAG / VECTOR SEARCH SKILL ──────────────────────────────────
# Node.js (retrieval helpers)
npm install pgvector

# Pinecone (optional — only when pgvector scale is insufficient)
npm install @pinecone-database/pinecone

# Python / FastAPI
pip install pgvector openai anthropic langchain-community langchain-openai

# ── AGENT ARCHITECTURE SKILL ───────────────────────────────────
# TypeScript / Next.js — Claude agents + streaming UI
npm install @anthropic-ai/sdk ai @ai-sdk/anthropic

# TypeScript / Next.js — stateful multi-agent graphs
npm install @langchain/langgraph @langchain/langgraph-sdk

# TypeScript — autonomous code/file-system agents (GSD tooling)
npm install @anthropic-ai/claude-agent-sdk

# Python / FastAPI — Claude agents
pip install anthropic

# Python / FastAPI — LangChain agent pipelines
pip install langchain langchain-core
```

---

## Sources

- [npmjs.com — stripe](https://www.npmjs.com/package/stripe) — v20.3.1 confirmed current (published ~18 days before 2026-02-24); MEDIUM confidence (search result claim)
- [npmjs.com — @stripe/stripe-js releases](https://github.com/stripe/stripe-js/releases) — v8.8.0 confirmed current (published 3 days before 2026-02-24); MEDIUM confidence
- [npmjs.com — @stripe/react-stripe-js](https://www.npmjs.com/package/@stripe/react-stripe-js) — v5.6.0 confirmed; MEDIUM confidence
- [PyPI — stripe](https://pypi.org/project/stripe/) — v14.3.0 confirmed (released 2026-01-28); HIGH confidence (fetched directly from PyPI)
- [Stripe Webhook Docs](https://docs.stripe.com/webhooks) — raw body requirement and `constructEvent()` verified; HIGH confidence
- [Stripe Idempotency Docs](https://docs.stripe.com/api/idempotent_requests) — auto-retry with idempotency keys in Node SDK v17+ verified; HIGH confidence
- [npmjs.com — pgvector](https://www.npmjs.com/package/pgvector) — v0.2.1 confirmed (Node.js); MEDIUM confidence
- [PyPI — pgvector](https://pypi.org/project/pgvector/) — v0.4.2 confirmed (Python); MEDIUM confidence
- [npmjs.com — @pinecone-database/pinecone](https://www.npmjs.com/package/@pinecone-database/pinecone) — v7.1.0 confirmed, Node >=20 requirement verified; MEDIUM confidence
- [OpenAI text-embedding-3 docs](https://platform.openai.com/docs/models/text-embedding-3-small) — 1536 dims, $0.02/1M tokens verified; HIGH confidence
- [pgvector/pgvector GitHub](https://github.com/pgvector/pgvector) — HNSW index recommendation, scale guidance verified; HIGH confidence
- [instaclustr.com — pgvector 2026 guide](https://www.instaclustr.com/education/vector-database/pgvector-key-features-tutorial-and-pros-and-cons-2026-guide/) — scale thresholds and best practices; MEDIUM confidence
- [npmjs.com — @anthropic-ai/sdk](https://www.npmjs.com/package/@anthropic-ai/sdk) — v0.78.0 confirmed (published 4 days before 2026-02-24); MEDIUM confidence
- [npmjs.com — @anthropic-ai/claude-agent-sdk](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk) — v0.2.49 confirmed; MEDIUM confidence
- [Vercel — AI SDK 6 announcement](https://vercel.com/blog/ai-sdk-6) — v6 stable, MCP support, Agent abstraction, tool execution verified; HIGH confidence
- [npmjs.com — ai](https://www.npmjs.com/package/ai) — v6.0.x confirmed current (published 2 hours before 2026-02-24 search); MEDIUM confidence
- [npmjs.com — @langchain/langgraph](https://www.npmjs.com/package/@langchain/langgraph) — v1.1.5 confirmed (published 6 days before 2026-02-24); MEDIUM confidence
- [PyPI — langchain](https://pypi.org/project/langchain/) — v0.5.1 (Feb 10, 2026) confirmed as latest; MEDIUM confidence
- [LangGraph JS docs](https://docs.langchain.com/oss/javascript/langgraph/overview) — TypeScript support, StateGraph pattern verified; HIGH confidence
- [datacamp.com — CrewAI vs LangGraph 2026](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen) — production comparison, LangGraph recommended for stateful/conditional workflows; MEDIUM confidence
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — orchestrator/subagent model, context scoping; HIGH confidence
- [mastra.ai](https://mastra.ai/docs) — @mastra/core v1.6.0 (Feb 2026), TypeScript-first agent framework; MEDIUM confidence

---

*Stack research for: viflo v1.3 Expert Skills (Stripe, RAG, Agent Architecture)*
*Researched: 2026-02-24*
