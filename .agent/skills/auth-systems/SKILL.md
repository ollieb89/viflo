---
name: auth-systems
description: Use when implementing authentication in Next.js App Router applications. Covers Clerk (managed auth — primary path) and Better Auth (self-hosted alternative) with sign-up, sign-in, protected routes via middleware, OAuth providers, session data access in server components/actions/API routes, Clerk webhook lifecycle sync, and the App Router cache-bypass pitfall (CVE-2025-29927).
---

# Auth Systems

> See `references/clerk-patterns.md` for full Clerk implementation details. See `references/better-auth-patterns.md` for full Better Auth implementation details.

## Quick Start

Minimal Clerk setup — add auth to an existing Next.js App Router app:

```bash
npm install @clerk/nextjs svix
```

```bash
# .env.local — get these from Clerk Dashboard -> API Keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```

```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

```typescript
// middleware.ts — protect /dashboard and all sub-routes
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isPublicRoute = createRouteMatcher([
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/webhooks(.*)",
]);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect(); // redirects to sign-in if unauthenticated
  }
});

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
```

> Self-hosting? Jump to Better Auth in section 1.

---

## 1. Setup

### Clerk (Managed Auth — Primary Path)

```bash
npm install @clerk/nextjs svix
```

**Env vars** (from Clerk Dashboard -> API Keys):

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
CLERK_WEBHOOK_SECRET=whsec_...          # only if using webhooks
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

**Wrap layout with ClerkProvider:**

```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

### Better Auth (Self-Hosted Alternative)

> **Note:** Better Auth replaced Auth.js as the recommended self-hosted auth solution in Sept 2025. Auth.js/NextAuth is maintenance-mode — the core team joined Better Auth. Do not use Auth.js for new projects.

```bash
npm install better-auth
```

> **Database adapter:** Uses raw `pg.Pool` in this quick-start (zero extra deps). If you use Prisma: `npm install @better-auth/prisma` and replace `Pool` with the Better Auth Prisma adapter.

**Env vars:**

```bash
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=                     # generate: openssl rand -base64 32
BETTER_AUTH_URL=http://localhost:3000   # production: your domain
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

**Core config:**

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { Pool } from "pg";

export const auth = betterAuth({
  database: new Pool({ connectionString: process.env.DATABASE_URL }),
  emailAndPassword: { enabled: true },
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
});
```

**Route handler:**

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { POST, GET } = toNextJsHandler(auth);
```

**Run schema migration:**

```bash
npx @better-auth/cli generate
npx @better-auth/cli migrate
```

---

## 2. Configuration

### Protected Routes (Side-by-Side)

**Clerk:**

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isPublicRoute = createRouteMatcher([
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/webhooks(.*)",
]);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect(); // redirects unauthenticated users to sign-in
  }
});

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
```

**Better Auth:**

Two approaches — choose based on your needs:

- **Approach A (fast — cookie check, no DB):** `getSessionCookie(request)` from `better-auth/cookies` — use for most routes
- **Approach B (full session fetch):** `auth.api.getSession({ headers: request.headers })` — use when you need user data in middleware

> Use Approach A in middleware + DAL in server components for defence-in-depth. See Gotchas section.

```typescript
// middleware.ts — Approach A (recommended for most apps)
import { NextRequest, NextResponse } from "next/server";
import { getSessionCookie } from "better-auth/cookies";

export async function middleware(request: NextRequest) {
  const sessionCookie = getSessionCookie(request);
  if (!sessionCookie && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/sign-in", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
```

### OAuth Providers (GitHub, Google)

**Clerk:**
Configure in Clerk Dashboard -> User & Authentication -> Social Connections. No code changes required. Add the callback URL shown in the Dashboard.

> OAuth config is entirely in the Dashboard — zero code changes needed.

**Better Auth:**
The `socialProviders` config is already in `lib/auth.ts` (section 1). To set up the OAuth apps:

- **GitHub:** Create OAuth app at `github.com/settings/applications/new`. Set callback URL to `{BASE_URL}/api/auth/callback/github`.
- **Google:** Create OAuth 2.0 Client ID at `console.cloud.google.com` -> APIs & Services -> Credentials. Set authorized redirect URI to `{BASE_URL}/api/auth/callback/google`.

Copy the Client ID and Secret into `.env.local` for each provider.

---

## 3. Patterns

### Session Data: Server Components, Server Actions, API Routes

**Clerk:**

```typescript
// Server component — access control (no network call)
import { auth, currentUser } from '@clerk/nextjs/server';

export default async function DashboardPage() {
  const { userId } = await auth();     // reads from JWT — no network call
  if (!userId) redirect('/sign-in');

  // Only call currentUser() when you need display data (network call to Clerk API)
  // const user = await currentUser();
  return <Dashboard userId={userId} />;
}
```

```typescript
// Server action
import { auth } from "@clerk/nextjs/server";

export async function deletePost(postId: string) {
  const { userId } = await auth();
  if (!userId) throw new Error("Unauthorized");
  // ... action logic
}
```

```typescript
// API route handler
import { auth } from "@clerk/nextjs/server";

export async function GET() {
  const { userId } = await auth();
  if (!userId) return new Response("Unauthorized", { status: 401 });
  return Response.json({ userId });
}
```

> Prefer `auth()` over `currentUser()` for access control — `auth()` reads from the JWT (no network); `currentUser()` makes an API call to Clerk. If you call `currentUser()` multiple times per render, wrap it in `cache()`.

**Better Auth:**

```typescript
// Server component
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) redirect('/sign-in');
  return <h1>Welcome {session.user.name}</h1>;
}
```

```typescript
// Server action
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function deletePost(postId: string) {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) throw new Error("Unauthorized");
  // ... action logic
}
```

```typescript
// API route handler
import { auth } from "@/lib/auth";

export async function GET(request: Request) {
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session) return new Response("Unauthorized", { status: 401 });
  return Response.json({ userId: session.user.id });
}
```

### Clerk Webhook Lifecycle Sync

Sync Clerk user events (`user.created`, `user.updated`, `user.deleted`) to your database. Required if you maintain a local User table.

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from "svix";
import { headers } from "next/headers";
import { WebhookEvent } from "@clerk/nextjs/server";

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET;
  if (!WEBHOOK_SECRET) throw new Error("CLERK_WEBHOOK_SECRET not set");

  const headerPayload = await headers();
  const svixId = headerPayload.get("svix-id");
  const svixTimestamp = headerPayload.get("svix-timestamp");
  const svixSignature = headerPayload.get("svix-signature");

  if (!svixId || !svixTimestamp || !svixSignature) {
    return new Response("Missing svix headers", { status: 400 });
  }

  const body = await req.text();
  let event: WebhookEvent;
  try {
    event = new Webhook(WEBHOOK_SECRET).verify(body, {
      "svix-id": svixId,
      "svix-timestamp": svixTimestamp,
      "svix-signature": svixSignature,
    }) as WebhookEvent;
  } catch {
    return new Response("Invalid signature", { status: 400 });
  }

  // Idempotency: reject duplicate deliveries (store svix-id in DB)
  const existing = await db.webhookEvent.findUnique({ where: { svixId } });
  if (existing) return new Response("Already processed", { status: 200 });
  await db.webhookEvent.create({ data: { svixId } });

  if (event.type === "user.created") {
    await db.user.create({
      data: {
        clerkId: event.data.id,
        email: event.data.email_addresses[0].email_address,
      },
    });
  }
  if (event.type === "user.updated") {
    await db.user.update({
      where: { clerkId: event.data.id },
      data: { email: event.data.email_addresses[0].email_address },
    });
  }
  if (event.type === "user.deleted" && event.data.id) {
    await db.user.delete({ where: { clerkId: event.data.id } });
  }

  return new Response("OK");
}
```

**Setup:** In Clerk Dashboard -> Webhooks -> Add Endpoint, set URL to `{PROD_URL}/api/webhooks/clerk`. Subscribe to `user.created`, `user.updated`, `user.deleted`. Copy Signing Secret to `CLERK_WEBHOOK_SECRET` env var.

---

## 4. Gotchas / Pitfalls

### 1. App Router Cache Bypass (CVE-2025-29927) — Middleware Is Not Enough

Next.js App Router can cache React renders. Middleware auth can be bypassed via `x-middleware-subrequest` header manipulation (patched in Next.js 15.2.3) — but even after patching, cached renders can return stale auth state. **Middleware is the first gate, not the only gate.**

**DAL pattern (Data Access Layer) — always re-verify auth in data-fetching functions:**

```typescript
// lib/dal.ts
import { cache } from 'react';
import { auth } from '@clerk/nextjs/server'; // or Better Auth equivalent
import { db } from '@/lib/db';
import { redirect } from 'next/navigation';

// React cache() memoizes within a single render pass — one DB call per request
export const getUser = cache(async () => {
  const { userId } = await auth();
  if (!userId) return null;
  return db.user.findUnique({ where: { clerkId: userId } });
});

// In any Server Component:
export default async function DashboardPage() {
  const user = await getUser(); // memoized — called N times, runs once
  if (!user) redirect('/sign-in');
  return <Dashboard user={user} />;
}
```

**Requirement:** Next.js 15.2.3+ (patches CVE-2025-29927). Check: `npx next --version`

**Warning signs:**

- Auth only in middleware, no re-verification in data functions
- No `cache()` wrapper on `getUser` or similar DAL functions
- Next.js version below 15.2.3

### 2. Using `currentUser()` Everywhere in Clerk

Each `currentUser()` call makes a network request to Clerk's API. Use `auth()` for access control (reads from JWT — no network). Reserve `currentUser()` for when you need display data. Always wrap in `cache()` if called in multiple places per render.

### 3. Better Auth Full Session Fetch in Middleware

`auth.api.getSession()` in middleware makes a DB round trip on every request. Use `getSessionCookie()` (cookie check) for the middleware fast path. Reserve full session fetch for server components that need user data.

### 4. Deprecated: `authMiddleware` (Clerk)

`authMiddleware` was deprecated in Clerk 5.x and removed in 6.x. Use `clerkMiddleware` + `createRouteMatcher`.

**Warning sign:** Any import of `authMiddleware` from `@clerk/nextjs`.

### 5. Auth.js / NextAuth as Self-Hosted Alternative

Auth.js/NextAuth is maintenance-mode as of Sept 2025. The core team joined Better Auth. Do not use Auth.js for new projects. If migrating from Auth.js, see Better Auth migration docs at `better-auth.com/docs/migrations/next-auth`.
