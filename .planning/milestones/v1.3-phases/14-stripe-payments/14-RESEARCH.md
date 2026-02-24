# Phase 14: Stripe Payments - Research

**Researched:** 2026-02-24
**Domain:** Stripe Node.js SDK, Stripe Checkout, Webhook handling, Subscription lifecycle, Next.js App Router
**Confidence:** HIGH

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Framework target**

- Next.js App Router throughout — all code examples use Route Handlers
- Stripe Checkout (hosted page) is the primary Quick Start path; Payment Element is noted as an alternative in a brief callout (not a full example)
- Webhook route handler shows `await req.text()` as the raw body extraction method — no variants, no alternatives shown inline
- Quick Start assumes Postgres is available upfront; skill states this dependency explicitly before the first code example

**Code example style**

- TypeScript only (no JS variants)
- Quick Start: minimal working snippets, under 30 lines total — no boilerplate beyond the essential Stripe calls
- Reference sections (webhook, subscriptions, idempotency): fuller examples with imports, error handling, and env variable usage shown
- Environment variables shown inline as `process.env.STRIPE_SECRET_KEY` — no config abstraction layer
- Stripe SDK initialized once in a Setup section (`const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: '...' })`); all later sections reference it without re-initializing

**Subscription lifecycle depth**

- Four events covered explicitly: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`
- Subscription status stored as Stripe's string directly (`active`, `canceled`, `past_due`, `trialing`, etc.) — no app-specific enum mapping
- Full schema with migrations shown: includes `stripe_customer_id`, `stripe_subscription_id`, `subscription_status`, `stripe_event_id` columns; migration SQL included in the skill
- Failed payment recovery: acknowledge `invoice.payment_failed`, point to Stripe Smart Retries as the recommended approach — no custom dunning implementation shown

**Gotchas tone and structure**

- Terse warning format: **Symptom** → **Cause** → **Fix** — three lines per pitfall, no narrative prose
- Exactly the 3 required pitfalls (raw body destruction, non-atomic idempotency, PCI scope creep) plus 1-2 bonus pitfalls if they cause genuine production pain (e.g. test/live key confusion, Stripe CLI required for local webhook testing)
- Raw body destruction fix: show `await req.text()` before any other body access; note that `req.json()` or bodyParser middleware destroys the raw body
- PCI scope creep fix: directive to use Checkout/Payment Element only, plus a link to Stripe's official PCI compliance documentation (not inline explanation of SAQ types)

**Specifics**

- The idempotency section must show `INSERT ... ON CONFLICT (stripe_event_id) DO NOTHING` in the **main body** — not a footnote or sidebar
- The webhook handler section must lead with `await req.text()` as the **first code example** — raw body extraction is the headline, not an afterthought
- Quick Start goal: developer accepts a one-time payment in under 15 minutes with fewer than 30 lines of code

### Claude's Discretion

- Exact section ordering within the skill (Quick Start → Webhooks → Idempotency → Subscriptions → Gotchas is a reasonable default)
- Which 1-2 bonus gotchas to include beyond the required three
- Specific Stripe API version string to use in the SDK init example
- Whether to include a "Local Development" callout showing Stripe CLI webhook forwarding

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>

## Phase Requirements

| ID        | Description                                                                                                        | Research Support                                                                                                                                                                     |
| --------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| STRIPE-01 | User can follow a Quick Start to accept a one-time payment via Stripe Checkout in under 15 minutes                 | Checkout Session with `mode: 'payment'`, `stripe.checkout.sessions.create()`, redirect to `session.url` — under 30 lines in Route Handler                                            |
| STRIPE-02 | Skill documents webhook handler with raw-body pattern (`await req.text()`) and atomic idempotency schema           | `req.text()` before any other body access + `constructEvent()` + `INSERT ... ON CONFLICT (stripe_event_id) DO NOTHING` SQL pattern                                                   |
| STRIPE-03 | Skill covers subscription lifecycle (create, update, cancel, status sync to database)                              | Four events: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed` — raw Stripe status strings stored directly |
| STRIPE-04 | Skill documents 3 named Gotchas with warning signs (raw body destruction, non-atomic idempotency, PCI scope creep) | Three required pitfalls fully documented; 2 bonus pitfalls (test/live key confusion, Stripe CLI for local testing) identified                                                        |
| STRIPE-05 | Skill covers Customer Portal integration and trial periods with proration handling                                 | `stripe.billingPortal.sessions.create()` API confirmed; `subscription_data.trial_period_days` for Checkout; proration behavior on plan changes confirmed                             |

</phase_requirements>

---

## Summary

This phase delivers a rewritten and substantially expanded `stripe-payments` SKILL.md. The existing SKILL.md in `.agent/skills/stripe-payments/SKILL.md` covers Checkout, Customer Portal, and failure modes at a high level but lacks the Quick Start entry point, explicit raw-body webhook handler, atomic SQL idempotency pattern, four-event subscription lifecycle, and Gotchas section in the terse format required by the phase success criteria. Two reference files (`references/webhook-patterns.md` and `references/subscription-patterns.md`) already exist with verified code patterns that can be pulled into the main skill body.

The Stripe Node.js SDK is currently at `v20.3.1` (npm, verified 2026-02-24). The current API version string is `2026-01-28.clover` (verified from official docs). The existing SKILL.md uses `2025-01-27.acacia` — this should be updated. The skill content is TypeScript-only (no JS variants), targeting Next.js App Router Route Handlers throughout.

The three mandatory pitfalls (raw body destruction, non-atomic idempotency, PCI scope creep) are all well-supported by existing reference files and official documentation. Two strong bonus pitfalls are identified: test/live key confusion (silent production incidents) and Stripe CLI being required for local webhook testing (not optional as developers often assume). The phase output is a developer-facing SKILL.md — not application code — so all verification is structural/content inspection, not runtime testing.

**Primary recommendation:** Rewrite SKILL.md to follow the Quick Start → Webhooks → Idempotency → Subscriptions → Customer Portal → Gotchas structure; pull verified code from existing reference files into the main body; update to `stripe` v20.x and API version `2026-01-28.clover`.

---

## Standard Stack

### Core

| Library        | Version | Purpose                                                        | Why Standard                              |
| -------------- | ------- | -------------------------------------------------------------- | ----------------------------------------- |
| `stripe` (npm) | 20.3.1  | Stripe Node.js SDK — sessions, webhooks, subscriptions, portal | Official SDK; maintained by Stripe; typed |
| Next.js        | 15.x    | App Router Route Handlers for all server-side Stripe API calls | Locked by CONTEXT.md                      |
| Postgres       | any     | Subscription status storage, idempotency table                 | Locked by CONTEXT.md (available upfront)  |

### Supporting

| Library        | Version    | Purpose                                                            | When to Use                                   |
| -------------- | ---------- | ------------------------------------------------------------------ | --------------------------------------------- |
| Stripe CLI     | latest     | Local webhook forwarding                                           | Required for local development — not optional |
| `next/headers` | Next.js 15 | Async `headers()` for reading `stripe-signature` in Route Handlers | Required in App Router webhook handler        |

### Alternatives Considered

| Instead of                              | Could Use                         | Tradeoff                                                                                                                                      |
| --------------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Stripe Checkout (hosted)                | Payment Element (custom UI)       | Payment Element: full UI control, more code, still SAQ A-EP; Checkout: zero frontend code, SAQ A — Checkout is locked choice                  |
| SQL `INSERT ... ON CONFLICT DO NOTHING` | Prisma `@unique` constraint check | Both enforce uniqueness; SQL is DB-agnostic and explicit; Prisma adds ORM dependency to idempotency logic — SQL is the CONTEXT.md requirement |

**Installation:**

```bash
npm install stripe
```

---

## Architecture Patterns

### Recommended Skill Structure

```
.agent/skills/stripe-payments/
├── SKILL.md                         # Primary — rewritten with Quick Start + all sections
└── references/
    ├── webhook-patterns.md          # EXISTS — full verified webhook handler + Prisma schema
    └── subscription-patterns.md    # EXISTS — lifecycle event handling + portal patterns
```

### Pattern 1: Quick Start — One-Time Payment via Checkout

**What:** Minimal Route Handler that creates a Checkout Session with `mode: 'payment'` and redirects to `session.url`. Under 30 lines.
**When to use:** Quick Start section — developer's first working integration in under 15 minutes.

```typescript
// Source: .agent/skills/stripe-payments/SKILL.md (to be written)
// app/api/checkout/route.ts
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2026-01-28.clover",
});

export async function POST(req: Request) {
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: "price_xxxx", quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/cancel`,
  });
  return Response.json({ url: session.url });
}
```

Client call: `const res = await fetch('/api/checkout', { method: 'POST' }); const { url } = await res.json(); window.location.href = url;`

Total lines including the client call: well under 30.

### Pattern 2: Webhook Handler — Raw Body First

**What:** Route Handler that calls `await req.text()` as the first operation, then `stripe.webhooks.constructEvent()` for signature verification.
**When to use:** All webhook endpoints. This is the headline pattern in the Webhooks section.

```typescript
// Source: .agent/skills/stripe-payments/references/webhook-patterns.md (existing, verified)
// app/api/webhooks/stripe/route.ts
import Stripe from "stripe";
import { headers } from "next/headers";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2026-01-28.clover",
});

export async function POST(req: Request) {
  const body = await req.text(); // MUST be first — req.json() destroys the raw body
  const headersList = await headers();
  const sig = headersList.get("stripe-signature");
  if (!sig)
    return new Response("Missing stripe-signature header", { status: 400 });

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!,
    );
  } catch (err) {
    return new Response("Invalid signature", { status: 400 });
  }
  // ... handle event
  return new Response("OK");
}
```

### Pattern 3: Atomic Idempotency via SQL

**What:** `INSERT ... ON CONFLICT (stripe_event_id) DO NOTHING` in the webhook handler body — not in the references, not in a footnote.
**When to use:** Every webhook handler that processes business side-effects (subscription creation, fulfillment, etc.)

```sql
-- Source: docs.stripe.com/webhooks + confirmed production pattern
-- Schema (run once)
CREATE TABLE stripe_events (
  stripe_event_id TEXT PRIMARY KEY,
  event_type      TEXT NOT NULL,
  processed_at    TIMESTAMPTZ DEFAULT NOW()
);

-- In the webhook handler (atomic — concurrent duplicate delivery is safe)
INSERT INTO stripe_events (stripe_event_id, event_type)
VALUES ($1, $2)
ON CONFLICT (stripe_event_id) DO NOTHING;

-- Returns 0 rows affected if already processed
-- Application should check affected rows and return 200 immediately if 0
```

### Pattern 4: Subscription Lifecycle — Four Critical Events

**What:** Handler switch covering `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, and `invoice.payment_failed`.
**When to use:** Subscription-based products where database plan state must stay in sync with Stripe.

```typescript
// Source: .agent/skills/stripe-payments/references/webhook-patterns.md (existing)
// Subscription status stored as Stripe's string directly — no enum mapping
switch (event.type) {
  case "customer.subscription.created":
  case "customer.subscription.updated": {
    const sub = event.data.object as Stripe.Subscription;
    await db.execute(
      "UPDATE users SET subscription_status = $1, stripe_subscription_id = $2 WHERE stripe_customer_id = $3",
      [sub.status, sub.id, sub.customer as string],
    );
    break;
  }
  case "customer.subscription.deleted": {
    const sub = event.data.object as Stripe.Subscription;
    await db.execute(
      "UPDATE users SET subscription_status = 'canceled', stripe_subscription_id = NULL WHERE stripe_customer_id = $1",
      [sub.customer as string],
    );
    break;
  }
  case "invoice.payment_failed": {
    const invoice = event.data.object as Stripe.Invoice;
    await db.execute(
      "UPDATE users SET subscription_status = 'past_due' WHERE stripe_customer_id = $1",
      [invoice.customer as string],
    );
    // Stripe Smart Retries handles recovery — no custom dunning needed
    break;
  }
}
```

### Pattern 5: Customer Portal Session

**What:** Route Handler creating a billing portal session for self-serve subscription management.
**When to use:** STRIPE-05 — Customer Portal integration requirement.

```typescript
// Source: docs.stripe.com/api/customer_portal/sessions/create (verified)
// app/api/billing-portal/route.ts
export async function POST(req: Request) {
  // ALWAYS authenticate first — never trust client-provided customerId
  // const session = await auth(); const customerId = await getStripeCustomerId(session.user.id);
  const { customerId } = await req.json(); // replace with server-side lookup in production

  const portalSession = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
  });
  return Response.json({ url: portalSession.url });
}
```

### Pattern 6: Trial Periods

**What:** `subscription_data.trial_period_days` on the Checkout Session for subscription mode.
**When to use:** STRIPE-05 — trial periods requirement.

```typescript
// Source: docs.stripe.com/payments/checkout/free-trials (verified)
const session = await stripe.checkout.sessions.create({
  mode: "subscription",
  line_items: [{ price: "price_xxxx", quantity: 1 }],
  subscription_data: {
    trial_period_days: 14,
  },
  // Collect payment method during trial to enable auto-charge at trial end
  // payment_method_collection: 'if_required'  // use this to allow trial without card
  success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
});
```

When the trial ends, Stripe fires `customer.subscription.trial_will_end` (3 days before) and then transitions the subscription to `active` (charging) or `canceled`/`paused` (if no payment method and `trial_settings.end_behavior.missing_payment_method` is set).

### Pattern 7: Database Schema (SQL, full migration)

```sql
-- Runs before any webhook handling — all four required columns
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS stripe_customer_id      TEXT UNIQUE,
  ADD COLUMN IF NOT EXISTS stripe_subscription_id  TEXT UNIQUE,
  ADD COLUMN IF NOT EXISTS subscription_status     TEXT DEFAULT 'free';
  -- stripe_event_id is on the stripe_events table, not users

-- Idempotency table
CREATE TABLE IF NOT EXISTS stripe_events (
  stripe_event_id TEXT PRIMARY KEY,
  event_type      TEXT NOT NULL,
  processed_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### Anti-Patterns to Avoid

- **Calling `req.json()` before `req.text()` in a webhook handler:** The raw body is consumed; `constructEvent()` will always throw `400`.
- **Check-then-insert for idempotency:** `SELECT` then `INSERT` has a race window. Two concurrent deliveries of the same event both pass the SELECT check and both insert, processing the event twice. Use `INSERT ... ON CONFLICT DO NOTHING` instead.
- **Storing a processed flag in application memory (Map, Set, Redis without TTL):** Memory is lost on restart; Redis without TTL leaks unboundedly. Postgres with `PRIMARY KEY` on `stripe_event_id` is durable and O(log n).
- **Trusting `success_url` query parameters as proof of payment:** Always verify `session.payment_status === 'paid'` server-side before granting access.
- **Calling Stripe API on every request to check subscription status:** Store status in the DB via webhooks; only call Stripe API for drift reconciliation.

---

## Don't Hand-Roll

| Problem                        | Don't Build                      | Use Instead                                               | Why                                                                                             |
| ------------------------------ | -------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Payment UI (card inputs)       | Custom HTML card form            | Stripe Checkout or Elements                               | Raw card data on your server = SAQ D (300+ requirements); Checkout = SAQ A (20 requirements)    |
| Webhook signature verification | HMAC comparison by hand          | `stripe.webhooks.constructEvent()`                        | Timing-safe comparison, replay window (5 min), event object parsing — all handled               |
| Idempotency logic              | Redis set / SELECT-then-INSERT   | `INSERT ... ON CONFLICT (stripe_event_id) DO NOTHING`     | Atomic; no race window; durable; free (already have Postgres)                                   |
| Subscription retry/dunning     | Custom payment retry scheduler   | Stripe Smart Retries                                      | AI-timed retries, configurable window (1 week – 2 months); 8 attempts in 2 weeks is the default |
| Customer self-service billing  | Custom plan management UI        | Stripe Customer Portal                                    | Pre-built: upgrades, downgrades, cancellation, invoice history, payment method updates          |
| Trial period enforcement       | Cron job checking trial end date | `subscription_data.trial_period_days` in Checkout Session | Stripe handles trial end, charging, and `past_due` transitions automatically                    |

**Key insight:** Stripe's hosted surfaces (Checkout, Customer Portal) move you from SAQ D to SAQ A — the difference between 300+ compliance controls and 20. Never implement custom payment UIs without this context.

---

## Common Pitfalls

### Pitfall 1: Raw Body Destruction (Required Gotcha)

**What goes wrong:** Webhook signature verification always fails with "No signatures found matching the expected signature for payload" even though the secret is correct.
**Why it happens:** `req.json()`, `req.formData()`, or Express `bodyParser` middleware consume the request body stream before `constructEvent()` can read it. The raw bytes that Stripe signed are gone.
**How to avoid:** Call `await req.text()` as the first line of the webhook Route Handler — before any other body access.
**Warning signs:** `stripe.webhooks.constructEvent()` throws consistently; Stripe dashboard shows all webhook deliveries as failed (400); error message mentions "payload".

### Pitfall 2: Non-Atomic Idempotency (Required Gotcha)

**What goes wrong:** The same event (e.g., `checkout.session.completed`) is processed twice — user gets charged twice or subscription is created twice.
**Why it happens:** Check-then-insert pattern (`SELECT` → if not exists → `INSERT`) has a race window. Stripe retries deliveries within milliseconds; two concurrent requests both pass the SELECT, then both INSERT and process.
**How to avoid:** Use `INSERT INTO stripe_events (stripe_event_id, event_type) VALUES ($1, $2) ON CONFLICT (stripe_event_id) DO NOTHING`. Check affected rows count — if 0, return 200 immediately.
**Warning signs:** Duplicate records in your DB; users emailing about being charged twice; duplicate Stripe Customer records.

### Pitfall 3: PCI Scope Creep (Required Gotcha)

**What goes wrong:** Building a custom payment form (HTML `<input>` for card number, expiry, CVV) puts raw card data on your server, escalating PCI scope from SAQ A to SAQ D.
**Why it happens:** Developers prototype with raw HTML forms before realizing Stripe tokenizes on their behalf. SAQ D has ~300 controls vs SAQ A's ~20.
**How to avoid:** Use Stripe Checkout (hosted redirect) or Payment Element (client-side tokenization, Stripe.js never leaves raw card data). See https://docs.stripe.com/security/guide for official scope guidance.
**Warning signs:** Your Route Handler receives raw card numbers, CVV, or expiry strings in request body.

### Pitfall 4: Test vs. Live Key Confusion (Bonus Gotcha)

**What goes wrong:** Charges appear in Stripe dashboard but users can't access paid features, or vice versa — or production traffic silently fails.
**Why it happens:** `STRIPE_SECRET_KEY` in production points to `sk_test_...` (test mode); webhooks come from live mode but the signing secret is from the test webhook endpoint (or vice versa).
**How to avoid:** `sk_test_` → test mode, `sk_live_` → live mode. Webhook signing secrets are per-endpoint (test endpoint secret ≠ live endpoint secret). Verify all three env vars in staging and production: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`.
**Warning signs:** `constructEvent()` fails in production only; charges show in test dashboard while app is "live"; Stripe CLI forwarding secret doesn't match deployed webhook secret.

### Pitfall 5: Webhook Testing Requires Stripe CLI (Bonus Gotcha)

**What goes wrong:** Developer runs `ngrok` or uses `localhost` URL in the Stripe dashboard, but events never arrive, or developer can't test specific event types without making real purchases.
**Why it happens:** Stripe dashboard webhooks require a publicly accessible HTTPS URL. `ngrok` adds complexity; `localhost` never works from Stripe's servers.
**How to avoid:** Install Stripe CLI (`brew install stripe/stripe-cli/stripe` or equivalent). Use `stripe listen --forward-to localhost:3000/api/webhooks/stripe` — it handles tunneling and signing automatically. Use `stripe trigger checkout.session.completed` to fire specific events without real purchases.
**Warning signs:** Webhook handler never receives events in local dev; developer testing by making real $0.01 charges.

---

## Code Examples

Verified patterns from official sources and existing reference files:

### SDK Initialization (Setup Section — referenced by all other sections)

```typescript
// Source: .agent/skills/stripe-payments/SKILL.md (existing, updated version)
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2026-01-28.clover", // current as of 2026-02-24
});
```

### Checkout Session — One-Time Payment (Quick Start)

```typescript
// Source: docs.stripe.com/payments/checkout + existing skill (pattern verified)
// app/api/checkout/route.ts
export async function POST() {
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: "price_xxxx", quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/cancel`,
  });
  return Response.json({ url: session.url });
}
```

### Checkout Session — Subscription with Trial

```typescript
// Source: docs.stripe.com/payments/checkout/free-trials (verified)
const session = await stripe.checkout.sessions.create({
  mode: "subscription",
  line_items: [{ price: "price_xxxx", quantity: 1 }],
  subscription_data: { trial_period_days: 14 },
  success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
  cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
});
```

### Webhook Handler — Full Pattern

```typescript
// Source: .agent/skills/stripe-payments/references/webhook-patterns.md (existing, verified)
import Stripe from "stripe";
import { headers } from "next/headers";

export async function POST(req: Request) {
  const body = await req.text(); // raw body — MUST be first
  const sig = (await headers()).get("stripe-signature");
  if (!sig) return new Response("Missing signature", { status: 400 });

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!,
    );
  } catch {
    return new Response("Invalid signature", { status: 400 });
  }

  // Atomic idempotency — returns early if already processed
  const result = await db.execute(
    "INSERT INTO stripe_events (stripe_event_id, event_type) VALUES ($1, $2) ON CONFLICT (stripe_event_id) DO NOTHING",
    [event.id, event.type],
  );
  if (result.rowCount === 0)
    return new Response("Already processed", { status: 200 });

  switch (
    event.type
    // ... cases
  ) {
  }
  return new Response("OK");
}
```

### Customer Portal Session

```typescript
// Source: docs.stripe.com/api/customer_portal/sessions/create (verified)
const portalSession = await stripe.billingPortal.sessions.create({
  customer: customerId, // from server-side DB lookup — never from request body
  return_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
});
return Response.json({ url: portalSession.url });
```

### Environment Variables

```bash
STRIPE_SECRET_KEY=sk_live_...               # sk_test_... for development
STRIPE_WEBHOOK_SECRET=whsec_...             # from Stripe dashboard > Webhooks
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_APP_URL=https://yourapp.com
```

### Stripe CLI Local Development

```bash
brew install stripe/stripe-cli/stripe       # macOS — see docs for Linux/Windows
stripe login
stripe listen --forward-to localhost:3000/api/webhooks/stripe
# In a second terminal:
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_failed
```

---

## State of the Art

| Old Approach                                           | Current Approach                        | When Changed                     | Impact                                                                                                    |
| ------------------------------------------------------ | --------------------------------------- | -------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `req.body` (Express bodyParser)                        | `await req.text()` (Web Fetch API)      | Next.js App Router (Next.js 13+) | Route Handlers use Web APIs — no `bodyParser` middleware exists; `req.text()` is the only correct pattern |
| API version `2025-01-27.acacia` (in existing SKILL.md) | `2026-01-28.clover`                     | January 2026                     | Existing skill is stale — needs update                                                                    |
| `stripe` npm v17.x (in existing SKILL.md)              | v20.3.1                                 | 2026                             | Existing skill version context is stale                                                                   |
| `await headers()` (sync in older Next.js)              | `await headers()` (async in Next.js 15) | Next.js 15                       | `headers()` is now async — must be awaited before `.get()`                                                |
| Manual dunning cron jobs                               | Stripe Smart Retries                    | Stripe Billing                   | AI-optimized retry timing; up to 8 retries in 2 weeks; no custom code needed                              |

**Deprecated/outdated in existing skill:**

- API version `2025-01-27.acacia`: replace with `2026-01-28.clover`
- `stripe` v17.x: replace with v20.x
- The existing SKILL.md has no Quick Start, no Gotchas section, and no idempotency section in the main body — these are the primary gaps

---

## Open Questions

1. **Proration on trial end**
   - What we know: When a trial ends and the subscription goes active, Stripe generates an invoice for the first full billing period — there is no proration (the trial itself is free)
   - What's unclear: The official free trials doc does not explicitly address proration behavior at trial-to-active transition; it does confirm that mid-trial plan changes in `billing_mode=flexible` generate a $0 invoice
   - Recommendation: State in the SKILL.md that trial-to-active generates the first full invoice (no proration) and that mid-cycle plan changes use `proration_behavior: 'create_prorations'` for upgrades and `'none'` for downgrades (this is already confirmed in `references/subscription-patterns.md`)

2. **Customer Portal configuration requirement**
   - What we know: The portal requires activation in the Stripe Dashboard before `billingPortal.sessions.create()` will succeed; the API endpoint is `POST /v1/billing_portal/sessions`
   - What's unclear: Whether the skill should note the dashboard setup step or treat it as an implicit prerequisite
   - Recommendation: Include a one-line note: "Enable the Customer Portal in Stripe Dashboard > Settings > Billing before calling this API"

3. **Stripe SDK v18+ breaking changes**
   - What we know: There is a documented migration guide for v18 (`stripe-node/wiki/Migration-guide-for-v18`); current version is v20.3.1
   - What's unclear: Whether any v18+ changes affect the patterns in the existing reference files (particularly the webhook handler using `headers()`)
   - Recommendation: The patterns in reference files use standard Web APIs (`req.text()`, `headers()`) rather than SDK internals — LOW risk. Use v20.x in all examples without documenting migration from v17.

---

## Sources

### Primary (HIGH confidence)

- `docs.stripe.com/api/versioning` — current API version `2026-01-28.clover` (fetched 2026-02-24)
- `docs.stripe.com/api/customer_portal/sessions/create` — `stripe.billingPortal.sessions.create()` API (fetched 2026-02-24)
- `docs.stripe.com/payments/checkout/free-trials` — `subscription_data.trial_period_days` (fetched 2026-02-24)
- `docs.stripe.com/billing/subscriptions/trials` — trial end behavior, `trial_settings.end_behavior.missing_payment_method` (fetched 2026-02-24)
- `.agent/skills/stripe-payments/references/webhook-patterns.md` — existing verified webhook handler + Prisma schema (read 2026-02-24)
- `.agent/skills/stripe-payments/references/subscription-patterns.md` — lifecycle event handling, plan changes, portal session (read 2026-02-24)
- npm registry (`npm show stripe version`) — v20.3.1 confirmed (2026-02-24)

### Secondary (MEDIUM confidence)

- `docs.stripe.com/billing/subscriptions/customer-portal` — portal overview, features list (fetched 2026-02-24)
- `docs.stripe.com/billing/revenue-recovery/smart-retries` — Smart Retries feature, 8 retries in 2 weeks default (via WebSearch, official source)
- WebSearch: "Stripe Node.js SDK npm version 2025" → v20.3.x confirmed via multiple sources

### Tertiary (LOW confidence)

- WebSearch: "Stripe Checkout one-time payment Next.js App Router 2025" — confirms Route Handler pattern; not directly verified against current docs

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — stripe v20.3.1 verified via npm, API version `2026-01-28.clover` verified via official docs
- Architecture patterns: HIGH — webhook handler and idempotency patterns verified in existing reference files; Customer Portal API verified in official docs
- Pitfalls: HIGH — raw body destruction and non-atomic idempotency are well-documented in existing skill; PCI scope confirmed via pci-compliance skill; test/live key confusion is a well-known production pattern; Stripe CLI requirement is official documentation

**Research date:** 2026-02-24
**Valid until:** 2026-03-26 (Stripe API versions change infrequently; SDK version may advance but patterns are stable)
