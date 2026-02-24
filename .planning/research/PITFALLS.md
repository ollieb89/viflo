# Pitfalls Research

**Domain:** Skill documentation — Stripe Payments, RAG/Vector Search, Agent Architecture (v1.3 Expert Skills)
**Researched:** 2026-02-24
**Confidence:** HIGH for Stripe integration pitfalls (multiple official + community sources); MEDIUM for RAG (rapidly evolving field); MEDIUM for Agent architecture (patterns stabilising but still emergent)

---

## Critical Pitfalls

### Pitfall 1: Stripe Webhook Body Parsing — Silent Signature Failure in Next.js App Router

**What goes wrong:**
`stripe.webhooks.constructEvent()` requires the **raw, unparsed request body** as a string or Buffer. In Next.js App Router, route handlers receive a `Request` object (Web API). If you call `await req.json()` — which feels natural — the body is parsed into a JavaScript object and the raw bytes are lost. Stripe's signature verification then throws `No signatures found matching the expected signature for payload`. The error message is cryptic enough that developers spend hours debugging before finding the root cause.

**Why it happens:**
Pages Router required `export const config = { api: { bodyParser: false } }` to disable automatic parsing. That config option is silently ignored in App Router — but unlike Pages Router, App Router does NOT auto-parse by default, so no `config` export is needed. The mistake is when developers call `req.json()` themselves, which parses the body and makes the raw bytes irrecoverable from the same request stream.

In addition, there is a known Next.js issue (#54090) where `export const config` for bodyParser configuration is unsupported in App Router. Developers copying Pages Router code paste this config into an App Router file, where it does nothing, and assume body parsing is disabled.

**How to avoid:**
Use `await req.text()` — not `await req.json()` — to get the raw body in App Router webhook handlers. Then pass that string directly to `stripe.webhooks.constructEvent(body, sig, secret)`. No `export const config` needed. Full correct pattern:

```typescript
// app/api/webhooks/stripe/route.ts
import Stripe from 'stripe';
import { NextRequest, NextResponse } from 'next/server';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: NextRequest) {
  const body = await req.text();                        // raw string, not parsed
  const sig = req.headers.get('stripe-signature')!;

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch (err) {
    return NextResponse.json({ error: 'Webhook signature verification failed' }, { status: 400 });
  }
  // ... handle event
  return NextResponse.json({ received: true });
}
```

**Warning signs:**
- Skill or example uses `await req.json()` in a Stripe webhook route handler.
- Skill includes `export const config = { api: { bodyParser: false } }` in an App Router file.
- Skill tutorial says "disable body parser" without explaining the App Router difference.

**Phase to address:**
Stripe skill authoring — the raw body pattern must be in the first code example in the webhook section, not a footnote.

---

### Pitfall 2: Stripe Webhook Idempotency — Race Conditions and Duplicate Fulfillment

**What goes wrong:**
Stripe retries webhook delivery for up to 3 days on non-2xx responses or timeouts. If a handler processes synchronously and is slow (e.g., sends email, provisions cloud resources), Stripe retries while the first invocation is mid-flight. Both invocations complete, resulting in duplicate order fulfillment, double subscription activations, or multiple emails.

The naive fix — an in-memory `Set` of processed event IDs — fails immediately under concurrent invocations (serverless functions have no shared memory between instances). A database check-then-process is also insufficient: "findOne → process → mark done" is not atomic and produces the exact race condition it's meant to prevent.

**Why it happens:**
Tutorial-level Stripe integrations show inline processing. The queue-first pattern is rarely taught. The race condition is invisible in development (single instance, low latency) and only manifests in production under load or during Stripe's retry window.

**How to avoid:**
1. Verify signature immediately and return 200.
2. Store the raw event in a `stripe_events` table with `stripe_event_id` as a UNIQUE constraint.
3. Return 200 to Stripe whether insert succeeded or failed (duplicate = already processing).
4. Process asynchronously from the queue via a background worker.

```typescript
// Atomic idempotency: upsert with conflict ignore
await db.execute(
  `INSERT INTO stripe_events (stripe_event_id, event_type, payload, received_at)
   VALUES ($1, $2, $3, NOW())
   ON CONFLICT (stripe_event_id) DO NOTHING`,
  [event.id, event.type, JSON.stringify(event)]
);
// Then enqueue worker; worker checks status before processing
```

**Warning signs:**
- Skill example processes webhook inline before returning 200.
- No `stripe_events` table or `stripe_event_id` deduplication in database schema.
- Skill does not mention Stripe's at-least-once delivery guarantee.
- Skill uses `Set` or in-memory cache for deduplication.

**Phase to address:**
Stripe skill authoring — idempotency pattern in the main SKILL.md body; schema in `references/`.

---

### Pitfall 3: Stripe Webhook Event Ordering — State Machine Assumptions

**What goes wrong:**
Stripe explicitly does not guarantee delivery order. Under network conditions, `customer.subscription.updated` can arrive before `customer.subscription.created`. If the application's database logic assumes sequential state transitions (e.g., `PENDING → ACTIVE → CANCELLED`), an out-of-order update is dropped silently or throws a foreign key violation.

Additionally, the 5-minute signature verification window (`stripe.webhooks.constructEvent` throws for timestamps > 300 seconds old) means you cannot persist raw webhook payloads and re-verify them later. The verify-then-enqueue pattern is required, not verify-on-dequeue.

**Why it happens:**
Developers model subscriptions as a state machine and assume Stripe mirrors that model with ordered delivery. The Stripe docs warn about this but it is easy to miss.

**How to avoid:**
- Never assume an event arrives after its prerequisites. On receiving `customer.subscription.updated` when no subscription exists locally, query Stripe's API to fetch and upsert the subscription.
- Store the raw event payload in a queue; process events by fetching current state from Stripe API rather than building derived state from event chains.
- Implement a reconciliation cron job (`/api/cron/stripe-reconcile`) that compares local subscription state against Stripe API for all active customers every 24 hours. This also catches the 3-day retry expiry case.
- Verify signature before enqueuing; process from the queue asynchronously.

**Warning signs:**
- Webhook handler has conditional branches like `if (localSub.status === 'active' && event.type === 'customer.subscription.deleted')` that assume prior state.
- No reconciliation job documented.
- No `customer.subscription.updated` + `customer.subscription.deleted` + `invoice.payment_failed` handlers documented (only `checkout.session.completed`).

**Phase to address:**
Stripe skill authoring — subscription lifecycle section must document all critical events and the event-ordering caveat.

---

### Pitfall 4: Stripe Test Keys in Production Environments

**What goes wrong:**
Test keys (`sk_test_*`) silently accept all requests but never move real money. If test keys reach a production environment — via a misconfigured CI secret, a committed `.env.local`, or a copy-paste error during deployment — the app appears to work (checkout completes, webhooks fire) but no revenue is collected.

Live keys (`sk_live_*`) are revealed only once in the Stripe dashboard. If lost, a new key must be generated, requiring rotation across all environments.

**Why it happens:**
Local development uses test keys. If the key name in `.env` is the same (`STRIPE_SECRET_KEY`) in both local and production files, a copy-paste between environments brings the wrong value. Stripe has no runtime warning for test keys being used in a live context — the API simply works.

**How to avoid:**
- Validate the key prefix at startup: `if (process.env.NODE_ENV === 'production' && process.env.STRIPE_SECRET_KEY!.startsWith('sk_test_')) throw new Error('Test Stripe key in production')`.
- Use separate env var names in CI: `STRIPE_SECRET_KEY_TEST` and `STRIPE_SECRET_KEY_LIVE`; deployment scripts explicitly select based on environment.
- Never commit `.env.local` (already in viflo's gitleaks/detect-secrets pre-commit setup).
- Validate the `livemode` boolean on incoming webhook events before processing.

**Warning signs:**
- Skill uses `STRIPE_SECRET_KEY` for both test and live without distinguishing them.
- No startup validation of key prefix.
- Skill's deployment checklist does not include "verify live Stripe key".

**Phase to address:**
Stripe skill authoring — deployment checklist section; mention in security section.

---

### Pitfall 5: RAG Chunking — Fixed-Size Splitting Destroys Semantic Units

**What goes wrong:**
Fixed-size chunking (e.g., split every 512 tokens with 50 token overlap) cuts through sentences, paragraphs, and logical sections arbitrarily. The resulting chunks have "averaged" embeddings that represent no single coherent idea. Retrieval returns semantically blurry results; the LLM receives incomplete context and either gives a vague answer or fills the gap by hallucinating.

Research consistently shows chunking quality as the primary driver of RAG failures — above model selection, embedding choice, or retrieval strategy. The wrong chunking strategy can create up to a 9% gap in recall performance.

**Why it happens:**
Fixed-size chunking is the simplest implementation, appears in all introductory tutorials, and works adequately on toy datasets with short, uniform documents. The failure mode only emerges at scale with real-world documents that have mixed structure (prose + tables + code + headers).

**How to avoid:**
For most production text corpora: use recursive character splitting that respects document structure (paragraphs, then sentences, then words). For domain-specific technical content (API docs, spec sheets): use semantic or proposition-based chunking.

Recommended parameters as a starting baseline:
- Chunk size: 800–1200 characters
- Overlap: 15–20% of chunk size (to preserve cross-chunk context)
- Separators: `["\n\n", "\n", ". ", " "]` in priority order

For structured documents (markdown, HTML): parse structure first, chunk within sections, not across them.

**Warning signs:**
- Skill shows `text_splitter = CharacterTextSplitter(chunk_size=512)` as the default.
- No mention of document structure preservation in chunking.
- No guidance on testing chunk quality (inspect retrieved chunks manually before going to production).
- Skill recommends a single chunk size without discussing the content-type dependency.

**Phase to address:**
RAG skill authoring — chunking section must present multiple strategies with selection criteria, not a single default.

---

### Pitfall 6: RAG Embedding Model Drift — Silent Retrieval Degradation

**What goes wrong:**
When an embedding model is upgraded (e.g., `text-embedding-ada-002` → `text-embedding-3-small`, or a local model is retrained), the new model's vector space is not compatible with vectors produced by the old model. The dot products and cosine similarities between old-indexed and newly-embedded query vectors become meaningless. Retrieval silently degrades — top-k results look plausible but are semantically wrong. This is invisible without retrieval evaluation metrics.

**Why it happens:**
Teams treat embeddings as immutable database records and embedding models as interchangeable. There is no build-time or runtime check that the model used to embed a document matches the model used to embed a query.

**How to avoid:**
- Store `embedding_model_version` as a column alongside every vector in the database.
- At query time, assert that the query's embedding model matches the indexed model.
- On model upgrade: re-embed all documents before switching query-side model. Use blue/green index strategy (keep old index live; build new index incrementally; switch atomically).
- Pin the model version in configuration: `EMBEDDING_MODEL=text-embedding-3-small` — never auto-upgrade.
- Monitor cosine similarity distribution over time. A shift in the p50 similarity of top-k results signals drift.

**Warning signs:**
- No `embedding_model_version` column in the vector table schema.
- Skill's embedding code doesn't pin a model version.
- No section on what to do when the embedding model changes.
- Skill has no retrieval evaluation section.

**Phase to address:**
RAG skill authoring — data model section must include `embedding_model_version`; deployment section must cover model pinning.

---

### Pitfall 7: RAG — No Retrieval Quality Evaluation Layer

**What goes wrong:**
A RAG pipeline that assembles chunks and passes them to an LLM looks complete. Without a retrieval quality layer, the following failure modes are invisible in production:

1. **Retrieval overload**: too many chunks (high k) introduce noise, degrading generation quality even when relevant chunks are present.
2. **Retrieval miss**: no highly-relevant chunk exists; the LLM hallucinates a plausible answer rather than saying "I don't know".
3. **Context position bias**: LLMs favour information at the start and end of the context window; relevant chunks injected in the middle are ignored.
4. **Citation hallucination**: the LLM cites documents that don't actually support its claims.

These all manifest as plausible-but-wrong LLM outputs that pass eyeball review.

**Why it happens:**
RAG tutorials demonstrate the happy path where retrieval succeeds. The skill that only teaches pipeline assembly leaves developers with no tools to diagnose the unhappy path.

**How to avoid:**
- Implement a retrieval score threshold: if top-k results have cosine similarity below a configurable threshold (e.g., < 0.75 for `text-embedding-3-small`), return a "no relevant context found" response rather than passing low-quality chunks to the LLM.
- Separate retrieval evaluation from generation evaluation. Measure hit rate, precision@k, and MRR on a golden retrieval test set before shipping.
- Use a small `k` (3–5) as the default. Only increase after demonstrating recall is insufficient.
- Document re-ranking as an intermediate step for high-stakes queries: retrieve k=20, re-rank with a cross-encoder, pass top-3 to the LLM.

**Warning signs:**
- No retrieval score threshold in the pipeline.
- No golden test set for retrieval quality.
- Skill recommends a fixed k without discussing the noise/recall tradeoff.
- No mention of the "no relevant context" case.

**Phase to address:**
RAG skill authoring — evaluation must be a first-class section in the main SKILL.md, not in `references/`.

---

### Pitfall 8: pgvector — Missing HNSW Index Causes Sequential Scans

**What goes wrong:**
pgvector without an HNSW or IVFFlat index performs a full sequential scan on the `vector` column for every similarity query. At 10,000+ rows, queries that take <50ms with an HNSW index take 30–70 seconds without one. The query planner may also silently prefer a sequential scan over the HNSW index when combined with additional `WHERE` clause filters, dropping query time back to sequential scan performance even with the index present.

**Why it happens:**
pgvector tutorials show `CREATE TABLE ... (embedding vector(1536))` and example queries but often omit the `CREATE INDEX` step. The index omission is invisible until scale. Additionally, pgvector's HNSW index does not play well with `ORDER BY ... LIMIT` combined with non-vector `WHERE` filters — the query planner sometimes ignores the vector index and performs a full scan.

**How to avoid:**
```sql
-- Always create after loading initial data (faster than building incrementally)
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- For filtered queries, add composite index or use partial index
-- Set ef_search at query time for recall/speed tradeoff:
SET hnsw.ef_search = 100;
```

For production filtering (e.g., `WHERE user_id = $1 ORDER BY embedding <=> $2 LIMIT 5`): benchmark with and without HNSW, as the planner may choose a sequential scan. Consider `hnsw.iterative_scan = relaxed_order` if the planner ignores the index.

Note: HNSW inserts are ~5x slower than without an index. Build the index after bulk load, not during it.

**Warning signs:**
- Skill schema has no `CREATE INDEX ... USING hnsw` statement.
- No mention of query planner behavior with combined vector + metadata filters.
- No guidance on `ef_search` tuning.
- No warning about insert performance regression with HNSW.

**Phase to address:**
RAG skill authoring — database schema section must include HNSW index creation and notes on filter interaction.

---

### Pitfall 9: Agent Runaway Loops — Unbounded Cost and Infinite Iteration

**What goes wrong:**
An agent that encounters a persistent error (a failing tool, an unreachable API, a bug it cannot fix) re-invokes itself indefinitely trying to recover. Without hard iteration limits, this runs until the API rate limit or budget is exhausted. Real-world incidents have seen multi-agent research systems run for 11 days straight before detection, with API bills of $47,000. Even shorter loops can burn $50–200 in minutes.

**Why it happens:**
Agents are designed to be persistent. The framework's default behaviour is to retry or continue until the task is complete. Without explicit termination conditions, "continue until done" becomes "continue forever" when "done" is unreachable.

**How to avoid:**
Mandatory guardrails for every agent deployment:

```typescript
const MAX_TURNS = 10;
const MAX_TOKENS_PER_RUN = 50_000;
const MAX_COST_USD = 1.00;

// Fail open: raise to human, don't silently fail
if (turns > MAX_TURNS || tokensUsed > MAX_TOKENS_PER_RUN) {
  throw new AgentBudgetExceededError(`Agent exceeded limits: ${turns} turns, ${tokensUsed} tokens`);
}
```

- Set `max_turns` at the framework level (LangGraph, OpenAI Agents SDK, Anthropic).
- Implement a circuit breaker: after N consecutive tool failures on the same tool, escalate to a human-in-the-loop step rather than retrying.
- Log every tool call and token count to a persistent store before the call completes (so you can audit after a runaway).
- Set spend alerts on your LLM provider account (OpenAI, Anthropic) to send an email at 80% of budget.

**Warning signs:**
- Agent skill examples have no `max_turns` or `max_iterations` parameter.
- No `AgentBudgetExceeded` error type or escalation pattern documented.
- No mention of cost monitoring.
- Tool retry logic has no maximum retry count.

**Phase to address:**
Agent skill authoring — guardrails section must be in the main SKILL.md with code examples, not deferred to `references/`.

---

### Pitfall 10: Agent Context Accumulation — Context Rot and Sub-Agent Explosion

**What goes wrong:**
Every LLM call assembles: system prompt + tool schemas + conversation history + task context. As an agent progresses through multi-turn tasks, the conversation history grows. Research on 18 LLMs shows performance degrades reliably as context fills, even when technically within token limits — a phenomenon called "context rot". The effective usable context is often 30–50% of the advertised limit.

In multi-agent systems this compounds: if an orchestrator passes full conversation history to a sub-agent, the sub-agent's context starts near-full before doing any work. At 4+ agents, context explosion is the primary cause of reasoning failures and cost inflation.

**Why it happens:**
The path of least resistance is to pass all available context to every agent. Framework defaults often do this. Developers don't notice the degradation because individual responses look reasonable — the failure is subtle accuracy loss, not complete failure.

**How to avoid:**
- Treat sub-agents as functions: pass only the specific task, required artifacts, and minimal context. Never pass full conversation history to a sub-agent.
- Implement context summarization at configurable thresholds: when history exceeds 50% of the context window, summarize the oldest N turns into a structured JSON summary.
- Store `system_prompt_tokens + tool_schema_tokens` as a constant at startup. Use remaining budget for conversation history.
- Monitor `input_tokens` per call in telemetry. Alert if a single agent call exceeds a threshold (e.g., 30k tokens for non-long-context tasks).

**Warning signs:**
- Multi-agent examples pass `messages=conversation_history` to sub-agents without filtering.
- No context window budget accounting in the skill.
- No summarization strategy documented.
- Agent skill treats context window as unlimited.

**Phase to address:**
Agent skill authoring — context budget management must be a dedicated section with TypeScript/Python code examples.

---

### Pitfall 11: Agent Architecture — "Bag of Agents" Without Coordination Topology

**What goes wrong:**
Adding more agents to a system without defining coordination topology produces exponentially increasing error rates. Research demonstrates a "17x error trap": errors don't add across agents, they multiply. An orchestrator that randomly delegates to available agents (the "bag of agents" pattern) loses accountability — when something goes wrong, no agent is traceable as the cause.

**Why it happens:**
Teams see multi-agent demos where each agent specialises and productivity multiplies. The demos work because they have curated tasks and success paths. Production exposes the coordination problem: unstructured delegation, no role definition, no handoff schema.

**How to avoid:**
- Define agent roles explicitly before writing any code. Each agent has one responsibility.
- Use typed handoff schemas: agents pass structured objects (not free text) to the next agent.
- Implement a supervisor/coordinator pattern: a top-level coordinator routes to specialist agents; specialist agents never delegate back to the coordinator (no cycles).
- Log which agent produced each output and which agent consumed it. Trace with request IDs propagated through the handoff chain.

```typescript
interface AgentHandoff {
  taskId: string;           // propagated for tracing
  fromAgent: string;
  toAgent: string;
  input: Record<string, unknown>;
  constraints: {
    maxTurns: number;
    requiredOutputFields: string[];
  };
}
```

**Warning signs:**
- Agent skill shows agents calling each other without typed handoff interfaces.
- No coordinator/supervisor pattern documented.
- No tracing/logging pattern for inter-agent calls.
- Agent roles described as "smart assistant that can do many things".

**Phase to address:**
Agent skill authoring — handoff schema and coordination topology section must be in the main SKILL.md.

---

### Pitfall 12: Skill Documentation — Auth.js is Maintenance-Mode Since September 2025

**What goes wrong:**
Auth.js (formerly NextAuth.js) core team joined Better Auth in September 2025. The library now receives only security patches. A skill written as "use Auth.js for self-hosted auth" is directing developers toward a maintenance-mode library for new projects. The v4 → v5 migration also had a silent breaking change: session cookie renamed from `next-auth.session-token` to `authjs.session-token`, causing silent logout for all users on upgrade.

**How to avoid:**
Clerk is the primary path for new projects (managed auth). Better Auth is the self-hosted path. Auth.js coverage in the skill should be scoped to "migrating existing Auth.js projects only." Link to the official Better Auth migration guide.

**Warning signs:**
- Skill intro says "use NextAuth" or "Auth.js" as the default recommendation for new projects.
- Skill imports from `next-auth/react` in v5 examples without noting the v5 session cookie change.

**Phase to address:**
Auth skill authoring — scope decision made in the skill outline, not during writing.

---

### Pitfall 13: Skill Documentation — Scope Creep Past 500-Line Limit

**What goes wrong:**
All three new skills (Stripe, RAG, Agent) cover wide domains. The temptation is to be comprehensive. viflo's v1.1 found several skills exceeding 500 lines; they were refactored by extracting content to `references/`. This rework costs time and delays shipping.

**How to avoid:**
- Define the SKILL.md scope in the frontmatter triggers before writing any body content.
- Plan `references/` files as part of the outline phase (not as an afterthought when the file grows).
- Hard rule: if the SKILL.md outline has more than 6 top-level sections, split before writing body content.
- Run `wc -l` on the draft at each phase checkpoint; fail CI if `> 500`.

**Phase to address:**
Skill outlining phase — scope and reference structure decided before body writing begins.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcode Stripe price IDs in skill examples | Simple, copy-pasteable | Price IDs are environment-specific; developers copy literal IDs into production | Never — always show `process.env.STRIPE_PRICE_ID_PRO` |
| Use `req.json()` in Stripe webhook handler | Feels natural | Silent signature verification failure | Never |
| Skip idempotency check in webhook example | Shorter example | Duplicate charges in production | Never for subscription webhooks |
| Fixed-size chunking in RAG | Simplest implementation | Up to 9% recall degradation; hallucinations from torn semantic units | Acceptable only for very short, uniform documents |
| No HNSW index in pgvector | Faster to set up | 30–70s query time at scale vs. <50ms | Never for production tables > 1000 rows |
| No `max_turns` in agent loop | Simpler code | Runaway cost; potentially $47k incidents | Never for any agent with tool access |
| Pass full conversation history to sub-agents | Simpler architecture | Context rot; inflated costs; reasoning failures | Never — always scope sub-agent context |
| Omit `embedding_model_version` column | Simpler schema | Silent retrieval degradation on model upgrade | Never for any production RAG system |
| Auth.js as default for new projects | More tutorials available | Building on maintenance-mode library | Never for greenfield projects |
| Single-file skill with all domain content | Easier to maintain | Exceeds 500-line limit; less scannable | Never — plan `references/` split upfront |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Stripe + Next.js App Router | `await req.json()` in webhook handler | `await req.text()` — no config export needed |
| Stripe + App Router | Copy `export const config = { api: { bodyParser: false } }` from Pages Router | Remove entirely — not supported in App Router |
| Stripe + subscription state | Assuming event delivery order | Fetch current state from Stripe API on `subscription.updated` when local record missing |
| Stripe + test/production | Same env var name `STRIPE_SECRET_KEY` for test and live | Validate key prefix at startup; separate env var names |
| Auth + Stripe | Creating Stripe Customer on every login | Check `stripeCustomerId` on user record; create only if null |
| pgvector + WHERE filters | HNSW index ignored by query planner with combined filters | Benchmark; use `hnsw.iterative_scan = relaxed_order` or partial index |
| RAG + model upgrade | Re-embedding with new model without rebuilding index | Blue/green index strategy; assert model version match at query time |
| Agent + sub-agents | Passing full `messages` array to sub-agent | Pass only task + required artifacts; no history |
| Agent + Stripe writes | No idempotency key on agent-initiated Stripe API calls | Derive deterministic idempotency key from task ID + operation type |
| RAG + agent | Re-embedding documents on every agent run | Embedding is an offline pipeline step; agent only embeds the query |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| No HNSW index on pgvector | Vector queries 30–70s | `CREATE INDEX USING hnsw` after initial data load | Tables > 1000 rows |
| Embedding on every request | High latency, inflated OpenAI cost | Embed documents offline; embed only query at request time | First 100 real-user requests |
| top_k too high in RAG retrieval | Diluted context, high token cost | Start k=3–5; increase only with measured recall evidence | 1000+ chunks in index |
| Full history to sub-agents | Context explosion; inflated token cost; reasoning failures | Scope context to task + artifacts only | 4+ agent system, multi-turn tasks |
| HNSW inserts during bulk load | 5x insert slowdown | Build HNSW index after bulk load, not during | Any table with >10k initial rows |
| Synchronous Stripe webhook processing | Stripe retries; duplicates | Verify + enqueue → 200; process async | First high-traffic day |
| No max_turns on agent | Runaway cost | Hard limit every agent loop | First agent encounters an unresolvable error |
| Stripe reconciliation missing | Subscription state drift after downtime | Cron job that polls Stripe API for active customers daily | Any downtime > 3 days |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Not verifying Stripe webhook signature | Spoofed webhooks trigger fulfillment | `stripe.webhooks.constructEvent(rawBody, sig, secret)` always first |
| Test Stripe keys in production | Real checkout completes, no revenue collected | Validate key prefix at startup; spend alerts on provider |
| Leaked Stripe secret key | Attacker creates charges, accesses customer data | gitleaks/detect-secrets pre-commit (already in viflo); rotate immediately if exposed |
| Agent with write tools, no confirmation step | Agent autonomously modifies production data or initiates payments | Human-in-the-loop for destructive/financial tool calls |
| RAG: user-supplied content ingested without sanitization | Prompt injection via malicious documents | Sanitize content at ingestion; use retrieval prompt that does not forward raw text verbatim |
| RAG: logging LLM prompts containing user PII | GDPR/CCPA compliance risk | Anonymize PII before embedding; log prompt hashes not contents |
| Exposing Clerk `privateMetadata` to client | Leaks internal roles, admin flags | Serialize only named fields; never spread `currentUser()` |
| Stripe customer portal without auth check | Any user can manage any customer's subscription | Validate session user owns the Stripe customer before creating portal session |
| No `livemode` validation on webhook events | Test events processed in production | Check `event.livemode === true` before processing in production |

---

## "Looks Done But Isn't" Checklist

- [ ] **Stripe skill:** Webhook handler uses `await req.text()` — verify NOT `await req.json()`.
- [ ] **Stripe skill:** Idempotency via `stripe_events` table with UNIQUE `stripe_event_id` — verify deduplication is in the main SKILL.md.
- [ ] **Stripe skill:** Covers all critical subscription lifecycle events — verify `customer.subscription.updated`, `customer.subscription.deleted`, and `invoice.payment_failed` are documented (not just `checkout.session.completed`).
- [ ] **Stripe skill:** Test vs. live key validation at startup — verify a startup check for key prefix in production.
- [ ] **Stripe skill:** Customer portal auth guard — verify the customer portal session creation checks that the requesting user owns the Stripe customer.
- [ ] **RAG skill:** HNSW index creation in schema — verify `CREATE INDEX USING hnsw` is in the database setup section.
- [ ] **RAG skill:** `embedding_model_version` in vector table schema — verify the column exists and is documented.
- [ ] **RAG skill:** Retrieval score threshold — verify a similarity threshold check is in the query pipeline, not just "pass all results to LLM".
- [ ] **RAG skill:** Chunking strategies plural — verify fixed-size is presented as a baseline, not the recommendation; recursive + semantic alternatives are documented.
- [ ] **RAG skill:** Retrieval evaluation section — verify hit rate, precision@k, and MRR are covered (not just pipeline assembly).
- [ ] **Agent skill:** `max_turns` and `max_tokens` guardrails — verify hard limits are in every agent example with TypeScript/Python code.
- [ ] **Agent skill:** Typed handoff schema — verify a TypeScript interface for agent-to-agent handoffs is in the main SKILL.md.
- [ ] **Agent skill:** Context scoping for sub-agents — verify examples pass task + artifacts, not full conversation history.
- [ ] **Agent skill:** Cost monitoring pattern — verify token logging and spend alert setup is documented.
- [ ] **All new skills:** `last-verified:` frontmatter date present — verify before milestone close.
- [ ] **All new skills:** ≤ 500 lines — verify with `wc -l` on SKILL.md before marking complete.
- [ ] **INDEX.md:** All three new skills listed with category, difficulty, and "when to use" — verify before milestone close.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Stripe webhook duplicate fulfillment in production | HIGH | Add `processed_stripe_events` table immediately; replay events from Stripe dashboard (Events tab); audit fulfillment records for duplicates; notify affected users |
| Stripe test keys shipped to production | HIGH | Swap to live keys immediately; audit all "completed" checkouts in test mode; if any live user was affected, process refunds manually |
| RAG retrieval silent degradation after model upgrade | MEDIUM | Re-embed all documents with new model; rebuild pgvector index; validate recall on golden test set before switching production traffic |
| pgvector sequential scan at scale | LOW | `CREATE INDEX CONCURRENTLY` on live table (no downtime); test query with `EXPLAIN ANALYZE` to confirm index is used |
| Agent runaway cost incident | HIGH | Kill agent process immediately; set hard budget limits before restart; audit tool call logs for root cause; review with postmortem |
| Agent context rot causing wrong outputs | MEDIUM | Add context summarization at 50% window threshold; reduce sub-agent history scope; add per-call token telemetry |
| Skill exceeds 500 lines | LOW | Extract overflow to `references/`; update SKILL.md to link; test SKILL.md is self-contained without the reference |
| Auth + Stripe integration gap discovered post-release | MEDIUM | Add "Cross-skill integration" section to both skills; add cross-links in INDEX.md; publish companion integration example |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Stripe raw body / `req.text()` | Stripe skill authoring — first code example | Confirm `await req.text()` in webhook handler; no `req.json()` |
| Stripe webhook not idempotent | Stripe skill authoring — webhook section | Confirm `stripe_events` table with UNIQUE constraint in schema |
| Stripe event ordering | Stripe skill authoring — subscription lifecycle section | Confirm `subscription.updated` handler fetches from Stripe API if local record missing |
| Stripe test/live key confusion | Stripe skill authoring — deployment checklist | Confirm startup key prefix validation in code example |
| RAG fixed-size chunking as default | RAG skill authoring — chunking section outline | Confirm outline shows multiple strategies; fixed-size labelled "baseline only" |
| RAG embedding model drift | RAG skill authoring — data model section | Confirm `embedding_model_version` column in schema |
| RAG no retrieval evaluation | RAG skill authoring — outline phase | Confirm evaluation section in SKILL.md outline before writing begins |
| pgvector missing HNSW index | RAG skill authoring — database setup section | Confirm `CREATE INDEX USING hnsw` in schema setup |
| Agent runaway loop | Agent skill authoring — guardrails section | Confirm `max_turns` + `max_tokens` with code in main SKILL.md |
| Agent context explosion | Agent skill authoring — context budget section | Confirm sub-agent context scoping example |
| Agent "bag of agents" | Agent skill authoring — coordination topology section | Confirm typed handoff interface and supervisor pattern in main SKILL.md |
| Auth.js deprecation | Auth skill outline phase (already addressed in v1.2) | Confirm "Better Auth for new projects" stance; no v4 imports |
| Skill scope creep past 500 lines | Each skill's outline phase | Confirm outline ≤ 6 top-level sections; `references/` plan exists |
| Auth + Stripe integration gap | Integration review phase (after all skills drafted) | Cross-reference audit: each skill pair mentions the other at integration seam |
| INDEX.md not updated | Final QA phase | Confirm all three new skills appear in INDEX.md |

---

## Sources

**Stripe**
- [Next.js App Router + Stripe Webhook Signature Verification](https://kitson-broadhurst.medium.com/next-js-app-router-stripe-webhook-signature-verification-ea9d59f3593f) — `req.text()` pattern
- [App Directory Does Not Support Disabling API Body Parsing (Next.js issue #54090)](https://github.com/vercel/next.js/issues/54090) — config export not supported in App Router
- [The Race Condition You're Probably Shipping With Stripe Webhooks](https://dev.to/belazy/the-race-condition-youre-probably-shipping-right-now-with-stripe-webhooks-mj4) — two-writer problem; queue architecture
- [Best practices I wish we knew when integrating Stripe webhooks](https://www.stigg.io/blog-posts/best-practices-i-wish-we-knew-when-integrating-stripe-webhooks) — event ordering, signature window, monitoring
- [Building Reliable Stripe Subscriptions: Webhook Idempotency](https://dev.to/aniefon_umanah_ac5f21311c/building-reliable-stripe-subscriptions-in-nestjs-webhook-idempotency-and-optimistic-locking-3o91) — optimistic locking
- [Stripe API Keys best practices](https://docs.stripe.com/keys-best-practices) — test vs. live key management
- [Stripe go-live checklist](https://docs.stripe.com/get-started/checklist/go-live) — official deployment checklist
- [Risks of a Leaked Stripe API Key](https://trufflesecurity.com/blog/the-risks-of-a-leaked-stripe-api-key) — key exposure consequences

**RAG / Vector Search**
- [Ten Failure Modes of RAG Nobody Talks About](https://dev.to/kuldeep_paul/ten-failure-modes-of-rag-nobody-talks-about-and-how-to-detect-them-systematically-7i4) — embedding drift, context position bias, citation hallucination
- [Chunking Strategies to Improve LLM RAG Pipeline Performance](https://weaviate.io/blog/chunking-strategies-for-rag) — Weaviate official guide
- [Best Chunking Strategies for RAG in 2025](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025) — semantic vs. fixed-size comparison
- [RAG at Scale: How to Build Production AI Systems in 2026](https://redis.io/blog/rag-at-scale/) — Redis production guide; embedding drift monitoring
- [Building Production RAG Systems in 2026](https://brlikhon.engineer/blog/building-production-rag-systems-in-2026-complete-tutorial-with-langchain-pinecone) — production architecture patterns
- [HNSW Indexes with Postgres and pgvector](https://www.crunchydata.com/blog/hnsw-indexes-with-postgres-and-pgvector) — Crunchy Data guide
- [pgvector HNSW index not used for KNN queries (GitHub issue #835)](https://github.com/pgvector/pgvector/issues/835) — query planner filter interaction
- [RAG Evaluation: A Complete Guide for 2025](https://www.getmaxim.ai/articles/rag-evaluation-a-complete-guide-for-2025/) — faithfulness, precision, recall metrics

**Agent Architecture**
- [Why Your Multi-Agent System is Failing: The 17x Error Trap](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/) — bag of agents anti-pattern; coordination topology
- [Cost Guardrails for Agent Fleets](https://medium.com/@Micheal-Lanham/cost-guardrails-for-agent-fleets-how-to-prevent-your-ai-agents-from-burning-through-your-budget-ea68722af3fe) — token runaway; $47k incident
- [The Context Window Problem: Scaling Agents Beyond Token Limits](https://factory.ai/news/context-window-problem) — context rot research
- [Architecting efficient context-aware multi-agent framework](https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/) — Google ADK guide
- [Read This Before Building AI Agents: Lessons From The Trenches](https://dev.to/isaachagoel/read-this-before-building-ai-agents-lessons-from-the-trenches-333i) — over-abstraction; single agent first
- [AgentGuard: Real-time guardrail for token spend](https://github.com/dipampaul17/AgentGuard) — open source token guardrail implementation
- [The Economics of Autonomy: Preventing Token Runaway in Agentic Loops](https://www.alpsagility.com/cost-control-agentic-systems) — budget guardrail patterns

---

*Pitfalls research for: v1.3 Expert Skills — Stripe Payments, RAG/Vector Search, Agent Architecture*
*Researched: 2026-02-24*
