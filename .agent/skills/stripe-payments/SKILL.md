---
name: stripe-payments
description: Use when implementing payments, subscriptions, or billing in web applications. Covers Stripe Checkout (hosted), Stripe Elements (custom UI), Payment Intents, subscription lifecycle, webhook handling, and production edge cases including duplicate delivery, mid-cycle plan changes, and payment failure recovery.
---

# Stripe Payments

> See `references/webhook-patterns.md` for verified webhook handling and idempotency patterns. See `references/subscription-patterns.md` for subscription lifecycle, plan changes, and billing portal.

## Decision Matrix

**Default recommendation:** Use Stripe Checkout for most new projects. Only drop down to Elements or Payment Intents when you have hard UI customisation requirements.

| Situation | Choice | Why |
|---|---|---|
| New project, standard checkout flow | Stripe Checkout (hosted) | Zero frontend code, PCI handled by Stripe, fastest to ship |
| Need custom payment UI (match your design system) | Stripe Elements | Full UI control, Stripe handles tokenisation and PCI scope |
| Complex flows (split payments, setup-then-charge) | Payment Intents API | Full control over payment lifecycle, supports deferred capture |
| Subscription with free trial | Stripe Checkout + `trial_period_days` | Built-in trial support, no custom logic |
| Usage-based billing | Stripe Meters + Subscriptions | Native metering API, no external tracking needed |
| Self-serve plan changes | Customer Portal | Pre-built UI for upgrades, downgrades, cancellation |

## Implementation Patterns

**Checkout Session (server-side — most common pattern):**

```typescript
// app/api/checkout/route.ts
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: '2025-01-27.acacia' });

export async function POST(req: Request) {
  const { priceId, userId } = await req.json();

  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    metadata: { userId }, // pass through to webhook
    allow_promotion_codes: true,
  });

  return Response.json({ url: session.url });
}
```

**Customer Portal (self-serve billing management):**

```typescript
// app/api/billing-portal/route.ts
export async function POST(req: Request) {
  // Authenticate first — never trust client-provided customerId
  // const session = await auth(); if (!session) return new Response('Unauthorized', { status: 401 });
  // const user = await db.user.findUnique({ where: { id: session.user.id } });
  // Use user.stripeCustomerId, not a value from the request body
  const { customerId } = await req.json();

  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
  });

  return Response.json({ url: session.url });
}
```

See `references/webhook-patterns.md` for webhook verification and `references/subscription-patterns.md` for subscription lifecycle handling.

## Failure Modes & Edge Cases

| Scenario | What Happens | How to Handle |
|---|---|---|
| Webhook duplicate delivery | Same event processed twice; user charged twice or plan set twice | Store `stripeEventId` and skip if already processed (see `references/webhook-patterns.md`) |
| `invoice.payment_failed` on subscription renewal | Subscription enters `past_due`, user loses access | Listen for event, email user, downgrade access after grace period (e.g., 3 days) |
| Plan upgrade mid-cycle | Proration creates confusing invoice line items | Set `proration_behavior: 'create_prorations'` and surface prorated amount in UI before confirming |
| Customer switches back to free tier | Subscription cancelled but Stripe Customer record remains | Never delete the Customer; set internal `plan = free` on your side, keep Stripe Customer for future reactivation |
| Checkout session expires (30 min timeout) | User returns to `success_url` with expired session | Check `session.payment_status === 'paid'` before granting access; don't rely on URL alone |
| Webhook signature verification fails | Attack or misconfigured secret | Return 400 (not 500) so Stripe stops retrying; check test vs. live webhook secret mismatch |
| Trial ends, no payment method on file | Subscription immediately cancels at trial end | Set `payment_settings.save_default_payment_method: 'on_subscription'` during Checkout |

## Version Context

| Library | Last Verified | Notes |
|---|---|---|
| `stripe` (npm) | 17.x | `apiVersion` must match your Stripe dashboard version to avoid breaking changes |
| Stripe API | `2025-01-27.acacia` | Set explicitly in constructor; default version may lag behind features |
| Next.js | 15.x | Route Handlers (`app/api/`) used; Pages Router uses `pages/api/` pattern instead |
