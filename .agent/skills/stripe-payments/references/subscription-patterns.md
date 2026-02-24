# Subscription Lifecycle Patterns

> Stripe SDK: stripe@20.3.1 — API version: 2026-01-28.clover — Next.js 15 (App Router)

## Database Schema

Add these columns to your users table — store Stripe's raw status strings directly:

```sql
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS stripe_customer_id      TEXT UNIQUE,
  ADD COLUMN IF NOT EXISTS stripe_subscription_id  TEXT UNIQUE,
  ADD COLUMN IF NOT EXISTS subscription_status     TEXT DEFAULT 'free';
```

## Subscription Status Reference

Store raw Stripe status strings — no app-specific enum mapping. Stripe owns the state machine.

| Stripe Status | Meaning                  | Typical Action                 |
| ------------- | ------------------------ | ------------------------------ |
| `active`      | Paid and current         | Full access                    |
| `trialing`    | In free trial            | Full access (trial)            |
| `past_due`    | Payment failed, retrying | Limited access + payment nudge |
| `canceled`    | Subscription ended       | Downgrade to free tier         |
| `incomplete`  | Checkout not completed   | No access                      |
| `paused`      | Paused by user or Stripe | No access                      |

## Four Subscription Lifecycle Events

All four critical events and their corresponding database updates:

```typescript
// Included in your webhook handler switch block
// (see references/webhook-patterns.md for the complete handler)

case 'customer.subscription.created':
case 'customer.subscription.updated': {
  // Handles initial subscription and all plan changes (upgrades, downgrades, trial conversions)
  const sub = event.data.object as Stripe.Subscription;
  await pool.query(
    `UPDATE users
     SET subscription_status = $1, stripe_subscription_id = $2
     WHERE stripe_customer_id = $3`,
    [sub.status, sub.id, sub.customer], // sub.status is the raw Stripe string: 'active', 'trialing', etc.
  );
  break;
}

case 'customer.subscription.deleted': {
  // Subscription permanently ended (canceled after all retries, or manually canceled)
  const sub = event.data.object as Stripe.Subscription;
  await pool.query(
    `UPDATE users
     SET subscription_status = 'canceled', stripe_subscription_id = NULL
     WHERE stripe_subscription_id = $1`,
    [sub.id],
  );
  break;
}

case 'invoice.payment_failed': {
  // Payment attempt failed — Stripe Smart Retries will attempt recovery automatically
  const invoice = event.data.object as Stripe.Invoice;
  await pool.query(
    `UPDATE users SET subscription_status = 'past_due' WHERE stripe_subscription_id = $1`,
    [invoice.subscription],
  );
  // Stripe Smart Retries handles recovery — no custom dunning needed.
  // Enable: Stripe Dashboard > Settings > Billing > Automatic collection > Smart Retries
  // If all retries fail, Stripe fires customer.subscription.deleted (handled above).
  break;
}
```

**Event summary table:**

| Event                           | DB Update                                                                 |
| ------------------------------- | ------------------------------------------------------------------------- |
| `customer.subscription.created` | SET `subscription_status = sub.status`, `stripe_subscription_id = sub.id` |
| `customer.subscription.updated` | SET `subscription_status = sub.status`, `stripe_subscription_id = sub.id` |
| `customer.subscription.deleted` | SET `subscription_status = 'canceled'`, `stripe_subscription_id = NULL`   |
| `invoice.payment_failed`        | SET `subscription_status = 'past_due'`                                    |

## Checking Subscription Status Server-Side

Always read from your database — webhooks keep it in sync. Call the Stripe API only for reconciliation:

```typescript
// DB-first (use this 99% of the time)
async function getUserSubscriptionStatus(userId: string) {
  const result = await pool.query(
    "SELECT subscription_status FROM users WHERE id = $1",
    [userId],
  );
  return result.rows[0]?.subscription_status ?? "free";
}

// Stripe API drift check — for reconciliation jobs only, not per-request
async function verifyStatusFromStripe(stripeSubscriptionId: string) {
  const subscription =
    await stripe.subscriptions.retrieve(stripeSubscriptionId);
  return subscription.status; // raw Stripe string
}
```

## Customer Portal

Lets users manage their own subscriptions (upgrades, downgrades, cancellations, invoice history) without custom UI.

**Enable first:** Stripe Dashboard > Settings > Billing > Customer portal — configure allowed actions before calling this API. The portal will not work until it is enabled in the Dashboard.

```typescript
// app/api/billing-portal/route.ts
import { stripe } from "@/lib/stripe";
import { pool } from "@/lib/db";
import { auth } from "@/lib/auth"; // your auth helper

export async function POST(req: Request) {
  const session = await auth();
  if (!session) return new Response("Unauthorized", { status: 401 });

  // Always look up customerId from your database using the authenticated user's ID
  // — never trust client-provided customerId
  const result = await pool.query(
    "SELECT stripe_customer_id FROM users WHERE id = $1",
    [session.user.id],
  );
  const customerId = result.rows[0]?.stripe_customer_id;
  if (!customerId)
    return new Response("No Stripe customer found", { status: 404 });

  const portalSession = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
  });

  return Response.json({ url: portalSession.url });
}
```

**Client redirect:** `window.location.href = url` — same pattern as Checkout.

## Trial Periods

Add `subscription_data.trial_period_days` to a subscription-mode Checkout Session:

```typescript
const session = await stripe.checkout.sessions.create({
  mode: "subscription",
  line_items: [{ price: priceId, quantity: 1 }],
  success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
  cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
  metadata: { userId },
  subscription_data: {
    trial_period_days: 14,
    trial_settings: {
      end_behavior: { missing_payment_method: "cancel" }, // or 'pause'
    },
  },
  payment_method_collection: "if_required", // no card required to start the trial
});
```

**Trial lifecycle events:**

- `customer.subscription.trial_will_end` — fires 3 days before trial ends; send a reminder email
- When trial ends, Stripe transitions the subscription to `active` (if card on file) or `past_due`/`canceled` based on `trial_settings.end_behavior.missing_payment_method`
- The status change flows through `customer.subscription.updated` — your existing handler covers it automatically

## Mid-Cycle Plan Changes (Upgrade/Downgrade)

```typescript
// Upgrade: immediate proration — customer sees prorated charge now
await stripe.subscriptions.update(subscriptionId, {
  items: [{ id: currentItemId, price: newPriceId }],
  proration_behavior: "create_prorations",
});

// Downgrade: apply at end of billing period — avoids confusing immediate invoice
await stripe.subscriptions.update(subscriptionId, {
  items: [{ id: currentItemId, price: newPriceId }],
  proration_behavior: "none",
  billing_cycle_anchor: "unchanged", // don't reset billing date
});
```

Both fire `customer.subscription.updated` — your webhook handler updates `subscription_status` automatically.
