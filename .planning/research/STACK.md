# Stack Research

**Domain:** v1.2 Skills Expansion — Auth, Stripe, RAG/Vector Search, Agent Architecture, Prompt Engineering
**Researched:** 2026-02-24
**Confidence:** HIGH (all versions verified against npm/PyPI/official sources)

---

## Skill 1: Auth Systems

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `@clerk/nextjs` | ^6.38.0 | Managed auth with prebuilt UI components | Fastest to production for SaaS — ships `<SignIn>`, `<UserButton>`, MFA, org management, RBAC out of the box. No database adapter required. Best choice when dev velocity > data ownership. |
| `next-auth` | 5.x (beta — `@beta` tag) | Self-hosted auth for Next.js App Router | Only mature self-hosted option for App Router. Single `auth()` function works in Server Components, Route Handlers, and `proxy.ts` middleware. Use when vendor lock-in is unacceptable. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `@auth/prisma-adapter` | ^2.x | Connects Auth.js to Prisma/PostgreSQL | Required for Auth.js persistent sessions — install when using next-auth self-hosted |
| `@auth/drizzle-adapter` | ^1.x | Connects Auth.js to Drizzle ORM | Alternative to Prisma adapter — lighter, better TypeScript inference |
| `jose` | ^5.x | JWT encode/decode (Auth.js peer dep) | Transitive — include in skill as context for custom token strategies |

### Installation

```bash
# Option A: Clerk (managed)
npm install @clerk/nextjs

# Option B: Auth.js (self-hosted)
npm install next-auth@beta @auth/prisma-adapter
# or
npm install next-auth@beta @auth/drizzle-adapter
```

### Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `@clerk/nextjs` v6 | Auth0 / `@auth0/nextjs-auth0` | Auth0 is better for enterprise B2B with complex SSO/SAML requirements — Clerk is simpler DX for B2C SaaS |
| `next-auth@beta` | Supabase Auth | Supabase Auth makes sense when already using Supabase as the database — avoids split infrastructure |

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `next-auth@4.x` (stable) | Lacks App Router support; uses Pages Router patterns that conflict with Next.js 16 | `next-auth@beta` (v5) |
| `@clerk/nextjs` < v6 / Core 2 | Core 1 is deprecated, lacks App Router middleware support, breaking changes in v6 upgrade | `@clerk/nextjs@^6` |
| Rolling custom JWT auth from scratch | Session management, CSRF, rotation, and token invalidation are subtle and easy to get wrong | Either Clerk or Auth.js |

### Stack Patterns by Variant

**If building a SaaS product that needs fast launch:**
- Use Clerk (`@clerk/nextjs` v6)
- Because it ships MFA, org management, and styled UI components with zero configuration

**If the project requires full data ownership (GDPR, healthcare, fintech):**
- Use Auth.js (`next-auth@beta`) with PostgreSQL adapter
- Because all user data stays in your own database

**If using Next.js 16 App Router (current viflo stack):**
- Both are compatible — Clerk via `clerkMiddleware()` in `proxy.ts`; Auth.js via `auth()` helper
- `proxy.ts` replaces `middleware.ts` in Next.js 16

---

## Skill 2: Stripe Payments

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `stripe` (Node.js) | ^20.3.1 | Server-side Stripe API client | Official SDK; handles checkout sessions, subscriptions, invoices, webhook signature verification. Supports TypeScript natively. |
| `@stripe/stripe-js` | ^5.x | Client-side Stripe.js loader | Lazy-loads Stripe.js from Stripe's CDN; required for PCI-compliant card Element embedding |
| `@stripe/react-stripe-js` | ^5.6.0 | React wrapper for Stripe Elements | Provides `<Elements>`, `<CardElement>`, `<PaymentElement>` components for React 19 / Next.js |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `stripe` webhook raw body | n/a (config) | Signature verification requires raw Buffer, not parsed JSON | ALWAYS — misconfiguration of body-parser breaks webhook verification |

### Installation

```bash
# Server-side (Next.js API routes / Route Handlers)
npm install stripe

# Client-side (React checkout UI)
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `stripe@<16` | Stripe API versioning — older major versions lock you to outdated API surfaces | `stripe@^20` |
| Parsing webhook body with `express.json()` before verification | Destroys the raw body needed for `stripe.webhooks.constructEvent()` | Use raw body middleware, or in Next.js App Router: `await request.text()` before parsing |
| Storing card data directly | PCI DSS violation — Stripe Elements offloads card data to Stripe servers | Always use Stripe Elements / Payment Element |

### Stack Patterns by Variant

**For one-time payments (e-commerce checkout):**
- Use Stripe Checkout (hosted page) or Payment Element with `payment_intent`
- Simplest integration, Stripe handles 3DS and payment method display

**For recurring subscriptions (SaaS billing):**
- Use `subscription` objects with `price` IDs
- Combine with Customer Portal (`stripe.billingPortal.sessions.create()`) for self-serve plan management

**For webhooks in Next.js App Router:**
```typescript
// app/api/webhooks/stripe/route.ts
export async function POST(request: Request) {
  const body = await request.text(); // raw body — critical for signature verification
  const sig = request.headers.get('stripe-signature')!;
  const event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  // handle event.type
}
```

---

## Skill 3: RAG / Vector Search

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `pgvector` (Python) | ^0.4.2 | pgvector driver for Python (SQLAlchemy, asyncpg, psycopg3) | Keeps vector search inside existing PostgreSQL — no extra managed service for MVPs and projects under 50M vectors. Integrates with FastAPI/SQLAlchemy 2.0 already in the viflo stack. |
| `pgvector` (Node.js) | ^0.2.1 | pgvector driver for Node.js/TypeScript | For Next.js Route Handler retrieval pipelines without a Python service |
| `@pinecone-database/pinecone` | ^7.1.0 | Managed Pinecone vector DB client | Use when scale exceeds pgvector's sweet spot (>50M vectors) or when fully managed, predictable latency is required for production RAG |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `openai` (Python) | ^1.x | OpenAI embeddings API (`text-embedding-3-small`) | Most cost-effective embedding model for production RAG at scale |
| `anthropic` (Python) | ^0.83.0 | Claude API for generation step in RAG | When using Claude as the generator in retrieve-then-generate |
| `langchain-community` (Python) | ^0.3.x | PGVector vectorstore integration | Wraps pgvector in LangChain's `VectorStore` interface for RAG chains |
| `langchain-openai` (Python) | ^1.1.10 | LangChain's OpenAI embedding wrapper | Needed if using LangChain for the full RAG pipeline |

### Embedding Model Recommendation

| Model | Dimensions | Cost | When to Use |
|-------|------------|------|-------------|
| `text-embedding-3-small` | 1536 | ~$0.02/1M tokens | Default — strong performance, low cost, fits pgvector well |
| `text-embedding-3-large` | 3072 | ~$0.13/1M tokens | High-precision retrieval where recall is critical; higher storage cost |

### Installation

```bash
# Python (FastAPI RAG backend)
pip install pgvector anthropic openai langchain-community langchain-openai

# Node.js (Next.js retrieval helpers)
npm install pgvector

# Pinecone (optional — use when pgvector insufficient)
npm install @pinecone-database/pinecone
# or
pip install pinecone
```

### Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| pgvector (primary) | Pinecone | >50M vectors, need managed SLA, no Postgres ops available |
| pgvector (primary) | Weaviate | Need hybrid search (dense + keyword BM25) with richer schema — not worth the ops burden at small scale |
| pgvector (primary) | Qdrant | Complex metadata filtering requirements at scale — Qdrant's payload filtering is best-in-class |
| `text-embedding-3-small` | `text-embedding-3-large` | High-recall use cases (legal, medical) where cost is secondary |

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `pgvector` extension > 50M vectors without pgvectorscale | ivfflat index degrades at scale; exact KNN is slow | Add `pgvectorscale` or migrate to Pinecone/Qdrant |
| Storing raw LLM output in vectors | Embeddings should represent source content, not generated text | Embed original documents/chunks |
| Chunking whole documents as single vectors | Long chunks degrade retrieval precision | Chunk to 512-1024 tokens with overlap |

### Stack Patterns by Variant

**If building on existing viflo PostgreSQL stack (recommended for MVP):**
- Use pgvector Python client + SQLAlchemy 2.0
- Add `CREATE EXTENSION IF NOT EXISTS vector;` to migration
- Store embeddings in a `VECTOR(1536)` column alongside existing data

**If scale or managed infra required:**
- Replace pgvector with `@pinecone-database/pinecone` v7
- Keep the same retrieval interface — the pattern is the same, only the client changes

---

## Skill 4: Agent Architecture

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `@anthropic-ai/sdk` (TypeScript) | ^0.78.0 | Anthropic Claude API — tools, streaming, multi-turn | Official SDK; supports tool use, extended thinking, streaming, vision. Use for direct Claude-based agent construction without framework overhead. |
| `anthropic` (Python) | ^0.83.0 | Same as above for FastAPI agent backends | Async client (`AsyncAnthropic`) works natively with FastAPI's async handlers |
| `@anthropic-ai/claude-agent-sdk` | ^0.2.49 | Programmatic Claude Code agents | Specialized SDK for building autonomous agents that control file systems and run commands — relevant for viflo's own agentic tooling use case |
| `ai` (Vercel AI SDK) | ^6.0.97 | Unified LLM SDK for Next.js streaming + agents | Best DX for streaming agent UI in Next.js — `useChat`, `useCompletion`, `streamText`, tool execution, MCP support. Sits on top of Anthropic/OpenAI SDKs. |
| `@langchain/langgraph` | ^1.1.5 | Stateful multi-agent graph orchestration | Use for complex multi-step agent workflows with explicit state transitions, checkpointing, and human-in-the-loop patterns |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `@ai-sdk/anthropic` | ^1.x | Vercel AI SDK Anthropic provider | Required when using Vercel AI SDK with Claude models |
| `@langchain/langgraph-sdk` | ^1.6.2 | LangGraph client SDK (connect to hosted graph server) | When running LangGraph server separately from Next.js |
| `langchain` (Python) | ^1.2.10 | Python orchestration for agent chains | FastAPI agent backends requiring complex chain composition |

### Installation

```bash
# TypeScript / Next.js agents
npm install @anthropic-ai/sdk ai @ai-sdk/anthropic

# LangGraph (complex stateful agents)
npm install @langchain/langgraph @langchain/langgraph-sdk

# Python / FastAPI agents
pip install anthropic langchain langchain-core
```

### Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Vercel AI SDK (`ai`) for Next.js | Direct `@anthropic-ai/sdk` | Direct SDK when you don't need streaming UI components or multi-provider switching |
| `@langchain/langgraph` for multi-agent | Custom orchestrator | LangGraph for well-defined state machines; custom if LangGraph's graph model doesn't map to your workflow |
| `@anthropic-ai/sdk` direct | OpenAI Agents SDK | OpenAI SDK if your agents are OpenAI-only — Anthropic SDK for Claude-first |

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `langchain` for simple single-turn completions | Massive abstraction overhead for what is a 5-line API call | Direct `@anthropic-ai/sdk` or Vercel AI SDK |
| Synchronous Anthropic Python client in FastAPI | Blocks async event loop — kills concurrency | `AsyncAnthropic` client |
| Storing full conversation history in memory (no persistence) | Agent state lost on restart; multi-user apps corrupt each other's context | PostgreSQL-backed session store or LangGraph checkpointer |

### Stack Patterns by Variant

**If building agent UI in Next.js (streaming chat, tool calls displayed live):**
- Use Vercel AI SDK v6 (`ai` + `@ai-sdk/anthropic`)
- `useChat` hook + `streamText` with tool definitions handles 90% of streaming agent UX

**If building a stateful multi-step agent pipeline (research, code review, etc.):**
- Use `@langchain/langgraph` with state schema
- Define nodes as tool-calling steps, edges as conditional transitions

**If building autonomous coding/file-system agents (viflo's own tooling):**
- Use `@anthropic-ai/claude-agent-sdk`
- This is what powers Claude Code itself — appropriate for viflo's GSD workflow agents

**Anthropic multi-agent recommended pattern (2026):**
- Orchestrator: Claude Opus 4 (`claude-opus-4-5` or latest)
- Subagents: Claude Sonnet 4 (`claude-sonnet-4-5` or latest)
- ~15x token usage vs single-agent; only viable when task value justifies cost

---

## Skill 5: Prompt Engineering

### Core Technologies

No library installs required for the prompt engineering skill itself — it is documentation-only content. However, these tools support evaluation workflows:

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `anthropic` (Python) | ^0.83.0 | Run evaluation scripts against Claude | Direct SDK for prompt iteration and automated eval scripts |
| `braintrust` | ^0.0.x | LLM evaluation platform | Industry-standard eval tooling; integrates with Anthropic, OpenAI; supports scoring functions and datasets |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `anthropic` Python `batch` API | (part of SDK) | Batch prompt evaluation over datasets | When running systematic prompt A/B tests across 100s of examples |
| `pytest` | ^8.x | Python test runner for eval scripts | Automate prompt regression tests in CI — flag prompt degradation |

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Hardcoding prompts in application code | Can't version, test, or iterate | Externalize to `.prompt` files or a prompt registry |
| Evaluating prompt quality manually at scale | Subjective and doesn't scale | LLM-as-judge with `braintrust` or Anthropic batch API |

---

## Version Compatibility Matrix

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| `@clerk/nextjs` ^6 | Next.js 16, React 19 | Requires `proxy.ts` (not `middleware.ts`) in Next.js 16 |
| `next-auth@beta` (v5) | Next.js 14+, React 18+ | Still beta as of 2026-02-24; widely used in production; install with `@beta` tag |
| `stripe` ^20 | Node.js 16+ | Node 16 deprecated — use Node 20+ per viflo stack |
| `@stripe/react-stripe-js` ^5.6 | React 16.8+, React 19 ✓ | Compatible with viflo's React 19 |
| `@pinecone-database/pinecone` ^7.1 | TypeScript >=5.2, Node.js >=20 | Fits viflo's TS 5.7+ and Node 20+ |
| `ai` (Vercel) ^6 | Next.js 14+, React 18+ | AI SDK 6 is backwards-compatible from v5 |
| `@anthropic-ai/sdk` ^0.78 | Node.js 18+ | Use `AsyncAnthropic` for async contexts |
| `anthropic` Python ^0.83 | Python 3.9+ | viflo uses Python 3.11+ — fully compatible |
| `pgvector` Python ^0.4.2 | SQLAlchemy 2.0, psycopg3, asyncpg | Matches viflo's SQLAlchemy 2.0 stack |
| `langchain` Python ^1.2.10 | Python >=3.10 | viflo uses Python 3.11+ — compatible |
| `@langchain/langgraph` ^1.1.5 | Node.js 18+ | Use alongside Vercel AI SDK for stateful agents |

---

## Full Installation Reference

```bash
# ── AUTH SKILL ────────────────────────────────────────────────
# Option A: Clerk
npm install @clerk/nextjs

# Option B: Auth.js
npm install next-auth@beta @auth/prisma-adapter

# ── STRIPE SKILL ──────────────────────────────────────────────
npm install stripe @stripe/stripe-js @stripe/react-stripe-js

# ── RAG SKILL (Node.js) ───────────────────────────────────────
npm install pgvector
npm install @pinecone-database/pinecone   # only if using Pinecone

# RAG SKILL (Python / FastAPI)
pip install pgvector anthropic openai langchain-community langchain-openai

# ── AGENT SKILL (TypeScript / Next.js) ───────────────────────
npm install @anthropic-ai/sdk ai @ai-sdk/anthropic
npm install @langchain/langgraph @langchain/langgraph-sdk  # stateful agents only

# Agent Skill (Python / FastAPI)
pip install anthropic langchain langchain-core

# ── PROMPT ENGINEERING SKILL ──────────────────────────────────
pip install anthropic pytest   # for eval scripts
```

---

## Sources

- [npmjs.com — @clerk/nextjs](https://www.npmjs.com/package/@clerk/nextjs) — v6.38.0 confirmed current (published 2 days ago at research date)
- [Clerk Docs — Next.js v6 Upgrade Guide](https://clerk.com/docs/guides/development/upgrading/upgrade-guides/nextjs-v6) — v6 breaking changes verified
- [Auth.js Installation Docs](https://authjs.dev/getting-started/installation?framework=Next.js) — `next-auth@beta` confirmed still beta, `auth()` API verified
- [npmjs.com — next-auth](https://www.npmjs.com/package/next-auth?activeTab=versions) — v5 latest beta version confirmed
- [npmjs.com — stripe](https://www.npmjs.com/package/stripe) — v20.3.1 confirmed current
- [npmjs.com — @stripe/react-stripe-js releases](https://github.com/stripe/react-stripe-js/releases) — v5.6.0 confirmed (Jan 28)
- [Stripe Webhook Docs](https://docs.stripe.com/webhooks) — raw body requirement and `constructEvent()` verified
- [npmjs.com — @pinecone-database/pinecone](https://www.npmjs.com/package/@pinecone-database/pinecone) — v7.1.0 confirmed, Node >=20 requirement verified
- [PyPI — pgvector](https://pypi.org/project/pgvector/) — v0.4.2 confirmed latest
- [GitHub — pgvector-node](https://github.com/pgvector/pgvector-node) — v0.2.1 confirmed
- [PyPI — anthropic](https://pypi.org/project/anthropic/) — v0.83.0 confirmed (Feb 19, 2026)
- [npmjs.com — @anthropic-ai/sdk](https://www.npmjs.com/package/@anthropic-ai/sdk) — v0.78.0 confirmed
- [npmjs.com — @anthropic-ai/claude-agent-sdk](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk) — v0.2.49 confirmed
- [Vercel AI SDK 6 announcement](https://vercel.com/blog/ai-sdk-6) — v6 stable, MCP support, agent tooling verified
- [npmjs.com — ai](https://www.npmjs.com/package/ai) — v6.0.97 confirmed (published 2 days ago at research date)
- [npmjs.com — @langchain/langgraph](https://www.npmjs.com/package/@langchain/langgraph) — v1.1.5 confirmed
- [PyPI — langchain](https://pypi.org/project/langchain/) — v1.2.10 confirmed (Feb 10, 2026)
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — multi-agent patterns, orchestrator/subagent model verified
- [pgvector vector DB comparison 2026](https://www.firecrawl.dev/blog/best-vector-databases) — pgvector vs Pinecone positioning verified

---

*Stack research for: viflo v1.2 Skills Expansion*
*Researched: 2026-02-24*
