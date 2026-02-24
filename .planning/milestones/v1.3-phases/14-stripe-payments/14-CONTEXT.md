# Phase 14: Stripe Payments - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

A developer-facing SKILL.md that teaches how to accept one-time payments via Stripe Checkout, handle webhooks with raw body + idempotency, and sync subscription lifecycle to a Postgres database — without introducing PCI scope or webhook processing bugs. Creating the interactive Payment Element UI, SCA/3DS handling, and dunning systems are outside this phase.

</domain>

<decisions>
## Implementation Decisions

### Framework target

- Next.js App Router throughout — all code examples use Route Handlers
- Stripe Checkout (hosted page) is the primary Quick Start path; Payment Element is noted as an alternative in a brief callout (not a full example)
- Webhook route handler shows `await req.text()` as the raw body extraction method — no variants, no alternatives shown inline
- Quick Start assumes Postgres is available upfront; skill states this dependency explicitly before the first code example

### Code example style

- TypeScript only (no JS variants)
- Quick Start: minimal working snippets, under 30 lines total — no boilerplate beyond the essential Stripe calls
- Reference sections (webhook, subscriptions, idempotency): fuller examples with imports, error handling, and env variable usage shown
- Environment variables shown inline as `process.env.STRIPE_SECRET_KEY` — no config abstraction layer
- Stripe SDK initialized once in a Setup section (`const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: '...' })`); all later sections reference it without re-initializing

### Subscription lifecycle depth

- Four events covered explicitly: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`
- Subscription status stored as Stripe's string directly (`active`, `canceled`, `past_due`, `trialing`, etc.) — no app-specific enum mapping
- Full schema with migrations shown: includes `stripe_customer_id`, `stripe_subscription_id`, `subscription_status`, `stripe_event_id` columns; migration SQL included in the skill
- Failed payment recovery: acknowledge `invoice.payment_failed`, point to Stripe Smart Retries as the recommended approach — no custom dunning implementation shown

### Gotchas tone & structure

- Terse warning format: **Symptom** → **Cause** → **Fix** — three lines per pitfall, no narrative prose
- Exactly the 3 required pitfalls (raw body destruction, non-atomic idempotency, PCI scope creep) plus 1-2 bonus pitfalls if they cause genuine production pain (e.g. test/live key confusion, Stripe CLI required for local webhook testing)
- Raw body destruction fix: show `await req.text()` before any other body access; note that `req.json()` or bodyParser middleware destroys the raw body
- PCI scope creep fix: directive to use Checkout/Payment Element only, plus a link to Stripe's official PCI compliance documentation (not inline explanation of SAQ types)

### Claude's Discretion

- Exact section ordering within the skill (Quick Start → Webhooks → Idempotency → Subscriptions → Gotchas is a reasonable default)
- Which 1-2 bonus gotchas to include beyond the required three
- Specific Stripe API version string to use in the SDK init example
- Whether to include a "Local Development" callout showing Stripe CLI webhook forwarding

</decisions>

<specifics>
## Specific Ideas

- The idempotency section must show `INSERT ... ON CONFLICT (stripe_event_id) DO NOTHING` in the **main body** — not a footnote or sidebar
- The webhook handler section must lead with `await req.text()` as the **first code example** — raw body extraction is the headline, not an afterthought
- Quick Start goal: developer accepts a one-time payment in under 15 minutes with fewer than 30 lines of code

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

_Phase: 14-stripe-payments_
_Context gathered: 2026-02-24_
