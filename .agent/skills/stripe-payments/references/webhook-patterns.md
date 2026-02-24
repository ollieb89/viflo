# Stripe Webhook Patterns

> Stripe SDK: stripe@20.3.1 — API version: 2026-01-28.clover — Next.js 15 (App Router)

## Verified Webhook Handler

Complete handler with raw body extraction, async headers (Next.js 15), and atomic idempotency SQL:

```typescript
// app/api/webhooks/stripe/route.ts
import Stripe from "stripe";
import { headers } from "next/headers";
import { pool } from "@/lib/db"; // your pg.Pool instance

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2026-01-28.clover", // stripe@20.3.1
});

export async function POST(req: Request) {
  const body = await req.text(); // MUST be first — raw bytes for HMAC verification
  const sig = (await headers()).get("stripe-signature"); // await headers() — Next.js 15 async API

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
    console.error("Webhook signature verification failed:", err);
    return new Response("Invalid signature", { status: 400 });
  }

  // Atomic idempotency — INSERT fails silently on duplicate; no race window
  const result = await pool.query(
    `INSERT INTO stripe_events (stripe_event_id, event_type)
     VALUES ($1, $2)
     ON CONFLICT (stripe_event_id) DO NOTHING`,
    [event.id, event.type],
  );
  if (result.rowCount === 0)
    return new Response("Already processed", { status: 200 });

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object as Stripe.Checkout.Session;
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
    case "customer.subscription.created":
    case "customer.subscription.updated": {
      const sub = event.data.object as Stripe.Subscription;
      await pool.query(
        `UPDATE users
         SET subscription_status = $1, stripe_subscription_id = $2
         WHERE stripe_customer_id = $3`,
        [sub.status, sub.id, sub.customer],
      );
      break;
    }
    case "customer.subscription.deleted": {
      const sub = event.data.object as Stripe.Subscription;
      await pool.query(
        `UPDATE users
         SET subscription_status = 'canceled', stripe_subscription_id = NULL
         WHERE stripe_subscription_id = $1`,
        [sub.id],
      );
      break;
    }
    case "invoice.payment_failed": {
      const invoice = event.data.object as Stripe.Invoice;
      await pool.query(
        `UPDATE users SET subscription_status = 'past_due' WHERE stripe_subscription_id = $1`,
        [invoice.subscription],
      );
      // Stripe Smart Retries handles recovery — no custom dunning needed.
      // Enable: Stripe Dashboard > Settings > Billing > Automatic collection > Smart Retries
      break;
    }
  }

  return new Response("OK");
}
```

## Idempotency Table Schema

```sql
CREATE TABLE IF NOT EXISTS stripe_events (
  stripe_event_id TEXT PRIMARY KEY,
  event_type      TEXT NOT NULL,
  processed_at    TIMESTAMPTZ DEFAULT NOW()
);
```

**Why atomic INSERT over SELECT-then-INSERT:** Two concurrent Stripe retries can both pass a `SELECT` existence check before either commits. The `INSERT ... ON CONFLICT (stripe_event_id) DO NOTHING` delegates the uniqueness guard to the database — only one concurrent INSERT wins, the other returns `rowCount === 0` and the handler short-circuits immediately.

## Environment Variables

```bash
STRIPE_SECRET_KEY=sk_live_...        # or sk_test_... for testing
STRIPE_WEBHOOK_SECRET=whsec_...      # from Stripe Dashboard > Webhooks > endpoint
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_APP_URL=https://yourapp.com
```

## Testing Webhooks Locally

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward Stripe events to your local server (handles tunneling + signing automatically)
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Fire a specific event without a real purchase
stripe trigger checkout.session.completed
```

> `stripe listen` issues a temporary webhook signing secret that is injected into the forwarded requests — you do not need to update `STRIPE_WEBHOOK_SECRET` locally, the CLI handles it.
