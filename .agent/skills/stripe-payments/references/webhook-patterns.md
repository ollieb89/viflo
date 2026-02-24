# Stripe Webhook Patterns

## Verified Webhook Handler

```typescript
// app/api/webhooks/stripe/route.ts
import Stripe from 'stripe';
import { headers } from 'next/headers';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: '2025-01-27.acacia' });

export async function POST(req: Request) {
  const body = await req.text(); // must be raw text, not parsed JSON
  const headersList = await headers();
  const sig = headersList.get('stripe-signature');

  if (!sig) return new Response('Missing stripe-signature header', { status: 400 });

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return new Response('Invalid signature', { status: 400 });
  }

  // Idempotency: @unique on stripeEventId is the true guard against concurrent delivery
  try {
    await db.stripeEvent.create({ data: { stripeEventId: event.id, type: event.type } });
  } catch (err: unknown) {
    if ((err as { code?: string }).code === 'P2002') {
      return new Response('Already processed', { status: 200 });
    }
    throw err;
  }

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session;
      const userId = session.metadata?.userId;
      if (userId && session.subscription) {
        await db.user.update({
          where: { id: userId },
          data: { stripeCustomerId: session.customer as string, stripeSubscriptionId: session.subscription as string, plan: 'pro' },
        });
      }
      break;
    }
    case 'invoice.payment_failed': {
      const invoice = event.data.object as Stripe.Invoice;
      const subscriptionId = invoice.subscription as string;
      await db.user.update({
        where: { stripeSubscriptionId: subscriptionId },
        data: { plan: 'past_due' }, // grant grace period; cron job downgrades after N days
      });
      break;
    }
    case 'customer.subscription.deleted': {
      const subscription = event.data.object as Stripe.Subscription;
      await db.user.update({
        where: { stripeSubscriptionId: subscription.id },
        data: { plan: 'free', stripeSubscriptionId: null },
      });
      break;
    }
  }

  return new Response('OK');
}
```

## Prisma Schema for Idempotency

```prisma
model StripeEvent {
  id            String   @id @default(cuid())
  stripeEventId String   @unique
  type          String
  createdAt     DateTime @default(now())
}
```

## Environment Variables

```bash
STRIPE_SECRET_KEY=sk_live_...        # or sk_test_... for testing
STRIPE_WEBHOOK_SECRET=whsec_...      # from Stripe dashboard > Webhooks
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_APP_URL=https://yourapp.com
```

## Testing Webhooks Locally

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward events to your local server
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Trigger a specific event
stripe trigger checkout.session.completed
```
