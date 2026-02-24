---
phase: 11-foundation-skills
plan: 02
subsystem: auth
tags:
  [clerk, better-auth, nextjs, middleware, oauth, webhooks, svix, typescript]

# Dependency graph
requires: []
provides:
  - "auth-systems SKILL.md rewritten to v1.2 depth: quick-start, numbered sections, side-by-side Clerk/Better Auth middleware, DAL pattern with cache(), CVE-2025-29927 documentation"
  - "better-auth-patterns.md: complete Better Auth reference (setup, middleware, session access, OAuth, client-side usage)"
  - "clerk-patterns.md upgraded: DAL pattern, version context table, failure modes"
  - "authjs-patterns.md replaced with deprecation stub"
affects:
  [stripe-payments, agent-architecture, any phase using auth-systems skill]

# Tech tracking
tech-stack:
  added:
    [better-auth, better-auth/cookies, better-auth/next-js, better-auth/react]
  patterns:
    - "DAL pattern: wrap auth calls in React cache() for memoization and defence-in-depth"
    - "Better Auth fast middleware path: getSessionCookie() for cookie check without DB round trip"
    - "Clerk webhook idempotency: store svix-id in DB to reject duplicate deliveries"

key-files:
  created:
    - ".agent/skills/auth-systems/references/better-auth-patterns.md"
  modified:
    - ".agent/skills/auth-systems/SKILL.md"
    - ".agent/skills/auth-systems/references/clerk-patterns.md"
    - ".agent/skills/auth-systems/references/authjs-patterns.md"

key-decisions:
  - "Better Auth replaces Auth.js as the self-hosted alternative — Auth.js is maintenance-mode since Sept 2025 (core team joined Better Auth)"
  - "authjs-patterns.md deprecated in-place with redirect stub rather than deleted — preserves git history"
  - "Better Auth middleware uses getSessionCookie() fast path (Approach A) as the recommended default; full auth.api.getSession() reserved for server components"
  - "CVE-2025-29927 documented as framework-level pitfall (Next.js App Router), not Clerk-specific — applies equally to Better Auth users"

patterns-established:
  - "Quick Start first: minimal copy-paste Clerk example before any explanation"
  - "Numbered sections 1-4: Setup, Configuration, Patterns, Gotchas — tutorial progression"
  - "Side-by-side comparisons: show Clerk pattern then Better Auth equivalent for protected routes"
  - "DAL with cache(): re-verify auth in data functions, not just middleware"

requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06]

# Metrics
duration: 3min
completed: 2026-02-24
---

# Phase 11 Plan 02: Auth Systems Skill Rewrite Summary

**auth-systems skill rewritten to v1.2 standard: Clerk quick-start, numbered sections, side-by-side Clerk/Better Auth middleware comparison, full Better Auth reference replacing Auth.js, and CVE-2025-29927 DAL pattern documentation**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-24T03:42:39Z
- **Completed:** 2026-02-24T03:45:56Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Rewrote `SKILL.md` (437 lines, under 500 limit) with Clerk quick-start, numbered sections 1-4, side-by-side middleware comparison (Clerk `clerkMiddleware` vs Better Auth `getSessionCookie`), session access patterns for server components/actions/API routes, Clerk webhook handler with svix verification, and Gotchas section with CVE-2025-29927 and DAL pattern
- Created `better-auth-patterns.md` (297 lines) as a complete Better Auth reference covering setup, middleware (fast and full paths), session access, OAuth provider setup (GitHub + Google), client-side usage, and failure modes
- Upgraded `clerk-patterns.md` with DAL pattern using `cache()`, version context table (noting `authMiddleware` removal in 6.x), and failure modes table
- Stubbed `authjs-patterns.md` with deprecation notice pointing to `better-auth-patterns.md`

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite SKILL.md with quick-start, numbered sections, and side-by-side Clerk/Better Auth comparison** - `8eda340` (feat)
2. **Task 2: Create better-auth-patterns.md and upgrade clerk-patterns.md** - `548b247` (feat)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `.agent/skills/auth-systems/SKILL.md` - Rewritten: quick-start, sections 1-4, side-by-side patterns, DAL/CVE-2025-29927 gotchas
- `.agent/skills/auth-systems/references/better-auth-patterns.md` - Created: full Better Auth reference
- `.agent/skills/auth-systems/references/clerk-patterns.md` - Upgraded: DAL pattern, version context, failure modes
- `.agent/skills/auth-systems/references/authjs-patterns.md` - Replaced with deprecation stub

## Decisions Made

- **Better Auth as self-hosted path:** Auth.js/NextAuth is maintenance-mode since Sept 2025; Better Auth is the active successor. `authjs-patterns.md` replaced with deprecation stub.
- **Better Auth middleware approach:** `getSessionCookie()` (Approach A, cookie check only) recommended as default for middleware; `auth.api.getSession()` (Approach B, full DB fetch) reserved for when middleware needs user data.
- **CVE-2025-29927 framing:** Documented as a Next.js App Router framework-level pitfall, not a Clerk-specific issue — applies equally to Better Auth users. Requires Next.js 15.2.3+.
- **authjs-patterns.md deprecation:** File retained as a stub with redirect rather than deleted — preserves git history and prevents broken references in older context.

## Deviations from Plan

None — plan executed exactly as written. All `must_haves` truths and artifacts satisfied.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. Skill is documentation only.

## Next Phase Readiness

- auth-systems skill is shippable: developer can implement Clerk or Better Auth in a Next.js App Router app without external docs
- Dependency chain ready: `auth-systems` skill is the prerequisite for `stripe-payments` (Phase 14)
- No blockers

---

_Phase: 11-foundation-skills_
_Completed: 2026-02-24_
