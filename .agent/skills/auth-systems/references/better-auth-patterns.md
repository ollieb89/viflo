# Better Auth Patterns

> Self-hosted auth alternative to Clerk. Better Auth replaced Auth.js as the recommended self-hosted solution (Sept 2025 — Auth.js team joined Better Auth). Auth.js/NextAuth is maintenance-mode — do not use for new projects.

## Installation & Setup

### Install

```bash
npm install better-auth
```

### Environment Variables

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
BETTER_AUTH_SECRET=                     # generate: openssl rand -base64 32
BETTER_AUTH_URL=http://localhost:3000   # production: your domain
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### lib/auth.ts — Core Config

```typescript
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

> **Prisma adapter:** If you use Prisma, replace `Pool` with the Better Auth Prisma adapter: `npm install @better-auth/prisma`. See `better-auth.com/docs/adapters/prisma` for schema setup.

### lib/auth-client.ts — Browser Client

```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL, // your app's base URL
});
```

### app/api/auth/[...all]/route.ts — Route Handler

```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { POST, GET } = toNextJsHandler(auth);
```

### Database Migration

```bash
npx @better-auth/cli generate   # generates migration SQL
npx @better-auth/cli migrate    # applies migration to DATABASE_URL
```

---

## Middleware

### Fast Path (Recommended)

Use `getSessionCookie` for middleware — cookie check only, no DB round trip. Suitable for most protected routes.

```typescript
// middleware.ts
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

### Full Session Fetch

Use only when middleware needs to inspect user data (e.g., role-based routing). Makes a DB round trip on every request — avoid for general route protection.

```typescript
// middleware.ts — Approach B (use sparingly)
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session && request.nextUrl.pathname.startsWith("/dashboard")) {
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

---

## Session Access

### Server Component

```typescript
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });
  if (!session) redirect('/sign-in');
  return <h1>Welcome {session.user.name}</h1>;
}
```

### Server Action

```typescript
"use server";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function deletePost(postId: string) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });
  if (!session) throw new Error("Unauthorized");
  // ... action logic
}
```

### API Route Handler

```typescript
import { auth } from "@/lib/auth";

export async function GET(request: Request) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });
  if (!session) return new Response("Unauthorized", { status: 401 });
  return Response.json({ userId: session.user.id, email: session.user.email });
}
```

### DAL Pattern (Defence-in-Depth)

Wrap `auth.api.getSession` in React's `cache()` to memoize per render pass. Combines with middleware for defence-in-depth.

```typescript
// lib/dal.ts
import { cache } from 'react';
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';

// cache() memoizes within a single render pass — one DB call even if called N times
export const getSession = cache(async () => {
  const session = await auth.api.getSession({
    headers: await headers(),
  });
  return session;
});

// In any Server Component or Server Action:
export default async function DashboardPage() {
  const session = await getSession(); // memoized — only runs once per render
  if (!session) redirect('/sign-in');
  return <Dashboard user={session.user} />;
}
```

---

## OAuth Providers

### GitHub Setup

1. Create OAuth app at `github.com/settings/applications/new`
2. Homepage URL: `http://localhost:3000` (production: your domain)
3. Authorization callback URL: `{BASE_URL}/api/auth/callback/github`
4. Copy Client ID and Client Secret to `.env.local`

### Google Setup

1. Go to `console.cloud.google.com` -> APIs & Services -> Credentials
2. Create OAuth 2.0 Client ID (Web application)
3. Authorized redirect URI: `{BASE_URL}/api/auth/callback/google`
4. Copy Client ID and Secret to `.env.local`

### Adding More Providers

Better Auth supports many OAuth providers. Add to `socialProviders` in `lib/auth.ts`. See `better-auth.com/docs/authentication/social` for the full list.

---

## Client-Side Usage

### Sign In / Sign Up

```typescript
"use client";
import { authClient } from "@/lib/auth-client";

// Email/password sign-in
await authClient.signIn.email({ email, password });

// Email/password sign-up
await authClient.signUp.email({ email, password, name });

// OAuth sign-in (redirects to provider)
await authClient.signIn.social({ provider: "github" });
await authClient.signIn.social({ provider: "google" });
```

### Sign Out

```typescript
"use client";
import { authClient } from "@/lib/auth-client";

await authClient.signOut();
```

### Get Session (Client Component)

```typescript
'use client';
import { authClient } from '@/lib/auth-client';

export function UserGreeting() {
  const { data: session, isPending, error } = authClient.useSession();

  if (isPending) return <div>Loading...</div>;
  if (!session) return <a href="/sign-in">Sign in</a>;
  return <div>Welcome, {session.user.name}</div>;
}
```

---

## Version Context

| Library               | Last Verified | Notes                                                    |
| --------------------- | ------------- | -------------------------------------------------------- |
| `better-auth`         | 1.3.x         | `betterAuth()` config + `toNextJsHandler` for App Router |
| `better-auth/cookies` | (bundled)     | `getSessionCookie` for fast middleware path              |
| `better-auth/next-js` | (bundled)     | `toNextJsHandler` mounts Better Auth in App Router       |
| `better-auth/react`   | (bundled)     | `createAuthClient` for client components                 |
| Next.js               | 15.2.3+       | Required — patches CVE-2025-29927 middleware bypass      |

---

## Failure Modes

| Scenario                                  | What Happens                                   | How to Handle                                                                                   |
| ----------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `DATABASE_URL` not set                    | Server error on first auth request             | Check env vars before first request; Better Auth logs the missing config                        |
| `BETTER_AUTH_SECRET` not set or too short | Sessions can be forged                         | Always use `openssl rand -base64 32`; never use a predictable secret                            |
| Migration not run                         | Table does not exist error on first login      | Run `npx @better-auth/cli migrate` before first request                                         |
| OAuth callback URL mismatch               | Provider returns `redirect_uri_mismatch` error | Callback URL in provider dashboard must exactly match `{BASE_URL}/api/auth/callback/{provider}` |
| Full session fetch in middleware          | DB round trip on every request                 | Use `getSessionCookie()` fast path in middleware; reserve full fetch for server components      |
| Prisma adapter vs raw `pg.Pool`           | Schema table names differ                      | Use `@better-auth/prisma` for Prisma projects; do not mix adapters                              |
| `BETTER_AUTH_URL` not set                 | OAuth callbacks fail in production             | Set to your production domain; must match provider redirect URI                                 |
