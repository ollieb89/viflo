---
name: auth-systems
description: Use when implementing authentication in web applications. Covers Clerk (managed auth) and Auth.js/NextAuth (self-hosted) with session handling, protected routes, OAuth providers, and common production edge cases.
---

# Auth Systems

> **Reference skill** — built to the `skill-depth-standard`. See `references/clerk-patterns.md` for Clerk-specific implementation and `references/authjs-patterns.md` for Auth.js/NextAuth patterns.

## Decision Matrix

**Default recommendation:** Start with Clerk. Switch to Auth.js when you need full database control, custom adapters, or cost at scale.

| Situation | Choice | Why |
|---|---|---|
| New SaaS, < 10k MAU | Clerk | Zero infra, fast to ship, generous free tier |
| Compliance: must own session data | Auth.js | Full control, no third-party session storage |
| Custom database adapter needed | Auth.js | Clerk doesn't support custom adapters |
| Multi-tenant orgs needed out-of-box | Clerk | Native org model, no custom code required |
| > 100k MAU, cost-sensitive | Auth.js | Clerk pricing scales per user |
| Need pre-built UI (sign-in, profile, org switcher) | Clerk | Drop-in components, no design work |

## Implementation Patterns

See `references/clerk-patterns.md` for Clerk and `references/authjs-patterns.md` for Auth.js.

**Middleware — Clerk (Next.js App Router):**

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

**Middleware — Auth.js (Next.js App Router):** See `references/authjs-patterns.md` for the Auth.js v5 middleware pattern.

## Failure Modes & Edge Cases

| Scenario | What Happens | How to Handle |
|---|---|---|
| Token refresh race (two browser tabs) | Both tabs attempt refresh; one gets stale token | Auth.js: use database sessions (not JWT) to eliminate race. Clerk: handled automatically. |
| OAuth provider returns unexpected scope | Callback fails silently if required scope is missing | Validate `account.scope` in `signIn` callback; return `false` to reject the login |
| Middleware misconfiguration | Protected routes accessible without auth | Test with `curl` and an empty/missing cookie header; response should redirect to sign-in |
| JWT secret rotation | All existing sessions invalidated immediately | Auth.js: pass `secret` as an array `[newSecret, oldSecret]` to support graceful rollover |
| Clerk webhook replay attack | Webhook handler processes same event twice | Store `svix-id` and reject duplicates; verify `svix-timestamp` is within 5 minutes |
| Concurrent login on new device | Session limit exceeded silently or old session not invalidated | Clerk: configure session limit in dashboard. Auth.js: query sessions table and invalidate oldest. |

## Version Context

| Library | Last Verified | Notes |
|---|---|---|
| `@clerk/nextjs` | 6.x | `clerkMiddleware` replaces `authMiddleware` (deprecated in 5.x) |
| `next-auth` / `@auth/core` | 5.x (Auth.js v5) | Breaking from v4: config moves to `auth.ts`, drops `pages/api/auth` pattern |
| `@auth/prisma-adapter` | 2.x | Requires Prisma 5.x; session/account table schema changed from v1 |
| Next.js | 15.x | App Router only; Pages Router auth pattern differs significantly |
