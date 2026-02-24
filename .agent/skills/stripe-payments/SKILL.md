---
name: stripe-payments
description: Use when implementing payments, subscriptions, or billing in Next.js App Router applications. Covers Stripe Checkout (hosted page) for one-time payments and subscriptions, raw-body webhook handling with atomic idempotency, subscription lifecycle (four critical events), Customer Portal for self-serve billing management, trial periods, and Gotchas (raw body destruction, non-atomic idempotency, PCI scope creep, key confusion, Stripe CLI).
---

# Stripe Payments

> See `references/webhook-patterns.md` for complete webhook handler with pg.Pool raw SQL and atomic idempotency.
> See `references/subscription-patterns.md` for subscription lifecycle, plan changes, and portal patterns.

## Setup

Install the Stripe SDK once:

```bash
npm install stripe
```

Initialize the Stripe client once in a shared module — all route handlers import from here, never re-initialize:

```typescript
// lib/stripe.ts
import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2026-01-28.clover',
});
```

**Environment variables** (all four required):

```bash
STRIPE_SECRET_KEY=sk_live_...               # sk_test_... in development
STRIPE_WEBHOOK_SECRET=whsec_...             # from Stripe Dashboard > Webhooks > endpoint
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_APP_URL=https://yourapp.com
```

## Quick Start — Accept a One-Time Payment

**Prerequisites:** Postgres database (needed for webhook idempotency table — shown in Webhooks section).

**Step 1 — Server: create a Checkout Session**

```typescript
// app/api/checkout/route.ts
import { stripe } from '@/lib/stripe';

export async function POST(req: Request) {
  const { priceId, userId } = await req.json();

  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    metadata: { userId },
  });

  return Response.json({ url: session.url });
}
```

**Step 2 — Client: redirect to Stripe's hosted page**

```typescript
const res = await fetch('/api/checkout', {
  method: 'POST',
  body: JSON.stringify({ priceId, userId }),
});
const { url } = await res.json();
window.location.href = url;
```

> **Prefer Checkout over Payment Element for most use cases.** Checkout = SAQ A (~20 controls). Payment Element = SAQ A-EP (~60 controls). Only drop down to Payment Element when you need a fully custom payment UI embedded in your page.

## Webhooks

Webhook handlers have one rule: call `await req.text()` before anything else.

Parsing the body with `req.json()`, `req.formData()`, or any middleware (e.g., Express bodyParser) consumes the stream — `constructEvent()` needs the raw bytes to verify the HMAC signature.

**Full webhook handler with raw body extraction and atomic idempotency:**

```typescript
// app/api/webhooks/stripe/route.ts
import { stripe } from '@/lib/stripe';
import { headers } from 'next/headers';
import { pool } from '@/lib/db'; // your pg.Pool instance

export async function POST(req: Request) {
  const body = await req.text(); // MUST be first — raw bytes for HMAC verification
  const sig = (await headers()).get('stripe-signature');

  if (!sig) return new Response('Missing stripe-signature header', { status: 400 });

  let event: import('stripe').Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return new Response('Invalid signature', { status: 400 });
  }

  // Atomic idempotency — INSERT fails silently if already processed
  const result = await pool.query(
    `INSERT INTO stripe_events (stripe_event_id, event_type)
     VALUES ($1, $2)
     ON CONFLICT (stripe_event_id) DO NOTHING`,
    [event.id, event.type],
  );
  if (result.rowCount === 0) return new Response('Already processed', { status: 200 });

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as import('stripe').Stripe.Checkout.Session;
      const userId = session.metadata?.userId;
      if (userId && session.subscription) {
        await pool.query(
          `UPDATE users
           SET stripe_customer_id = $1, stripe_subscription_id = $2, subscription_status = 'active'
           WHERE id = $3`,
          [session.customer, session.subscription, userId],
        );
      }
      break;
    }
    case 'customer.subscription.created':
    case 'customer.subscription.updated': {
      const sub = event.data.object as import('stripe').Stripe.Subscription;
      await pool.query(
        `UPDATE users
         SET subscription_status = $1, stripe_subscription_id = $2
         WHERE stripe_customer_id = $3`,
        [sub.status, sub.id, sub.customer],
      );
      break;
    }
    case 'customer.subscription.deleted': {
      const sub = event.data.object as import('stripe').Stripe.Subscription;
      await pool.query(
        `UPDATE users
         SET subscription_status = 'canceled', stripe_subscription_id = NULL
         WHERE stripe_subscription_id = $1`,
        [sub.id],
      );
      break;
    }
    case 'invoice.payment_failed': {
      const invoice = event.data.object as import('stripe').Stripe.Invoice;
      await pool.query(
        `UPDATE users SET subscription_status = 'past_due' WHERE stripe_subscription_id = $1`,
        [invoice.subscription],
      );
      // Point to Stripe Smart Retries — no custom dunning needed.
      // Enable: Stripe Dashboard > Settings > Billing > Automatic collection > Smart Retries
      break;
    }
  }

  return new Response('OK');
}
```

**Idempotency table schema:**

```sql
CREATE TABLE IF NOT EXISTS stripe_events (
  stripe_event_id TEXT PRIMARY KEY,
  event_type      TEXT NOT NULL,
  processed_at    TIMESTAMPTZ DEFAULT NOW()
);
```

**Local development — test webhooks without real purchases:**

```bash
# Forward Stripe events to your local server (handles tunneling + signing)
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Fire a specific event without a real purchase
stripe trigger checkout.session.completed
```

## Subscription Lifecycle

**Database schema** — add these columns to your users table:

```sql
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS stripe_customer_id     TEXT UNIQUE,
  ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT UNIQUE,
  ADD COLUMN IF NOT EXISTS subscription_status    TEXT DEFAULT 'free';
```

Store Stripe's status strings directly — no app-specific enum mapping. The four critical events are shown in the webhook handler above. Summary of update logic:

| Event | DB Update |
|---|---|
| `customer.subscription.created` | SET `subscription_status = sub.status`, `stripe_subscription_id = sub.id` |
| `customer.subscription.updated` | SET `subscription_status = sub.status`, `stripe_subscription_id = sub.id` |
| `customer.subscription.deleted` | SET `subscription_status = 'canceled'`, `stripe_subscription_id = NULL` |
| `invoice.payment_failed` | SET `subscription_status = 'past_due'` |

**Failed payment recovery:** Handle `invoice.payment_failed` by marking users `past_due`, then point to Stripe Smart Retries (Stripe Dashboard > Settings > Billing > Automatic collection). No custom dunning needed — Stripe retries on an intelligent schedule and transitions the subscription to `canceled` if all retries fail.

**Create a subscription Checkout Session:**

```typescript
// app/api/checkout/route.ts
export async function POST(req: Request) {
  const { priceId, userId } = await req.json();

  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    metadata: { userId },
    allow_promotion_codes: true,
    payment_settings: { save_default_payment_method: 'on_subscription' },
  });

  return Response.json({ url: session.url });
}
```

**Check subscription status server-side** — always read from your DB; call Stripe API only for reconciliation:

```typescript
async function getUserSubscriptionStatus(userId: string) {
  const result = await pool.query(
    'SELECT subscription_status FROM users WHERE id = $1',
    [userId],
  );
  return result.rows[0]?.subscription_status ?? 'free';
}
```

## Customer Portal

Lets users manage their own subscriptions (upgrades, downgrades, cancellations, invoice history) without custom UI.

**Enable first:** Stripe Dashboard > Settings > Billing > Customer portal — configure what actions users can take before calling this API.

```typescript
// app/api/billing-portal/route.ts
import { stripe } from '@/lib/stripe';
import { pool } from '@/lib/db';
import { auth } from '@/lib/auth'; // your auth helper

export async function POST(req: Request) {
  const session = await auth();
  if (!session) return new Response('Unauthorized', { status: 401 });

  // Always look up customerId from your database using the authenticated user's ID
  // — never trust client-provided customerId
  const result = await pool.query(
    'SELECT stripe_customer_id FROM users WHERE id = $1',
    [session.user.id],
  );
  const customerId = result.rows[0]?.stripe_customer_id;
  if (!customerId) return new Response('No Stripe customer found', { status: 404 });

  const portalSession = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
  });

  return Response.json({ url: portalSession.url });
}
```

**Client:** `window.location.href = url` — same redirect pattern as Checkout.

## Trial Periods

Add `subscription_data.trial_period_days` to a subscription-mode Checkout Session:

```typescript
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  line_items: [{ price: priceId, quantity: 1 }],
  success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
  cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
  metadata: { userId },
  subscription_data: {
    trial_period_days: 14,
    trial_settings: {
      end_behavior: { missing_payment_method: 'cancel' }, // or 'pause'
    },
  },
  payment_method_collection: 'if_required', // no card required to start trial
});
```

When the trial ends, Stripe fires `customer.subscription.trial_will_end` (3 days before), then transitions to `active` (charges card) or `past_due`/`canceled` based on `trial_settings.end_behavior.missing_payment_method`. Your subscription webhook handler already covers this — the subscription status update flows through `customer.subscription.updated`.

**Mid-cycle plan changes:**

```typescript
// Upgrade: immediate proration — customer sees prorated charge now
await stripe.subscriptions.update(subscriptionId, {
  items: [{ id: currentItemId, price: newPriceId }],
  proration_behavior: 'create_prorations',
});

// Downgrade: apply at end of billing period — avoids confusing immediate invoice
await stripe.subscriptions.update(subscriptionId, {
  items: [{ id: currentItemId, price: newPriceId }],
  proration_behavior: 'none',
  billing_cycle_anchor: 'unchanged',
});
```

## Gotchas

**Symptom → Cause → Fix format. Three lines per pitfall.**

---

**Gotcha 1: Raw Body Destruction**
Symptom: `constructEvent()` always throws "No signatures found matching the expected signature for payload" even with the correct webhook secret.
Cause: `req.json()`, `req.formData()`, or Express `bodyParser` consumed the request stream before `constructEvent()` reads it — the raw bytes are gone.
Fix: `await req.text()` must be the absolute first line of the webhook handler — before any other body access, imports, or middleware.

---

**Gotcha 2: Non-Atomic Idempotency**
Symptom: Same event processed twice — duplicate charges, duplicate subscription records, users billed twice.
Cause: `SELECT` → if-not-exists → `INSERT` has a race window; two concurrent Stripe retries both pass the SELECT check, then both INSERT and both process the event.
Fix: `INSERT INTO stripe_events ... ON CONFLICT (stripe_event_id) DO NOTHING`; check `result.rowCount === 0` and return 200 immediately if already processed — the DB constraint is the true guard.

---

**Gotcha 3: PCI Scope Creep**
Symptom: Compliance audit flags raw card numbers, CVV, or expiry appearing in server request bodies or logs.
Cause: Custom HTML payment form (`<input>` fields for card data) passes raw card data through your server — SAQ D (300+ controls, annual audit).
Fix: Use Stripe Checkout or Payment Element only — card data never touches your server. See https://docs.stripe.com/security/guide. Checkout = SAQ A (~20 controls). Payment Element = SAQ A-EP (~60 controls).

---

**Gotcha 4: Test vs. Live Key Confusion**
Symptom: Charges appear in Stripe test dashboard while the app is live; `constructEvent()` fails in production only.
Cause: `STRIPE_SECRET_KEY=sk_test_...` deployed to production, or the webhook signing secret from a test endpoint (`whsec_test_...`) used with a live webhook endpoint.
Fix: `sk_test_` = test mode, `sk_live_` = live mode. Webhook signing secrets are per-endpoint — test and live endpoints have different `whsec_` values. Verify all four env vars before go-live.

---

**Gotcha 5: Stripe CLI Required for Local Webhook Testing**
Symptom: Webhook handler never receives events in local development; developer is making real purchases to test.
Cause: `localhost` is unreachable from Stripe's servers; ngrok adds complexity and breaks signing secrets on each tunnel restart.
Fix: `stripe listen --forward-to localhost:3000/api/webhooks/stripe` — handles tunneling and signing automatically. `stripe trigger checkout.session.completed` fires specific events without real purchases.

---

## Version Context

| Library | Version | Notes |
|---|---|---|
| stripe (npm) | 20.3.1 | Official Node.js SDK |
| Next.js | 15.x | App Router Route Handlers; `await headers()` is async in Next.js 15 |
| Stripe API version | 2026-01-28.clover | Current as of 2026-02-24; set in `new Stripe()` constructor |
