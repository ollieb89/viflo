# Feature Research

**Domain:** Skill file library — Auth, Stripe, RAG/vector search, Agent architecture, Prompt engineering
**Researched:** 2026-02-24
**Confidence:** HIGH (Auth, Stripe), MEDIUM (RAG, Agent), MEDIUM (Prompt Engineering)

---

## Context

This research covers five new skill areas for viflo v1.2. These are not product features —
they are *documentation modules* (SKILL.md + references/) that an AI coding assistant loads
at task time. The audience is a solo developer or small team using viflo with Claude Code or
a similar agentic tool. The question for each skill is: what must the skill cover to be
immediately useful when the AI picks it up mid-task?

Existing viflo skills this work depends on:
- `postgresql` — covers pgvector briefly; RAG skill extends this
- `fastapi-templates` — FastAPI app structure; Auth and Stripe backends build on this
- `frontend` / `frontend-dev-guidelines` — Next.js App Router; Auth skill extends this
- `ci-cd-pipelines` — CI patterns; Prompt Engineering skill's evaluation/CI section connects here

---

## Skill 1: Auth Systems (Clerk + Auth.js/NextAuth)

### Table Stakes (Users Expect These)

Features a developer assumes the skill covers. Missing these = skill feels useless.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Clerk quick-start for Next.js App Router | Most solo devs reach for Clerk first — fastest path | LOW | Cover `clerkMiddleware`, `auth()`, `SignIn`/`SignUp` components |
| Auth.js v5 (NextAuth) setup + `auth()` universal function | Open-source alternative; zero vendor lock-in | MEDIUM | Auth.js v5 unified `auth()` works in server components, route handlers, proxy.ts, server actions |
| Protected routes via middleware (proxy.ts in Next.js 16) | Core security pattern; every app needs this | MEDIUM | Next.js 16 renames `middleware.ts` → `proxy.ts`; skill must reflect this |
| OAuth provider wiring (GitHub, Google) | Devs assume social login is covered | MEDIUM | Cover both Clerk social connections and Auth.js provider config |
| Session access in server components + server actions | App Router default pattern; no client-side session juggling | MEDIUM | Validate session at data access layer, not just middleware |
| Sign-in / sign-out / sign-up flows | Core UX flows every app needs | LOW | Clerk: drop-in components. Auth.js: build-your-own with `signIn()`/`signOut()` |
| Environment variable setup and secrets | Every integration starts here; mistakes are common | LOW | Clerk public/secret keys, Auth.js `AUTH_SECRET`, callback URLs |

### Differentiators (Competitive Advantage)

Features that make this skill exceptional versus looking up the official docs.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Cache / caching pitfall for authenticated content | App Router's cache can leak User A's data to User B — not obvious | LOW | Single callout box: user-specific data must bypass all caching layers |
| When to choose Clerk vs Auth.js decision tree | Docs never tell you which to pick; skill makes this explicit | LOW | Clerk = speed + managed; Auth.js = control + self-hosted |
| Data Access Layer (DAL) pattern for real security | Middleware alone is not enough; DAL is where actual security lives | MEDIUM | Each sensitive DB/API call re-validates session independently |
| Role-based access control (RBAC) skeleton | Most apps need at least admin vs user distinction | MEDIUM | Clerk metadata vs Auth.js JWT callbacks; keep to a pattern, not full RBAC library |
| Webhook receiver for Clerk user lifecycle events | Clerk fires webhooks on user create/update/delete; devs need to sync to their own DB | MEDIUM | Svix signature verification, upsert user pattern |

### Anti-Features (Scope Creep to Avoid)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full custom auth from scratch (JWT + bcrypt) | "I don't want vendor lock-in" | Multi-week rabbit hole; security mistakes are catastrophic; out of scope for this skill | Use Auth.js for self-hosted with full control |
| Magic link / passwordless deep dive | Useful, but niche | Blows the 500-line budget; secondary flow | Single paragraph pointing to Clerk/Auth.js docs |
| Auth0 / WorkOS / Supabase Auth coverage | Mentioned in comparisons | Scope creep — project spec says Clerk + Auth.js | Call out in skill frontmatter that other providers are out of scope |
| Multi-tenancy / organization management | Clerk has Orgs feature | Complex enough for its own skill | One-sentence mention with link to Clerk Orgs docs |
| Full RBAC library integration (CASL, etc.) | Teams want fine-grained permissions | Standalone topic; adds a dependency | Refer to architecture-patterns skill |

---

## Skill 2: Stripe Payments

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Checkout Session creation (one-time payment) | Simplest Stripe flow; every payment skill must cover it | LOW | `stripe.checkout.sessions.create()`, `success_url`, `cancel_url` |
| Subscription setup with Stripe Billing | SaaS use case; the most common reason devs reach for Stripe | MEDIUM | Products + Prices + `subscription_data`; portal link |
| Webhook receiver with signature verification | Critical security step; #1 production mistake | MEDIUM | `stripe.webhooks.constructEvent()`, raw body requirement in Next.js route handlers |
| Idempotent webhook handler (dedup by `event.id`) | Stripe retries events; duplicate processing causes double charges | MEDIUM | Log `event.id` before processing; check before acting |
| Environment variable split (test vs live keys) | #2 common mistake; mixing keys corrupts production | LOW | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` |
| Customer portal for self-serve billing management | Users expect to update cards and cancel themselves | LOW | `stripe.billingPortal.sessions.create()`; one redirect |
| Storing Stripe IDs (not payment data) in your DB | PCI DSS: never store card data; store `customer_id`, `subscription_id` | LOW | Schema pattern: `stripe_customer_id`, `stripe_subscription_id` on user table |
| Key Stripe events to handle | Devs don't know which events matter | LOW | `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed` |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Async webhook processing pattern | 20-second Stripe timeout bites devs; return 200 fast then process | MEDIUM | Acknowledge immediately after signature verification; push to queue or background job |
| Subscription status sync pattern | Subscription state lives in Stripe, not your DB — sync strategy matters | MEDIUM | Webhook-driven upsert to `subscriptions` table; never trust only your DB |
| Stripe CLI local webhook testing | Devs spend hours debugging webhooks; `stripe listen --forward-to` solves it | LOW | Short code block; massively reduces friction |
| Test card cheat sheet | Everyone needs `4242 4242 4242 4242` and failure scenarios | LOW | Include declined, auth-required, dispute cards in a quick-reference table |
| Metered / usage-based billing skeleton | Increasingly common for AI products charging per token/call | HIGH | Short mention only — flag as complex; point to Stripe metered usage docs |

### Anti-Features (Scope Creep to Avoid)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full PCI DSS compliance documentation | "We handle payments so we need this" | Viflo already has a `pci-compliance` skill | Reference that skill; don't duplicate |
| Custom payment form (Stripe Elements) | Some devs want full control of UI | Complex; Stripe Checkout covers 90% of use cases | One paragraph: use Checkout unless brand control is a hard requirement |
| Connect / marketplace payments | Multi-vendor payouts | Entirely different product; own skill territory | Out of scope callout in frontmatter |
| Invoicing API deep dive | B2B invoicing is a valid use case | Niche; blows budget | One-sentence mention with link |
| Tax calculation (Stripe Tax) | Automatic tax is attractive | Changes frequently; regulatory complexity | Reference Stripe Tax docs only |

---

## Skill 3: RAG / Vector Search

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Embedding pipeline: chunk → embed → store | The core RAG loop; skill is useless without this | MEDIUM | Text splitting, `text-embedding-3-small` via OpenAI, insert to pgvector |
| pgvector setup and schema | viflo stack uses PostgreSQL; pgvector is the natural fit | MEDIUM | `CREATE EXTENSION vector`, `vector(1536)` column, `ivfflat`/`hnsw` index |
| Cosine similarity query | The retrieval half of RAG; equally important as ingestion | MEDIUM | `<=>` operator; `ORDER BY embedding <=> $1 LIMIT 10` pattern |
| Chunking strategy with overlap | Biggest performance lever; most tutorials skip it | MEDIUM | 500-token chunks, 10-20% overlap; semantic boundary awareness |
| Embedding model consistency rule | Single most common RAG bug: query and index use different models | LOW | Bold callout: index model must match query-time model, forever |
| Basic RAG query loop: embed query → retrieve → inject into prompt | The full assembly; devs need to see end-to-end | MEDIUM | Python snippet showing embed → SELECT → f-string prompt construction |
| When to use pgvector vs Pinecone | Devs need a decision rule, not a library overview | LOW | pgvector: ≤1M vectors, PostgreSQL already in stack; Pinecone: >1M vectors or dedicated search team |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Hybrid search (vector + BM25/full-text) | Consistently outperforms pure vector search; most tutorials skip it | HIGH | pgvector + PostgreSQL `tsvector`; RRF (Reciprocal Rank Fusion) to merge scores |
| Chunking pitfall: tiny chunks cause hallucinations | 128-token chunks split mid-concept; leads to fragmented context | LOW | Explicit warning with the failure mode: retrieves sentence fragments → hallucination |
| Index synchronization strategy | Updating documents after ingestion is harder than first indexing | MEDIUM | Delete-and-reinsert vs. update; trigger-based re-embedding tradeoffs |
| Retrieval evaluation with a sample test set | "My RAG feels wrong" is not actionable; this gives a method | MEDIUM | Build 20-question golden set; measure precision@5 before deploying |
| Observability: log retrieved chunks with every LLM call | Without this, debugging is guesswork | LOW | Pattern: log query, top-k chunks, and final prompt in same trace |

### Anti-Features (Scope Creep to Avoid)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Fine-tuning embedding models | "Custom embeddings will be better" | Requires ML expertise and GPU budget; out of scope for viflo | Use `text-embedding-3-small`; it's excellent and cheap |
| Full LangChain integration deep dive | LangChain is popular | LangChain changes rapidly; abstracts away understanding of the actual pipeline | Show the raw pattern first; mention LangChain as an option |
| Multimodal RAG (images, audio) | Emerging use case | Entirely different pipeline; no pgvector support | One-sentence future reference |
| GraphRAG / knowledge graphs | Interesting research topic | Production complexity 10x; no standard tooling | Out of scope callout |
| Pinecone setup as primary path | Some devs want managed vector DB | viflo stack is PostgreSQL-first; pgvector keeps the stack simple | Cover Pinecone in a references/ file, not primary path |

---

## Skill 4: Agent Architecture

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Core agent loop: perceive → reason → act | Foundational mental model; every agent skill must start here | LOW | Diagram + description; not framework-specific |
| Tool/function calling pattern | Agents are useless without tools; this is the mechanism | MEDIUM | OpenAI function calling schema or Anthropic tool_use block; include Python type-annotated example |
| Orchestrator–worker pattern | Most common multi-agent pattern; high practical value | MEDIUM | One orchestrator routes tasks to specialist workers; show with code |
| Memory types: in-context, external, episodic | Agents without memory degrade; devs need the taxonomy | MEDIUM | In-context (conversation history), external (vector store), episodic (structured DB log) |
| Handoff pattern between agents | "How does Agent A pass work to Agent B?" | MEDIUM | Structured handoff object: task, context, constraints; show the data contract |
| Guardrails: input validation + output validation | Agents in production without guardrails cause real harm | MEDIUM | Schema validation on tool inputs; confidence thresholds before acting |
| When NOT to use agents | Agents are overused; this is genuinely valuable | LOW | Single-step tasks, latency-sensitive paths, and tasks with deterministic correct answers do not need agents |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Anthropic's 6 composable patterns (from official docs) | Vendor-aligned, battle-tested; matches viflo's Claude Code environment | MEDIUM | Prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer — brief description of each |
| MCP (Model Context Protocol) overview | Industry converging on MCP for agent-tool communication; viflo already uses it | MEDIUM | What it is, when it adds value vs. direct tool calling; point to viflo's own MCP usage |
| Failure budget / partial failure handling | Agents fail silently; teams discover broken runs days later | HIGH | Explicit retry strategy, fallback to human-in-the-loop, dead-letter log pattern |
| Token budget awareness for long agent runs | Long chains exhaust context; a common production surprise | LOW | Callout: summarize intermediate results, don't accumulate full histories |
| Tracing and observability first | Without traces, multi-agent debugging is impossible | MEDIUM | Log: agent name, tool name, input, output, latency, token count per step |

### Anti-Features (Scope Creep to Avoid)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full LangGraph / LangChain deep dive | Popular framework | Framework-specific; changes rapidly; obscures core patterns | Show patterns in plain Python; mention LangGraph as implementation option |
| AutoGen / CrewAI / other framework tutorials | "Which framework should I use?" | Framework churn is high; this is a patterns skill not a framework survey | One comparison table in references/; not primary content |
| Autonomous long-running agent without human oversight | Seems powerful | High failure rate in production; safety risk | Always design for human-in-the-loop checkpoints; this is a design principle to enforce |
| Agent fine-tuning | "I want a specialized agent" | Requires ML infrastructure; out of scope for viflo | Use system prompt engineering + tool definition instead |
| Full agent platform setup (Vertex AI Agents, etc.) | Managed convenience | Cloud-specific; violates viflo's tool-agnostic principle | Cover in cloud-deployment skill if needed |

---

## Skill 5: Prompt Engineering

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Prompt anatomy: role, context, task, output contract | Structural foundation; most prompts fail because one piece is missing | LOW | Name each component; show a before/after example |
| System prompt vs user message vs assistant prefill | Model-level mechanics devs misuse | LOW | When to put instructions in system vs user turn; prefill for output shaping |
| Few-shot examples | Most effective single technique for format compliance | LOW | Show 1-3 examples in prompt; when examples help vs hurt |
| Chain of thought (CoT) prompting | Standard technique for reasoning tasks | LOW | "Think step by step" and structured scratchpad variants |
| Output format specification | "The model keeps returning JSON in markdown code blocks" | LOW | Explicit schema + example + negative example in prompt |
| Iterative refinement workflow | Devs don't know how to systematically improve prompts | MEDIUM | Measure → identify failure mode → hypothesize fix → test on 10 examples → compare |
| Prompt versioning in files (not hardcoded strings) | Most common anti-pattern causing prod regressions | LOW | Store prompts in `.prompts/` directory with semantic versioning; never embed in application code |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Anti-pattern catalogue (top 5) | Negative examples are more memorable than positive rules | LOW | (1) Vague task description, (2) missing output contract, (3) too long with no priority, (4) conflicting instructions, (5) prompt injection surface |
| Evaluation without a platform (golden set method) | Teams think they need LangSmith before they can evaluate; they don't | MEDIUM | Build 20-example golden set in a JSON file; score with `assert` or simple rubric; run in CI |
| LLM-as-judge pattern | Automated quality scoring without manual review | MEDIUM | Use a second LLM call with a rubric prompt; useful for open-ended outputs |
| Prompt injection awareness | Security concern specific to prompts; often ignored | LOW | User input in prompts creates injection surface; delimiting and input sanitization patterns |
| Model-specific tuning notes (Claude vs GPT-4o) | Prompts don't port perfectly between models | LOW | Claude: respond well to XML tags, explicit role instructions; GPT: strong with JSON mode |
| Context window budget management | Long prompts cost money and degrade quality past threshold | LOW | Prioritize instructions at top, examples in middle, data last; trim ruthlessly |

### Anti-Features (Scope Creep to Avoid)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full PromptOps platform setup (LangSmith, Maxim, etc.) | Teams want managed tooling | Vendor-specific; changes fast; high setup friction for solo devs | Mention platforms in references/; primary skill uses file-based approach |
| Automated prompt A/B testing infrastructure | Sounds rigorous | Requires traffic volume and statistical significance; overkill for v1.2 | Manual comparison with golden set is sufficient |
| Fine-tuning as prompt alternative | "If prompts fail, fine-tune" | Separate discipline entirely; expensive; out of scope | Note: exhaust prompt engineering before considering fine-tuning |
| Red teaming / adversarial testing deep dive | Important for safety | Dedicated topic; exceeds skill budget | One callout: point to Promptfoo for red-teaming |
| Image / multimodal prompting | Vision models are gaining use | Different enough to need its own skill; budget risk | Out of scope callout in frontmatter |

---

## Feature Dependencies

```
Auth skill
    └──extends──> frontend (Next.js App Router patterns)
    └──extends──> fastapi-templates (protected API endpoints)

Stripe skill
    └──extends──> fastapi-templates (webhook route handlers)
    └──depends on──> Auth skill (customer-to-user mapping requires authenticated user)
    └──references──> pci-compliance (existing skill; do not duplicate)

RAG skill
    └──extends──> postgresql (pgvector type already mentioned)
    └──extends──> fastapi-templates (embedding pipeline as FastAPI background task)
    └──enhances──> Agent skill (agents can use RAG as a retrieval tool)

Agent skill
    └──uses──> RAG skill (retrieval tool for memory)
    └──uses──> Prompt Engineering skill (system prompt design for agents)
    └──references──> workflow-orchestration-patterns (existing skill)

Prompt Engineering skill
    └──enhances──> Agent skill (system prompts, tool descriptions)
    └──enhances──> RAG skill (query-time prompt construction)
    └──references──> ci-cd-pipelines (evaluation in CI)
```

### Dependency Notes

- **Stripe requires Auth:** You need an authenticated user ID to create a Stripe Customer and map subscriptions to your user table. Build Auth first.
- **RAG extends postgresql:** The postgresql skill already mentions `pgvector` and the `vector` type. The RAG skill picks up from there with full pipeline coverage.
- **Agent and Prompt Engineering are mutually reinforcing:** Agent system prompts are the most important prompts to get right. Teach Prompt Engineering before or alongside Agent Architecture.
- **RAG feeds Agent memory:** Treat RAG as the external memory tool for agents. The skills should cross-reference each other.

---

## MVP Definition (Per Skill — What Ships in v1.2)

### Launch With (each skill's SKILL.md)

These sections are required in every SKILL.md to meet the ≤500-line constraint:

- [ ] Frontmatter (name, description, triggers) — discoverable by agents
- [ ] "When to use this skill" section — prevents mis-triggering
- [ ] Core pattern(s) with annotated code — the reason the skill exists
- [ ] Gotchas / pitfalls callout box — highest-density value
- [ ] Decision rule (when to use X vs Y) — removes ambiguity

### Add to references/ (overflow content)

- [ ] Full code examples (>30 lines) that would blow the 500-line SKILL.md budget
- [ ] Extended comparison tables
- [ ] Step-by-step setup walkthroughs
- [ ] Links to official docs with version pins

### Future Consideration (v1.3+)

- [ ] Auth: RBAC skill using CASL or similar
- [ ] Stripe: Connect / marketplace payments skill
- [ ] RAG: Multimodal retrieval (images, audio)
- [ ] Agents: Full LangGraph workflow patterns skill
- [ ] Prompt Engineering: Automated evaluation CI pipeline (blocked by `AUTO-01` being out of scope)

---

## Feature Prioritization Matrix

| Skill / Feature | User Value | Implementation Cost | Priority |
|----------------|------------|---------------------|----------|
| Auth: Clerk + Auth.js quick-start | HIGH | LOW | P1 |
| Auth: Protected routes (proxy.ts) | HIGH | LOW | P1 |
| Auth: DAL re-validation pattern | HIGH | LOW | P1 |
| Auth: Cache pitfall callout | HIGH | LOW | P1 |
| Stripe: Checkout + subscriptions | HIGH | LOW | P1 |
| Stripe: Webhook with idempotency | HIGH | MEDIUM | P1 |
| Stripe: Async processing pattern | HIGH | LOW | P1 |
| RAG: Embed → store → query loop | HIGH | MEDIUM | P1 |
| RAG: pgvector schema + index | HIGH | LOW | P1 |
| RAG: Chunking strategy + pitfalls | HIGH | LOW | P1 |
| RAG: Hybrid search pattern | MEDIUM | HIGH | P2 |
| Agent: Core loop + tool calling | HIGH | MEDIUM | P1 |
| Agent: Orchestrator-worker pattern | HIGH | MEDIUM | P1 |
| Agent: Memory taxonomy | MEDIUM | LOW | P1 |
| Agent: Guardrails pattern | HIGH | MEDIUM | P2 |
| Prompt: Anatomy + output contract | HIGH | LOW | P1 |
| Prompt: Anti-pattern catalogue | HIGH | LOW | P1 |
| Prompt: Golden set evaluation | MEDIUM | MEDIUM | P1 |
| Prompt: Prompt injection awareness | MEDIUM | LOW | P2 |
| Prompt: Versioning in files | HIGH | LOW | P1 |

---

## Sources

- Auth research: [Authentication in Next.js App Router — WorkOS 2026](https://workos.com/blog/nextjs-app-router-authentication-guide-2026), [Clerk complete auth guide](https://clerk.com/articles/complete-authentication-guide-for-nextjs-app-router), [Auth.js protecting routes](https://authjs.dev/getting-started/session-management/protecting)
- Stripe research: [Stripe webhooks official docs](https://docs.stripe.com/billing/subscriptions/webhooks), [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests), [Best practices for Stripe webhooks — Stigg](https://www.stigg.io/blog-posts/best-practices-i-wish-we-knew-when-integrating-stripe-webhooks)
- RAG research: [Chunking strategies — dasroot.net Feb 2026](https://dasroot.net/posts/2026/02/chunking-strategies-rag-performance/), [RAG at Scale — Redis 2026](https://redis.io/blog/rag-at-scale/), [Optimizing RAG with hybrid search — Superlinked](https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking)
- Agent research: [Anthropic composable agent patterns](https://aimultiple.com/building-ai-agents), [AI Agent Orchestration Patterns — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns), [OpenAI multi-agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/)
- Prompt engineering research: [PromptOps complete guide — Adaline 2026](https://www.adaline.ai/blog/complete-guide-prompt-engineering-operations-promptops-2026), [Prompt engineering best practices — Palantir](https://www.palantir.com/docs/foundry/aip/best-practices-prompt-engineering), [IBM 2026 prompt engineering guide](https://www.ibm.com/think/prompt-engineering)

---

*Feature research for: viflo v1.2 skills expansion*
*Researched: 2026-02-24*
