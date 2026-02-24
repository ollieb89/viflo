# Phase 11: Foundation Skills - Research

**Researched:** 2026-02-24
**Domain:** Skill authoring — Prompt Engineering (Anthropic SDK) + Auth Systems (Clerk / Better Auth)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Skill structure & navigation**
- Open with a quick start first — minimal working example developers can copy, then build depth
- File/split decision is Claude's discretion based on final content size
- Numbered sections (1. Setup, 2. Config, 3. Patterns) for clear tutorial progression
- Dedicated named **Gotchas / Pitfalls** section (not inline warnings) — AUTH-05 cache pitfall and PROMPT-04 anti-patterns land here

**Clerk vs Better Auth treatment**
- Clerk is the primary path; Better Auth is framed as the self-hosted alternative
- Side-by-side comparison for the protected-route/middleware pattern — show the Clerk version, then the Better Auth equivalent
- Clerk webhook lifecycle sync only (AUTH-06) — Better Auth users manage their own DB so no equivalent webhook section needed
- App Router cache pitfall (AUTH-05) documented once at the framework level — it's a Next.js App Router issue, not Clerk-specific

**Code example depth**
- Copy-paste ready — full working files where possible; developer should be able to drop in with minimal adjustment
- Full TypeScript with proper type annotations throughout (target stack is Next.js App Router + TypeScript)
- Prompt engineering examples use real Claude TypeScript SDK calls with real model IDs — not pseudocode
- Anti-pattern examples (PROMPT-04) use Before/After format: bad code block followed by corrected version

**Prompt golden set & evaluation**
- Golden set: a folder of `.md` test case files (input prompt + expected output criteria) + a TypeScript script that calls Claude and compares results. Developer runs: `npx ts-node eval.ts` and sees pass/fail
- Prompt versioning: Git-tracked files — each prompt variant is a file, git history is the version history. The skill explains: version prompts like code
- `applies-to:` and `last-verified-against:` frontmatter: defined schema with valid values (e.g. `applies-to: [claude-opus-4-6, claude-sonnet-4-6]`, `last-verified-against: claude-sonnet-4-6`)
- Golden set includes one example per pattern — three total: chain-of-thought, few-shot, and output format specification

### Claude's Discretion
- Whether to split auth skill into one file or two (clerk.md + better-auth.md) based on final content size
- Exact number of anti-patterns in the PROMPT-04 catalogue (requirements say top 5)
- Spacing, typography, and exact prose style within sections

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PROMPT-01 | Developer can write structured prompts using role/context/task/output anatomy | Anthropic SDK `messages.create` with `system` + `messages` pattern; existing skill has the `buildPrompt` template function — needs quick-start upgrade |
| PROMPT-02 | Skill documents model-specific technique applicability with `applies-to:` tags and `last-verified-against:` frontmatter | Defined schema using current model IDs: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`; documented in Version Context section |
| PROMPT-03 | Developer can apply chain-of-thought, few-shot, and output format specification patterns | Existing skill and references cover all three; SDK now has `client.messages.parse` + `zodOutputFormat` / `jsonSchemaOutputFormat` for structured output |
| PROMPT-04 | Skill includes an anti-pattern catalogue (top 5 output-degrading patterns) | Existing `references/anti-patterns.md` covers injection, drift, structured output failure — needs 2 more anti-patterns and Before/After format per locked decision |
| PROMPT-05 | Developer can version and evaluate prompts using a golden set (no external platform required) | Golden set architecture defined: `.md` test case files + `eval.ts` TypeScript runner; existing `references/evaluation-workflows.md` covers scoring rubrics |
| AUTH-01 | Developer can follow a Clerk quick-start to add auth to a Next.js App Router app (sign-up, sign-in, protected routes via middleware.ts) | Verified: `clerkMiddleware` + `createRouteMatcher` from `@clerk/nextjs/server` 6.x; existing skill has working code |
| AUTH-02 | Developer can configure Better Auth as the self-hosted alternative with the same protected-route pattern | Verified: `getSessionCookie` fast-path or `auth.api.getSession` full-path in `middleware.ts`; `toNextJsHandler` for route handler; Better Auth v1.3.x |
| AUTH-03 | Developer can access session data in server components, server actions, and API routes | Verified: Clerk uses `auth()` / `currentUser()` from `@clerk/nextjs/server`; Better Auth uses `auth.api.getSession({ headers: await headers() })` |
| AUTH-04 | Developer can wire OAuth providers (GitHub, Google) through both Clerk and Better Auth | Verified: Clerk — configured via Dashboard UI, no code change; Better Auth — `socialProviders: { github: {...}, google: {...} }` in `betterAuth()` config |
| AUTH-05 | Skill documents the App Router cache pitfall and DAL re-validation pattern to prevent auth bypass | CVE-2025-29927 confirmed: middleware-only auth is bypassable; DAL pattern with `cache()` memoization is the correct fix; requires Next.js 15.2.3+ |
| AUTH-06 | Developer can set up a Clerk webhook receiver for user lifecycle sync (created, updated, deleted) | Verified: svix signature verification + idempotency via `svix-id` storage; existing skill has full working example |
</phase_requirements>

## Summary

Phase 11 produces two complete, shippable skills: `prompt-engineering` and `auth-systems`. Both skills already exist in `.agent/skills/` with basic structure and reference files — they pass `quick_validate.py` — but they were built to an earlier, thinner standard and require significant expansion to meet the v1.2 requirements defined in CONTEXT.md.

The primary work is **authoring depth**: upgrading existing skills rather than building from scratch. The prompt-engineering skill needs a quick-start section, model-specific applicability documentation with `applies-to:` frontmatter schema, Before/After anti-pattern format, and the golden-set eval architecture. The auth-systems skill needs Better Auth to replace Auth.js (the team migrated to Better Auth in Sept 2025; Auth.js is now maintenance-mode per STATE.md), a side-by-side Clerk/Better Auth middleware comparison, and the App Router cache-bypass pitfall section.

**Primary recommendation:** Treat both skills as rewrites-in-place. The structure is right; the content depth, Better Auth migration, and CONTEXT.md decisions are not yet reflected. Preserve the `skill-depth-standard` four-section structure while layering in the numbered tutorial progression and dedicated Gotchas sections.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `@anthropic-ai/sdk` | latest (SDK ≥ 0.40) | Claude API calls in prompt-engineering examples | Official SDK; `client.messages.create` is the canonical call pattern |
| `@clerk/nextjs` | 6.x | Managed auth — primary auth path | `clerkMiddleware` replaces deprecated `authMiddleware`; drop-in protected routes |
| `better-auth` | 1.3.x | Self-hosted auth — alternative path | Auth.js team migrated here Sept 2025; Auth.js is maintenance-mode |
| `svix` | latest | Clerk webhook signature verification | Used inside Clerk's own SDK; required for webhook security |
| `zod` | 3.x | Structured output schema validation in prompt eval | Used in SDK's `zodOutputFormat` helper; already in most Next.js projects |
| `ts-node` | 10.x | Running `eval.ts` golden set runner | Developer tool; `npx ts-node eval.ts` is the prescribed invocation |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `@anthropic-ai/sdk/helpers/zod` | (bundled) | `zodOutputFormat()` for structured Claude output | When output needs Zod schema validation and `messages.parse` |
| `@anthropic-ai/sdk/helpers/json-schema` | (bundled) | `jsonSchemaOutputFormat()` | When Zod is not in the project |
| `better-auth/next-js` | (bundled) | `toNextJsHandler` adapter | Required to mount Better Auth in App Router route handler |
| `better-auth/cookies` | (bundled) | `getSessionCookie` | Fast middleware path — cookie check without a DB round-trip |
| `next` | 15.2.3+ | Next.js App Router | Must be ≥ 15.2.3 to patch CVE-2025-29927 middleware bypass |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Better Auth (self-hosted) | Auth.js v5 | Auth.js is maintenance-mode as of Sept 2025; Better Auth is the active successor — do not use Auth.js for new projects |
| `zodOutputFormat` helper | Manual JSON parsing + retry | The helper handles structured output parsing correctly in one call; manual approach needs error handling boilerplate |
| Git-tracked prompt files | External prompt management platform | No external dependency; git history is version history; meets PROMPT-05 requirement |

**Installation:**
```bash
# Auth (Clerk path)
npm install @clerk/nextjs svix

# Auth (Better Auth path)
npm install better-auth

# Prompt engineering
npm install @anthropic-ai/sdk zod
npm install -D ts-node @types/node
```

## Architecture Patterns

### Recommended Project Structure

For the skill files themselves (output of this phase):

```
.agent/skills/prompt-engineering/
├── SKILL.md                          # ≤500 lines — quick start + four depth sections
└── references/
    ├── anti-patterns.md              # PROMPT-04: top 5 anti-patterns, Before/After format
    ├── evaluation-workflows.md       # PROMPT-05: golden set architecture + eval.ts runner
    └── golden-set/                   # Example golden set (one per pattern)
        ├── chain-of-thought.md       # Test case file: input prompt + expected criteria
        ├── few-shot.md
        └── output-format.md

.agent/skills/auth-systems/
├── SKILL.md                          # ≤500 lines — quick start + four depth sections
└── references/
    ├── clerk-patterns.md             # Full Clerk implementation (middleware, server, client, webhooks)
    └── better-auth-patterns.md      # Full Better Auth implementation (replaces authjs-patterns.md)
```

Note: `authjs-patterns.md` exists in the current skill. Per the locked decisions, Better Auth replaces Auth.js as the self-hosted alternative. The file should be renamed/replaced to `better-auth-patterns.md`.

### Pattern 1: Skill Quick-Start Section

**What:** Every skill opens with a minimal copy-paste example before any explanation.
**When to use:** Required per locked decisions — "open with a quick start first."
**Example (prompt-engineering SKILL.md opening):**

```typescript
// Source: Context7 /anthropics/anthropic-sdk-typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from env

// 1. Minimal structured prompt
const response = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 1024,
  system: 'You are a helpful assistant. Return only valid JSON.',
  messages: [{ role: 'user', content: 'List the capitals of France and Germany.' }],
});

console.log(response.content[0].text);
// → {"france":"Paris","germany":"Berlin"}
```

### Pattern 2: Numbered Tutorial Progression

**What:** Sections numbered 1. Setup, 2. Config, 3. Patterns, 4. Gotchas / Pitfalls.
**When to use:** Required per locked decisions for both skills.
**Example (auth-systems SKILL.md structure):**

```
# Auth Systems

## Quick Start

[Copy-paste Clerk minimal example]

## 1. Setup

### Clerk
[Installation, env vars, ClerkProvider in layout]

### Better Auth
[Installation, auth.ts config, route handler]

## 2. Configuration

### Protected Routes
[Side-by-side Clerk middleware vs Better Auth middleware]

### OAuth Providers (GitHub, Google)
[Clerk: Dashboard config; Better Auth: socialProviders config]

## 3. Patterns

### Session Data in Server Components, Actions, API Routes
[auth() / currentUser() for Clerk; auth.api.getSession() for Better Auth]

### Clerk Webhook Lifecycle Sync
[AUTH-06 svix verification + idempotency]

## 4. Gotchas / Pitfalls

[AUTH-05: App Router cache pitfall + DAL pattern]
[Middleware-only auth bypass (CVE-2025-29927)]
```

### Pattern 3: `applies-to:` Frontmatter Schema for Prompt Techniques

**What:** Each pattern in the prompt-engineering skill carries frontmatter declaring which models it applies to.
**When to use:** Required for PROMPT-02.
**Schema:**

```markdown
---
applies-to: [claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001]
last-verified-against: claude-sonnet-4-6
verified-date: 2026-02-24
---
```

Valid `applies-to` values (as of 2026-02-24):
- `claude-opus-4-6` — Most capable; best for complex reasoning, CoT
- `claude-sonnet-4-6` — Balanced; recommended default for most production prompts
- `claude-haiku-4-5-20251001` — Fast and cheap; classification, extraction, eval judge

Note: Instruction-tuned models (all Claude) respond well to XML tags for section delimiters (`<context>`, `<task>`). This is Claude-specific — GPT-4o uses plain text sections.

### Pattern 4: Golden Set Eval Architecture

**What:** A folder of `.md` test cases + a `eval.ts` runner the developer invokes with `npx ts-node eval.ts`.
**When to use:** Required for PROMPT-05.

Golden set test case format (`.md` file):

```markdown
---
pattern: chain-of-thought
model: claude-sonnet-4-6
---

## Input Prompt

System: You are a math tutor. Think step by step before answering.
User: If a train travels 120 miles in 2 hours, what is its speed?

## Expected Output Criteria

- Contains step-by-step reasoning before the final answer
- Final answer is "60 mph" or equivalent
- Does not skip directly to answer without showing work
```

Eval runner skeleton (`eval.ts`):

```typescript
// Source: Pattern documented in this research; SDK calls verified against Context7
import Anthropic from '@anthropic-ai/sdk';
import * as fs from 'fs';
import * as path from 'path';

const client = new Anthropic();

interface TestCase {
  pattern: string;
  model: string;
  inputPrompt: string;
  expectedCriteria: string[];
}

async function runEval(testCase: TestCase): Promise<{ passed: boolean; reason: string }> {
  const response = await client.messages.create({
    model: testCase.model,
    max_tokens: 1024,
    messages: [{ role: 'user', content: testCase.inputPrompt }],
  });
  const output = response.content[0].type === 'text' ? response.content[0].text : '';

  // LLM-as-judge: ask Claude to score against criteria
  const judgeResponse = await client.messages.create({
    model: 'claude-haiku-4-5-20251001', // cheap judge
    max_tokens: 256,
    messages: [{
      role: 'user',
      content: `Output: "${output}"\nCriteria: ${testCase.expectedCriteria.join('; ')}\nDoes the output satisfy all criteria? Reply PASS or FAIL and one sentence reason.`,
    }],
  });

  const verdict = judgeResponse.content[0].type === 'text' ? judgeResponse.content[0].text : 'FAIL';
  return { passed: verdict.startsWith('PASS'), reason: verdict };
}

// Run all .md files in golden-set/
// ... (file enumeration and reporting)
```

### Pattern 5: Better Auth Middleware (Two Approaches)

**What:** Better Auth supports two middleware strategies — fast cookie check and full session fetch.
**When to use:** Research confirmed both patterns from official docs.

```typescript
// Source: Context7 /better-auth/better-auth — official docs

// APPROACH A: Fast (cookie check only — no DB round trip)
// Use for most routes — no network call, relies on signed cookie
import { getSessionCookie } from 'better-auth/cookies';

export async function middleware(request: NextRequest) {
  const sessionCookie = getSessionCookie(request);
  if (!sessionCookie && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/sign-in', request.url));
  }
  return NextResponse.next();
}

// APPROACH B: Full session fetch (DB verification)
// Use when you need to validate session data (e.g., check user role)
import { auth } from '@/lib/auth';

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/sign-in', request.url));
  }
  return NextResponse.next();
}
```

**Recommendation:** Use Approach A (cookie check) for performance. The DAL pattern (AUTH-05) then re-validates in server components — defence-in-depth, not redundancy.

### Pattern 6: App Router Cache Pitfall + DAL (AUTH-05)

**What:** Next.js App Router caches `fetch` responses and React renders across requests. Auth checked only in middleware can be stale.
**Why it matters:** CVE-2025-29927 (March 2025) demonstrated that middleware-only auth is bypassable via `x-middleware-subrequest` header manipulation. Even without the CVE, cached renders can return stale auth state.

```typescript
// Source: Next.js official docs + CVE-2025-29927 disclosure
// BAD: auth only in middleware — bypassable, no defence-in-depth
// middleware.ts checks auth → passes → Server Component renders cached data

// GOOD: DAL pattern — re-verify in every data access function
import { cache } from 'react';
import { auth } from '@clerk/nextjs/server'; // or Better Auth equivalent

// React cache() memoizes this within a single render pass (no extra DB calls)
export const getUser = cache(async () => {
  const { userId } = await auth();
  if (!userId) return null;
  return db.user.findUnique({ where: { clerkId: userId } });
});

// In any Server Component:
export default async function DashboardPage() {
  const user = await getUser(); // memoized — only one DB call per render
  if (!user) redirect('/sign-in');
  return <Dashboard user={user} />;
}
```

**Key point for skill:** Document this as a framework-level pitfall (Next.js App Router), not Clerk-specific. Applies equally to Better Auth users.

### Anti-Patterns to Avoid

- **Auth.js as self-hosted path:** Auth.js team joined Better Auth team Sept 2025; Auth.js is maintenance-mode. The existing `authjs-patterns.md` reference file must be replaced with `better-auth-patterns.md`.
- **Middleware-only auth:** Covered in AUTH-05 — always add DAL verification.
- **`authMiddleware` in Clerk:** Deprecated in Clerk 5.x — use `clerkMiddleware` + `createRouteMatcher`.
- **Pseudocode in prompt examples:** Locked decision — all prompt examples must use real SDK calls with real model IDs.
- **Single anti-pattern format:** Locked decision — PROMPT-04 requires Before/After code block pairs, not prose.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Webhook signature verification | Custom HMAC verification | `svix` (Clerk) via `new Webhook(secret).verify(body, headers)` | Timing-safe comparison, svix-timestamp replay protection built in |
| OAuth token exchange | Custom OAuth flow | Clerk Dashboard config / Better Auth `socialProviders` | Token refresh, PKCE, provider quirks handled by library |
| Structured output parsing | `JSON.parse` + regex cleanup | `zodOutputFormat` + `client.messages.parse` | Handles Claude's output format variations; auto-retry on parse failure |
| Session memoization within render | Custom request-scoped cache | React `cache()` wrapping auth call | React memoizes within a render pass; custom solutions miss Server Actions |
| Prompt evaluation platform | External LLM ops tooling | `eval.ts` + LLM-as-judge using cheap model | No external dependency; developer runs `npx ts-node eval.ts` |

**Key insight:** The complexity in both domains (auth, prompt eval) lies in edge cases that libraries have already solved. The skill's job is to show developers how to wire the libraries correctly, not how to build auth or eval infrastructure.

## Common Pitfalls

### Pitfall 1: Auth.js Still Referenced as "Self-Hosted Alternative"

**What goes wrong:** Developer reads skill, implements Auth.js (NextAuth v5), then discovers the library is in maintenance mode with no active development.
**Why it happens:** Auth.js was the dominant self-hosted auth library through 2024; training data and older documentation still references it.
**How to avoid:** The skill must clearly state: "Better Auth is the self-hosted alternative. Auth.js/NextAuth is maintenance-mode as of Sept 2025 — the core team joined Better Auth. Covered only as 'migrating from.'"
**Warning signs:** Any mention of `next-auth` or `@auth/core` as a new project recommendation.

### Pitfall 2: Middleware-Only Auth (AUTH-05 / CVE-2025-29927)

**What goes wrong:** Developer protects routes via middleware, but server components serve stale cached data or the middleware header is forged.
**Why it happens:** Middleware feels like the natural protection layer — it runs on every request and it is the Clerk/Better Auth documentation's first example.
**How to avoid:** Document in Gotchas / Pitfalls: middleware is the first gate, not the only gate. Add DAL with `cache()` in every data-fetching function. Require Next.js 15.2.3+.
**Warning signs:** No `cache()` import in server component data functions. `auth()` called outside a DAL wrapper.

### Pitfall 3: Using `currentUser()` Everywhere in Clerk

**What goes wrong:** Developer calls `currentUser()` in every server component, causing one extra network call to Clerk's API per render.
**Why it happens:** `currentUser()` is the "complete user object" — developers want the full user.
**How to avoid:** Use `auth()` (returns `userId`, `orgId` from the JWT — no network call) for access control. Reserve `currentUser()` for when you need display data. Wrap in `cache()` if used multiple times per render.
**Warning signs:** `currentUser()` called at the top of server components that only need `userId`.

### Pitfall 4: Prompt Anti-Pattern — Concatenating User Input into System Prompt

**What goes wrong:** `const system = "You are a helpful assistant. User name: " + userName + ". " + userMessage` — injection vector.
**Why it happens:** It feels like providing helpful context.
**How to avoid:** User-controlled data goes in the user turn, always. System prompt is developer-controlled static context only.
**Warning signs:** Template literals combining env-controlled content and user content in the `system` field.

### Pitfall 5: Prompt Versioning Without Structure

**What goes wrong:** Developer iterates on prompts in-place; no history of what changed or why; regression introduced and not discoverable.
**Why it happens:** Prompt is a string — easy to edit directly.
**How to avoid:** Each prompt variant is a file. Git history is the version history. Skill explains: "Version prompts like code." The `last-verified-against:` frontmatter field locks each variant to a model snapshot.
**Warning signs:** Single `prompts.ts` with inline string edits and no comment history.

### Pitfall 6: Better Auth Middleware Using Full Session Fetch for Every Route

**What goes wrong:** `auth.api.getSession()` is called in middleware for every request, causing a DB round trip on every page load.
**Why it happens:** Documentation shows the full-fetch pattern first; developers use it uniformly.
**How to avoid:** Use `getSessionCookie(request)` from `better-auth/cookies` in middleware for the fast path. Reserve full `auth.api.getSession()` for server components that need user data. Combined with DAL + `cache()` this is optimal.
**Warning signs:** `auth.api.getSession` called directly in middleware without profiling.

## Code Examples

Verified patterns from official sources:

### Clerk Middleware (Protected Routes)

```typescript
// Source: Context7 /better-auth/better-auth + existing clerk-patterns.md (verified)
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isPublicRoute = createRouteMatcher([
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
]);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect(); // redirects unauthenticated users to sign-in
  }
});

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
};
```

### Better Auth Setup (`lib/auth.ts`)

```typescript
// Source: Context7 /better-auth/better-auth
import { betterAuth } from 'better-auth';
import { Pool } from 'pg'; // or your DB adapter

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

### Better Auth Route Handler

```typescript
// Source: Context7 /better-auth/better-auth — official docs
// app/api/auth/[...all]/route.ts
import { auth } from '@/lib/auth';
import { toNextJsHandler } from 'better-auth/next-js';

export const { POST, GET } = toNextJsHandler(auth);
```

### Better Auth Session in Server Component

```typescript
// Source: Context7 /better-auth/better-auth
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

### Anthropic SDK — Structured Prompt with Zod Output

```typescript
// Source: Context7 /anthropics/anthropic-sdk-typescript
import Anthropic from '@anthropic-ai/sdk';
import { zodOutputFormat } from '@anthropic-ai/sdk/helpers/zod';
import { z } from 'zod';

const client = new Anthropic();

const SentimentSchema = z.object({
  sentiment: z.enum(['positive', 'negative', 'neutral']),
  confidence: z.number().min(0).max(1),
});

const message = await client.messages.parse({
  model: 'claude-sonnet-4-6',
  max_tokens: 256,
  messages: [{ role: 'user', content: 'Classify: "Fast shipping, exactly as described."' }],
  output_config: {
    format: zodOutputFormat(SentimentSchema),
  },
});

console.log(message.parsed_output?.sentiment); // 'positive'
```

### Chain-of-Thought Pattern (PROMPT-03)

```typescript
// Source: Anthropic SDK verified; CoT pattern is model-agnostic
const response = await client.messages.create({
  model: 'claude-sonnet-4-6',     // applies-to: [claude-opus-4-6, claude-sonnet-4-6]
  max_tokens: 2048,               // CoT needs space to reason
  system: 'Think through this step by step before giving your final answer.',
  messages: [{ role: 'user', content: 'If a train travels 120 miles in 2 hours, what is its speed?' }],
});
```

### Few-Shot Pattern (PROMPT-03)

```typescript
// Source: Existing skill references/anti-patterns.md (verified pattern; model IDs updated)
const messages: Anthropic.MessageParam[] = [
  { role: 'user', content: 'Classify sentiment: "Product arrived broken."' },
  { role: 'assistant', content: '{"sentiment": "negative", "confidence": 0.97}' },
  { role: 'user', content: 'Classify sentiment: "Fast shipping, exactly as described."' },
  { role: 'assistant', content: '{"sentiment": "positive", "confidence": 0.95}' },
  { role: 'user', content: `Classify the sentiment.\n\nText: ${userInput}` }, // userInput is NOT in quotes
];
// applies-to: [claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001]
```

### Clerk Webhook Handler with Idempotency (AUTH-06)

```typescript
// Source: Existing clerk-patterns.md (verified; matches Clerk 6.x API)
// app/api/webhooks/clerk/route.ts
import { Webhook } from 'svix';
import { headers } from 'next/headers';
import { WebhookEvent } from '@clerk/nextjs/server';

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET;
  if (!WEBHOOK_SECRET) throw new Error('CLERK_WEBHOOK_SECRET not set');
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
  // Idempotency: reject duplicate deliveries
  const existing = await db.webhookEvent.findUnique({ where: { svixId } });
  if (existing) return new Response('Already processed', { status: 200 });
  await db.webhookEvent.create({ data: { svixId } });

  if (event.type === 'user.created') {
    await db.user.create({
      data: { clerkId: event.data.id, email: event.data.email_addresses[0].email_address },
    });
  }
  if (event.type === 'user.deleted') {
    await db.user.delete({ where: { clerkId: event.data.id } });
  }
  return new Response('OK');
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Auth.js (NextAuth v5) as self-hosted alternative | Better Auth v1.3.x | Sept 2025 — Auth.js team joined Better Auth | Auth.js is maintenance-mode; Better Auth is the active successor for self-hosted auth |
| `authMiddleware` (Clerk) | `clerkMiddleware` + `createRouteMatcher` | Clerk 5.x (deprecated), fully removed in 6.x | `authMiddleware` will not work in `@clerk/nextjs` 6.x |
| Manual JSON.parse for structured output | `client.messages.parse` + `zodOutputFormat` / `jsonSchemaOutputFormat` | SDK ≥ 0.40 (2025) | Structured output with auto-validation; no retry boilerplate needed |
| External prompt versioning tools | Git-tracked `.md` prompt files with frontmatter | 2025 (community convergence) | No external dependency; PROMPT-05 compliant |
| Middleware-only auth protection | Middleware + DAL with `cache()` (defence-in-depth) | CVE-2025-29927 (March 2025) | Middleware alone is bypassable; DAL re-verification is required |

**Deprecated/outdated:**
- `next-auth` / `@auth/core` as primary self-hosted auth: maintenance-mode, no new features
- `authMiddleware` from `@clerk/nextjs`: removed in 6.x
- Claude model ID `claude-haiku-3-5` as the cheap judge: use `claude-haiku-4-5-20251001`
- The existing `.agent/skills/auth-systems/references/authjs-patterns.md`: must be replaced by `better-auth-patterns.md`

## Open Questions

1. **Better Auth database adapter choice**
   - What we know: Better Auth supports Prisma, Drizzle, raw SQL (via `pg.Pool`), and others
   - What's unclear: Which adapter to show in the skill's quick-start — Prisma is most common in Next.js projects, but the skill should not add a Prisma dependency
   - Recommendation: Use raw `pg.Pool` in the quick-start (zero extra deps); add a callout: "If you use Prisma, replace `Pool` with the Better Auth Prisma adapter."

2. **Golden set runner output format**
   - What we know: Developer runs `npx ts-node eval.ts` and sees pass/fail
   - What's unclear: Whether to print a table, JSON, or simple per-test lines
   - Recommendation: Simple stdout per-test line (`✓ chain-of-thought: PASS`, `✗ few-shot: FAIL — ...`) with exit code 1 on any failure; no over-engineering

3. **Prompt anti-pattern count for PROMPT-04**
   - What we know: Requirements say "top 5"; Claude's discretion on exact count
   - What's unclear: Whether the existing 3 in `anti-patterns.md` (injection, drift, structured output) are the right 3 to keep
   - Recommendation: Keep all 3 existing; add 2 more: (4) over-specifying output at the expense of quality (constraint overload), (5) burying key instructions in the middle of a long prompt ("lost in the middle")

## Sources

### Primary (HIGH confidence)

- Context7 `/better-auth/better-auth` (2752 snippets, High reputation) — Better Auth middleware patterns, social providers, session in server components, route handler setup
- Context7 `/anthropics/anthropic-sdk-typescript` (260 snippets, High reputation) — `messages.create`, `messages.parse`, `zodOutputFormat`, `jsonSchemaOutputFormat`
- Existing `.agent/skills/auth-systems/` — Clerk patterns verified; Auth.js patterns confirmed outdated (to be replaced)
- Existing `.agent/skills/prompt-engineering/` — Core patterns verified; references need Before/After format and golden set additions

### Secondary (MEDIUM confidence)

- WebSearch: CVE-2025-29927 Next.js middleware auth bypass (March 2025) — confirmed by multiple security sources including ProjectDiscovery; mitigation is Next.js 15.2.3+
- WebSearch: Anthropic model IDs (Feb 2026) — confirmed `claude-opus-4-6`, `claude-sonnet-4-6` as current; `claude-haiku-4-5-20251001` as current haiku

### Tertiary (LOW confidence)

- None required — all key claims verified via Context7 or official sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified via Context7 for both Better Auth and Anthropic SDK; Clerk verified via existing working skill code
- Architecture: HIGH — locked decisions from CONTEXT.md are prescriptive; structure patterns verified against existing skill format
- Pitfalls: HIGH — Auth.js deprecation confirmed via STATE.md + project history; CVE-2025-29927 confirmed via WebSearch with multiple sources; other pitfalls verified from official docs

**Research date:** 2026-02-24
**Valid until:** 2026-03-26 (stable stack; Better Auth 1.3.x minor releases unlikely to break patterns within 30 days)
