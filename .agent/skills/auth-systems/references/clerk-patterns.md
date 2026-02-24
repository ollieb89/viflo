# Clerk Patterns

> Full Clerk implementation reference for Next.js App Router. See `SKILL.md` for quick start and side-by-side Better Auth comparison.

## Version Context

| Library | Last Verified | Notes |
|---|---|---|
| `@clerk/nextjs` | 6.x | `clerkMiddleware` replaces `authMiddleware` (removed in 6.x) |
| `svix` | latest | Required for Clerk webhook signature verification |
| Next.js | 15.2.3+ | Required — patches CVE-2025-29927 middleware bypass |

---

## Environment Variables

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
CLERK_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

---

## Middleware (Protected Routes)

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isPublicRoute = createRouteMatcher([
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
]);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect(); // redirects to sign-in if unauthenticated
  }
});

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
};
```

> **Deprecated:** `authMiddleware` was removed in `@clerk/nextjs` 6.x. Always use `clerkMiddleware` + `createRouteMatcher`.

---

## Session Access

### Server Component

```typescript
import { auth, currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const { userId } = await auth();     // reads from JWT — no network call
  if (!userId) redirect('/sign-in');

  // currentUser() makes a network call to Clerk API — use only for display data
  // const user = await currentUser();
  return <Dashboard userId={userId} />;
}
```

> Prefer `auth()` over `currentUser()` for access control. `auth()` reads from the signed JWT (no network). `currentUser()` makes an API call to Clerk — reserve for when you need display data, and wrap in `cache()` if called multiple times per render.

### Server Action

```typescript
'use server';
import { auth } from '@clerk/nextjs/server';

export async function deletePost(postId: string) {
  const { userId } = await auth();
  if (!userId) throw new Error('Unauthorized');
  // ... action logic
}
```

### API Route Handler

```typescript
import { auth } from '@clerk/nextjs/server';

export async function GET() {
  const { userId, orgId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });
  return Response.json({ userId, orgId });
}
```

---

## DAL Pattern (Defence-in-Depth)

Re-verify auth in every data-fetching function. Middleware is the first gate, not the only gate — see CVE-2025-29927 in `SKILL.md` Gotchas section.

```typescript
// lib/dal.ts — Data Access Layer
import { cache } from 'react';
import { auth } from '@clerk/nextjs/server';
import { db } from '@/lib/db';
import { redirect } from 'next/navigation';

// cache() memoizes within a single render pass — one DB call even if called N times
export const getUser = cache(async () => {
  const { userId } = await auth();
  if (!userId) return null;
  return db.user.findUnique({ where: { clerkId: userId } });
});

// In any Server Component or Server Action:
export default async function DashboardPage() {
  const user = await getUser();
  if (!user) redirect('/sign-in');
  return <Dashboard user={user} />;
}
```

---

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

---

## Webhook Handler (Clerk User Lifecycle Sync)

Sync Clerk user events to your database. Required if you maintain a local User table. Install: `npm install svix`.

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from 'svix';
import { headers } from 'next/headers';
import { WebhookEvent } from '@clerk/nextjs/server';

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET;
  if (!WEBHOOK_SECRET) throw new Error('CLERK_WEBHOOK_SECRET is not set');

  const headerPayload = await headers();
  const svixId = headerPayload.get('svix-id');
  const svixTimestamp = headerPayload.get('svix-timestamp');
  const svixSignature = headerPayload.get('svix-signature');

  if (!svixId || !svixTimestamp || !svixSignature) {
    return new Response('Missing svix headers', { status: 400 });
  }

  const body = await req.text();
  let event: WebhookEvent;
  try {
    event = new Webhook(WEBHOOK_SECRET).verify(body, {
      'svix-id': svixId,
      'svix-timestamp': svixTimestamp,
      'svix-signature': svixSignature,
    }) as WebhookEvent;
  } catch {
    return new Response('Invalid signature', { status: 400 });
  }

  // Idempotency: check svix-id before processing to reject duplicate deliveries
  const existing = await db.webhookEvent.findUnique({ where: { svixId } });
  if (existing) return new Response('Already processed', { status: 200 });
  await db.webhookEvent.create({ data: { svixId } });

  if (event.type === 'user.created') {
    await db.user.create({
      data: {
        clerkId: event.data.id,
        email: event.data.email_addresses[0].email_address,
      },
    });
  }
  if (event.type === 'user.updated') {
    await db.user.update({
      where: { clerkId: event.data.id },
      data: { email: event.data.email_addresses[0].email_address },
    });
  }
  if (event.type === 'user.deleted' && event.data.id) {
    await db.user.delete({ where: { clerkId: event.data.id } });
  }

  return new Response('OK');
}
```

**Webhook setup:**
1. In Clerk Dashboard -> Webhooks -> Add Endpoint
2. Set URL to `{PROD_URL}/api/webhooks/clerk`
3. Subscribe to: `user.created`, `user.updated`, `user.deleted`
4. Copy Signing Secret -> add to `CLERK_WEBHOOK_SECRET` env var

---

## Failure Modes

| Scenario | What Happens | How to Handle |
|---|---|---|
| Token refresh race (two browser tabs) | Both tabs attempt refresh; one gets stale token | Handled automatically by Clerk |
| OAuth provider returns unexpected scope | Callback fails silently | Validate `account.scope` in callback; contact Clerk support if persistent |
| Middleware misconfiguration | Protected routes accessible without auth | Test with `curl` and empty cookie header; response should redirect to sign-in |
| Webhook replay attack | Webhook handler processes same event twice | Store `svix-id` and reject duplicates (idempotency pattern above) |
| `authMiddleware` import | Build error — removed in Clerk 6.x | Replace with `clerkMiddleware` + `createRouteMatcher` |
| `currentUser()` on every page | Network call to Clerk API on every render | Use `auth()` for access control; wrap `currentUser()` in `cache()` |
