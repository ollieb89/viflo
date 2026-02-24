# Pitfalls Research

**Domain:** Skill documentation — Auth, Stripe, RAG/vector search, Agent architecture, Prompt engineering
**Researched:** 2026-02-24
**Confidence:** MEDIUM (WebSearch-verified; specific viflo skill-doc context is synthesized from first principles + evidence)

---

## Critical Pitfalls

### Pitfall 1: Auth.js / NextAuth is mid-migration — the team moved to Better Auth

**What goes wrong:**
Auth.js (formerly NextAuth.js) announced in September 2025 that the core team joined Better Auth. The library receives only security patches now. A skill written as "use Auth.js" guidance becomes stale immediately and points developers toward a maintenance-mode library for new projects.

**Why it happens:**
The v4 → v5 migration was disruptive enough (cookie name changes, broken sessions, env var renames) that many tutorials froze on v4 examples. Developers copying skill guidance write v4 code into v5 projects or build on Auth.js when Better Auth is now the community default for new Next.js projects.

**How to avoid:**
- The Auth skill must cover Clerk as the primary path and explicitly position Auth.js / Better Auth as the self-hosted alternative, not Auth.js v5 as the default.
- If Auth.js is covered, scope it clearly to "existing projects only" and document the v4 → v5 cookie rename (`next-auth.session-token` → `authjs.session-token`) that silently logs users out on upgrade.
- Link to the official Better Auth migration guide, not the Auth.js main docs.
- Add a frontmatter `version:` field and a `last-verified:` date so the skill signals when it needs review.

**Warning signs:**
- Skill uses `NEXTAUTH_SECRET` / `NEXTAUTH_URL` env var names (v4-era) without noting v5 renames.
- Skill's intro says "use NextAuth" without mentioning Better Auth.
- Skill references `import { getServerSession } from 'next-auth'` without v5 shim notes.

**Phase to address:**
Auth skill authoring phase — establish the "Clerk primary / self-hosted via Better Auth" stance in the skill outline before writing the body.

---

### Pitfall 2: Clerk middleware misconfiguration causes silent auth bypass

**What goes wrong:**
Clerk requires `clerkMiddleware()` in `middleware.ts` at the project root. If a developer forgets this or places it under `src/` when the project root expects it (or vice versa), the `auth()` helper throws a runtime error — or worse, returns `null` for auth state silently, making every route appear public. The Clerk docs even have a dedicated error page for this: "auth() was called but Clerk can't detect usage of clerkMiddleware()".

**Why it happens:**
The skill is written assuming a clean project setup. Real projects have pre-existing middleware (rate limiting, logging, i18n redirects). Developers merge the Clerk middleware without understanding that Next.js supports only one `middleware.ts`. The skill does not warn about this composition problem.

**How to avoid:**
- Explicitly warn: "Only one `middleware.ts` is allowed. Compose Clerk with any existing middleware inside that single file."
- Provide a pattern for chaining middleware (Clerk + i18n + rate limiting) rather than just the standalone Clerk example.
- Document `prefetch={false}` on `Link` components pointing to protected routes — without it, prefetch fires as an unauthenticated request and returns 401, breaking Next.js prefetch.
- Document `privateMetadata` — never pass the full `currentUser()` object to client components; only destructure needed fields.

**Warning signs:**
- SKILL.md only shows standalone `clerkMiddleware()` with no composition example.
- No mention of `prefetch={false}` in the protected-route section.
- No mention of `privateMetadata` exposure risk.

**Phase to address:**
Auth skill authoring phase — add middleware composition pattern and data exposure warnings before the skill is marked done.

---

### Pitfall 3: Stripe webhook handler is not idempotent — duplicate charges in production

**What goes wrong:**
Stripe retries webhook delivery for up to 3 days if your endpoint returns a non-2xx response or times out. If the handler processes synchronously and is slow, Stripe retries while the first invocation is still running. Both complete, resulting in duplicate order fulfillment, duplicate emails, or double subscription activation.

**Why it happens:**
Tutorial-level Stripe examples show `stripe.webhooks.constructEvent()` → process inline → return 200. This works in development but fails under load. The skill must teach the queue-then-process pattern, not the inline-process pattern.

**How to avoid:**
- Document the correct pattern: verify signature → store raw event in DB with `event.id` as unique key → return 200 immediately → process asynchronously.
- Include idempotency key check: `SELECT 1 FROM processed_events WHERE stripe_event_id = $1` before processing.
- Document the 5-minute signature verification window — timestamp drift beyond 300 seconds causes `constructEvent` to throw.
- Warn that Stripe stops retrying after 3 days; implement a reconciliation job that polls Stripe API for subscription state if your system was down.

**Warning signs:**
- Skill's webhook example processes events inline before returning 200.
- No mention of `stripe_event_id` deduplication in the database section.
- No mention of the 300-second timestamp window.

**Phase to address:**
Stripe skill authoring phase — idempotency pattern must be in the main SKILL.md body, not a reference doc, because it is critical and frequently skipped.

---

### Pitfall 4: RAG skill conflates retrieval quality with generation quality — hallucinations appear fixed when they are not

**What goes wrong:**
A skill that teaches "connect embeddings → vector search → pass chunks to LLM" makes RAG look solved. Developers ship this and see reasonable demo results. In production, low-quality retrieval (wrong chunks, too-small chunk size, mismatched embedding model) causes the LLM to hallucinate because the context does not contain the answer. Developers blame the LLM rather than the retrieval step.

**Why it happens:**
RAG tutorials focus on the happy path: the right chunk is retrieved and the LLM summarizes it. They do not teach how to measure retrieval quality separately from generation quality. Without that separation, developers cannot diagnose which layer is failing.

**How to avoid:**
- The skill must cover evaluation as a first-class section: retrieval precision/recall separately from answer faithfulness.
- Document the chunking tradeoff explicitly: chunks too small → context torn, wrong answers; chunks too large → noise dilutes the signal.
- Recommend semantic chunking or proposition-based chunking over fixed-size splitting for domain-specific content.
- Document the embedding model mismatch problem: if you embed with `text-embedding-3-small` at index time but query with a different model, retrieval degrades silently.
- Include a "retrieval score threshold" pattern — if the top result's similarity score is below a threshold, return "I don't know" rather than hallucinate.

**Warning signs:**
- Skill has no section on evaluating retrieval quality.
- Skill recommends fixed-size chunking without discussing alternatives.
- Skill does not mention embedding model version pinning.
- Skill has no guidance on what to do when no relevant chunks are found.

**Phase to address:**
RAG skill authoring phase — evaluation section must appear in the main SKILL.md, not deferred to a reference doc.

---

### Pitfall 5: Agent skill scope creep — tries to be an orchestration framework manual

**What goes wrong:**
Agent architecture is a wide topic (single agent, multi-agent, orchestrator/subagent, memory, tool selection, handoffs). A skill that tries to document all of it exceeds the 500-line limit, contains contradictory patterns (when to use each), and becomes too abstract to apply. Developers read it and still don't know what to build.

**Why it happens:**
The domain is genuinely large, and the temptation is to be comprehensive. viflo's existing skills that exceeded 500 lines were caught and split in v1.1; the agent skill must be scoped from the start to avoid the same rework.

**How to avoid:**
- Define the skill's scope in the frontmatter triggers as "designing agent task decomposition and handoff patterns" — not "building agentic systems from scratch."
- Focus the SKILL.md on: when to use a single agent vs. multi-agent, how to structure handoffs, context budget management, and failure modes.
- Extract implementation-heavy content (framework comparisons, memory store setup, tool registry patterns) into `references/` from day one.
- Hard limit: if the outline has more than 6 top-level sections, split before writing.

**Warning signs:**
- Skill outline includes framework comparison (LangGraph vs. CrewAI vs. custom) as a main section.
- Skill covers memory types (in-context, external, episodic) in exhaustive detail in the main file.
- Draft exceeds 400 lines before the code examples section.

**Phase to address:**
Agent skill outline phase — scope decision made during outlining, not during writing.

---

### Pitfall 6: Prompt engineering skill goes stale within one model release cycle

**What goes wrong:**
Prompt engineering techniques are tightly coupled to model behavior. Chain-of-thought works differently on reasoning models (o3, DeepSeek R1) than on instruction-tuned models (Claude, GPT-4). A skill written for one model generation is actively harmful advice for the next. The 2025 pattern of "add 'think step by step'" can hurt performance on reasoning models that already reason internally.

**Why it happens:**
Prompt engineering knowledge accretes. A skill assembled from current best practices becomes a mix of techniques that conflict across model families. The skill does not declare which model family each technique applies to.

**How to avoid:**
- Scope every technique with a `Applies to:` tag: instruction-tuned models, reasoning models, or both.
- Add a `last-verified-against:` frontmatter field listing the specific model versions verified (e.g., `claude-sonnet-4-6`, `gpt-4o`, `o3`).
- The evaluation section must be model-agnostic: always measure, never assume a technique works.
- Explicitly warn about the 2025 anti-pattern: using chain-of-thought prompting on reasoning models that already do internal reasoning — it can degrade output quality.

**Warning signs:**
- Skill has no version metadata.
- All techniques presented as universally applicable.
- No distinction between instruction-tuned and reasoning model families.
- "Think step by step" recommended without qualification.

**Phase to address:**
Prompt engineering skill authoring phase — model-tagging convention defined in frontmatter before writing begins.

---

### Pitfall 7: Skills cross-reference each other incorrectly — Auth + Stripe integration gap

**What goes wrong:**
A common real-world pattern is: authenticated user → Stripe Customer → subscription gate → protected route. If the Auth skill and Stripe skill are written independently, neither covers the junction: how to create a Stripe Customer on signup, how to store `stripeCustomerId` on the user record, how to protect routes based on subscription tier. Developers reach the integration point and find no guidance in either skill.

**Why it happens:**
Each skill is designed to be self-contained. This is correct for most content but creates gaps at the exact integration seams that developers most frequently need help with.

**How to avoid:**
- Both skills must have a "Cross-skill integration" section that points to the other skill and documents the handoff point.
- Auth skill: document `stripe_customer_id` on the user model as a field to provision at signup; link to Stripe skill's customer creation pattern.
- Stripe skill: document that the Clerk `userId` (or session user ID) is the lookup key for Stripe Customer; warn against creating duplicate Customers by always checking before creating.
- Agent skill: document how to pass auth context through tool calls so agents can make authenticated API requests.

**Warning signs:**
- Auth SKILL.md has no mention of Stripe or payment gating.
- Stripe SKILL.md has no mention of auth user ID as the customer lookup key.
- INDEX.md does not link the skills as related.

**Phase to address:**
Final integration review phase — after individual skills are drafted, audit cross-references before marking skills complete.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcode Stripe price IDs in skill examples | Simple, copy-pasteable code | Price IDs are environment-specific and rotate; developers copy the literal ID into production | Never — always show env var reference: `process.env.STRIPE_PRICE_ID_PRO` |
| Skip idempotency in webhook example | Shorter, simpler example | Duplicate charges in production; hardest class of Stripe bug to debug | Never for subscription webhooks; marginal risk for one-time payments |
| Use Auth.js v4 examples because they are more widely available | More tutorials to reference | v4 is unmaintained; session cookie name breaks on upgrade | Never for new skills — document v5 or Better Auth |
| Generic RAG pipeline without evaluation | Faster to write | Hallucination bugs that are invisible until production | Never — evaluation is not optional for shipped RAG |
| Single-file prompt engineering skill with all techniques | Easier to maintain one file | Stale advice for half the model families within 6 months | Never — use model-tagged sections or separate reference files |
| Omit cross-skill references to keep skills self-contained | Cleaner skill boundaries | Critical integration seams (Auth + Stripe, Auth + Agent) have no documented path | Never — cross-skill sections should be short and explicitly scoped |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Auth + Stripe | Creating a Stripe Customer on every login instead of on first signup | Check `stripeCustomerId` on user record; create only if null; store the ID immediately |
| Auth + RAG | Passing full `currentUser()` object into RAG context | Extract only the user's role/tier and inject as metadata filter on vector search to scope retrieval |
| Stripe + Agent | Agent calls Stripe API without idempotency key | Every agent-initiated Stripe write must include a deterministic idempotency key derived from the task ID |
| RAG + Agent | Agent re-embeds the same documents on every run | Embedding pipeline must be a one-time or incremental step, not an agent activity per request |
| Prompt skill + all others | Writing prompts that assume a specific model | Tag every prompt template with the model family it was tested against; provide fallbacks |
| Clerk + Next.js prefetch | `<Link href="/dashboard">` on public page triggers 401 prefetch | Add `prefetch={false}` to all Link components pointing to protected routes |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Embedding on every request in RAG | High latency, high OpenAI API cost | Embed at index time; only embed the query at request time | First 100 real user requests |
| Synchronous webhook processing | Stripe retries, duplicate processing | Queue webhook payload; process asynchronously | First high-traffic day (~10+ concurrent webhooks) |
| top_k too high in RAG retrieval | Inflated context, high token cost, diluted relevance | Start with k=3–5; measure; increase only if recall is demonstrably low | At scale with large document sets (1000+ chunks) |
| Multi-agent without token budget | Runaway API costs; agents loop indefinitely | Set hard `max_turns` and `max_tokens_per_run` limits; escalate to human after N failures | First time an agent hits a bug it cannot fix — can burn $100s in minutes |
| No Clerk middleware matcher configured | Every route is protected, blocking static assets | Configure matcher to exclude `/_next/`, `/public/`, `/favicon.ico` | During first end-to-end test of the deployed app |
| Auth session checked on every RSC render | Unnecessary round trips to Clerk | Cache session with `auth()` in layout, pass down as prop or use React context | At 500+ concurrent users |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing `privateMetadata` from Clerk `currentUser()` to client | Leaks internal user flags, roles, admin fields | Only serialize named fields needed by the client; never spread the full user object |
| Not verifying Stripe webhook signature | Spoofed webhooks can trigger subscription upgrades or fulfillment | Always call `stripe.webhooks.constructEvent(rawBody, signature, secret)` before processing |
| Using Stripe test keys in production CI | Accidental charges if keys rotate to live | Store keys in separate env: `STRIPE_SECRET_KEY_TEST` vs. `STRIPE_SECRET_KEY`; CI only uses test |
| Logging LLM prompts that contain user PII in RAG | Compliance risk (GDPR, CCPA) | Sanitize or anonymize PII before embedding; log prompt hashes not contents |
| Agent with write-tool access and no confirmation step | Agent autonomously modifies production data | Require human-in-the-loop confirmation for destructive or financial tool calls |
| Storing Clerk session token in localStorage | XSS can steal the session | Clerk uses HttpOnly cookies by default; never override with localStorage |
| Embedding user-supplied content without sanitization in RAG | Prompt injection via malicious documents | Sanitize ingested content; use a separate retrieval prompt that does not forward raw text to the final LLM call |

---

## "Looks Done But Isn't" Checklist

- [ ] **Auth skill:** Covers both Clerk (managed) and self-hosted (Better Auth) paths — verify both have working code examples with correct import paths for 2025.
- [ ] **Auth skill:** Documents middleware composition — verify there is a multi-middleware example (Clerk + existing middleware), not just standalone Clerk.
- [ ] **Stripe skill:** Webhook handler is idempotent — verify code example stores `event.id` in DB and checks before processing.
- [ ] **Stripe skill:** Covers subscription lifecycle events (not just `payment_intent.succeeded`) — verify `customer.subscription.updated`, `customer.subscription.deleted`, and `invoice.payment_failed` are documented.
- [ ] **RAG skill:** Covers retrieval evaluation — verify there is a section on measuring retrieval quality, not just pipeline assembly.
- [ ] **RAG skill:** Warns on chunking tradeoffs — verify chunk size guidance includes "too small" and "too large" consequences.
- [ ] **Agent skill:** Has token budget guidance — verify `max_turns` / `max_tokens` patterns are in the main file, not buried in references.
- [ ] **Agent skill:** Has handoff structure — verify there is a typed handoff schema example (what one agent passes to the next), not just a description.
- [ ] **Prompt skill:** Is model-tagged — verify every major technique specifies which model family it applies to.
- [ ] **All skills:** Have `last-verified:` frontmatter date — verify before marking the milestone complete.
- [ ] **All skills:** Are ≤ 500 lines in SKILL.md — verify with `wc -l` before marking complete (v1.1 constraint).
- [ ] **INDEX.md updated:** Verify all five new skills appear in INDEX.md with correct category, difficulty, and "when to use" description.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Auth skill recommends deprecated Auth.js v4 | MEDIUM | Audit all code examples for v4 import paths; replace with v5 or Better Auth equivalents; update frontmatter version tag |
| Stripe webhook duplicate processing in production | HIGH | Add `processed_stripe_events` table immediately; replay events from Stripe dashboard; audit fulfillment records for duplicates |
| RAG hallucinations from bad retrieval | MEDIUM | Add retrieval score threshold check; re-evaluate chunk size; switch to semantic chunking; add citation display to surface bad retrieval to users |
| Agent runaway token loop | HIGH | Add hard token budget limits; implement circuit breaker (fail after N retries); review and cap tool call depth |
| Skills exceed 500 lines | LOW | Extract overflowed content to `references/` subdirectory; update SKILL.md to link the reference file; test that SKILL.md still makes sense standalone |
| Cross-skill integration gap discovered post-release | MEDIUM | Add "Cross-skill integration" section to both affected skills; add cross-links in INDEX.md; publish a companion integration example in `assets/examples/` |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Auth.js deprecation — wrong library recommended | Auth skill authoring (outline phase) | Confirm frontmatter says "Better Auth for new projects"; no v4 imports in examples |
| Clerk middleware misconfiguration | Auth skill authoring (writing phase) | Confirm multi-middleware composition example exists in SKILL.md |
| Stripe webhook not idempotent | Stripe skill authoring (writing phase) | Confirm `event.id` deduplication code is in the main SKILL.md webhook section |
| RAG hallucination from bad retrieval | RAG skill authoring (outline phase) | Confirm evaluation section is in the SKILL.md outline before writing begins |
| Agent skill scope creep | Agent skill outlining (pre-writing) | Confirm outline has ≤ 6 top-level sections; references/ plan exists |
| Prompt skill model staleness | Prompt skill authoring (frontmatter first) | Confirm `last-verified-against:` field and model tags present before merge |
| Auth + Stripe integration gap | Integration review phase (after all 5 skills drafted) | Cross-reference audit: each skill pair mentions the other at the integration seam |
| Skills exceed 500 lines | Final QA phase | `wc -l` check on all five SKILL.md files; fail if any exceed 500 |
| INDEX.md not updated | Final QA phase | Confirm all five skills appear in INDEX.md with correct metadata |

---

## Sources

- Clerk error documentation: [auth() was called but Clerk can't detect clerkMiddleware()](https://clerk.com/docs/reference/nextjs/errors/auth-was-called)
- Clerk Next.js best practices: [Authentication Best Practices: Convex, Clerk and Next.js](https://stack.convex.dev/authentication-best-practices-convex-clerk-and-nextjs)
- Auth.js v5 migration: [Migrating to v5 — Auth.js](https://authjs.dev/getting-started/migrating-to-v5)
- Auth.js team joins Better Auth: [Auth.js is now part of Better Auth · Discussion #13252](https://github.com/nextauthjs/next-auth/discussions/13252)
- Stripe webhook idempotency: [Handling Payment Webhooks Reliably](https://medium.com/@sohail_saifii/handling-payment-webhooks-reliably-idempotency-retries-validation-69b762720bf5)
- Stripe webhook best practices: [Best practices I wish we knew when integrating Stripe webhooks](https://www.stigg.io/blog-posts/best-practices-i-wish-we-knew-when-integrating-stripe-webhooks)
- Stripe subscription webhook guide: [Using webhooks with subscriptions](https://docs.stripe.com/billing/subscriptions/webhooks)
- Stripe duplicate event handling: [Handling duplicate events from Stripe](https://www.duncanmackenzie.net/blog/handling-duplicate-stripe-events/)
- RAG retrieval pitfalls: [Advanced RAG Techniques — Neo4j](https://neo4j.com/blog/genai/advanced-rag-techniques/)
- RAG 2026 production guide: [Learn How to Build Reliable RAG Applications in 2026](https://dev.to/pavanbelagatti/learn-how-to-build-reliable-rag-applications-in-2026-1b7p)
- Multi-agent token runaway: [The Economics of Autonomy: Preventing Token Runaway in Agentic Loops](https://www.alpsagility.com/cost-control-agentic-systems)
- Multi-agent context window: [The Context Window Problem: Scaling Agents Beyond Token Limits](https://factory.ai/news/context-window-problem)
- Cognition's argument against multi-agents: [Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)
- Anthropic multi-agent research: [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- Prompt engineering mistakes: [Beyond "Prompt and Pray": 14 Prompt Engineering Mistakes](https://opendatascience.com/beyond-prompt-and-pray-14-prompt-engineering-mistakes-youre-probably-still-making/)
- Prompt engineering 2025 state: [Prompt Engineering in 2025: The Latest Best Practices](https://www.news.aakashg.com/p/prompt-engineering)
- Documentation staleness: [How to Write Technical Documentation in 2025](https://dev.to/auden/how-to-write-technical-documentation-in-2025-a-step-by-step-guide-1hh1)

---

*Pitfalls research for: v1.2 Skills Expansion — Auth, Stripe, RAG, Agent architecture, Prompt engineering*
*Researched: 2026-02-24*
