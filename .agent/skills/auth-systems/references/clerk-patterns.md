# Clerk Patterns

## Server-Side Auth (App Router)

```typescript
import { auth, currentUser } from '@clerk/nextjs/server';

export async function GET() {
  const { userId, orgId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });

  const user = await currentUser(); // full user object (extra network call — cache if needed)
  return Response.json({ userId, orgId, name: user?.firstName });
}
```

## Client-Side Auth

```typescript
'use client';
import { useAuth, useUser, useOrganization } from '@clerk/nextjs';

export function Dashboard() {
  const { userId, isLoaded } = useAuth();
  const { user } = useUser();
  const { organization } = useOrganization();

  if (!isLoaded) return null; // always guard the loading state
  if (!userId) return <SignIn />;

  return <div>Hello {user?.firstName} — org: {organization?.name ?? 'Personal'}</div>;
}
```

## Webhook Handler (sync Clerk events to your database)

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from 'svix';
import { headers } from 'next/headers';
import { WebhookEvent } from '@clerk/nextjs/server';

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET;
  if (!WEBHOOK_SECRET) throw new Error('CLERK_WEBHOOK_SECRET is not set');
  const headerPayload = await headers();
  const svix_id = headerPayload.get('svix-id');
  const svix_timestamp = headerPayload.get('svix-timestamp');
  const svix_signature = headerPayload.get('svix-signature');

  if (!svix_id || !svix_timestamp || !svix_signature) {
    return new Response('Missing svix headers', { status: 400 });
  }

  const body = await req.text();
  const wh = new Webhook(WEBHOOK_SECRET);

  let event: WebhookEvent;
  try {
    event = wh.verify(body, {
      'svix-id': svix_id,
      'svix-timestamp': svix_timestamp,
      'svix-signature': svix_signature,
    }) as WebhookEvent;
  } catch {
    return new Response('Invalid signature', { status: 400 });
  }

  // Idempotency: check svix-id before processing
  const existing = await db.webhookEvent.findUnique({ where: { svixId: svix_id } });
  if (existing) return new Response('Already processed', { status: 200 });

  await db.webhookEvent.create({ data: { svixId: svix_id } });

  if (event.type === 'user.created') {
    await db.user.create({
      data: {
        clerkId: event.data.id,
        email: event.data.email_addresses[0].email_address,
      },
    });
  }

  return new Response('OK');
}
```

## Environment Variables

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
CLERK_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```
