# Subscription Lifecycle Patterns

## Subscription Status Mapping

Map Stripe subscription statuses to your internal plan states:

| Stripe Status | Your Plan State | Action |
|---|---|---|
| `active` | pro | Full access |
| `trialing` | pro | Full access (trial) |
| `past_due` | past_due | Limited access + payment nudge |
| `canceled` | free | Downgrade immediately |
| `incomplete` | free | Checkout not completed |
| `paused` | paused | No access (Stripe feature) |

## Handling Plan Changes (Upgrade/Downgrade)

```typescript
// Upgrade: switch to higher price immediately with proration
await stripe.subscriptions.update(subscriptionId, {
  items: [{ id: currentItemId, price: newPriceId }],
  proration_behavior: 'create_prorations', // customer sees prorated charge immediately
});

// Downgrade: apply at end of billing period to avoid immediate proration confusion
await stripe.subscriptions.update(subscriptionId, {
  items: [{ id: currentItemId, price: newPriceId }],
  proration_behavior: 'none',
  billing_cycle_anchor: 'unchanged', // don't reset billing date
});
```

## Checking Active Subscription Server-Side

```typescript
// Never trust the client — always verify from Stripe or your DB
async function getUserPlan(userId: string) {
  const user = await db.user.findUnique({ where: { id: userId }, select: { stripeSubscriptionId: true } });
  if (!user?.stripeSubscriptionId) return 'free';

  const subscription = await stripe.subscriptions.retrieve(user.stripeSubscriptionId);
  return subscription.status === 'active' || subscription.status === 'trialing' ? 'pro' : 'free';
}
```

## Grace Period for Failed Payments

```typescript
// cron job or scheduled function — runs daily
async function downgradePastDueUsers() {
  const gracePeriodDays = 3;
  const cutoff = new Date(Date.now() - gracePeriodDays * 24 * 60 * 60 * 1000);

  const pastDueUsers = await db.user.findMany({
    where: { plan: 'past_due', updatedAt: { lt: cutoff } },
  });

  for (const user of pastDueUsers) {
    await db.user.update({ where: { id: user.id }, data: { plan: 'free' } });
    // send email: "Your subscription has ended"
  }
}
```
