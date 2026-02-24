---
phase: 11-foundation-skills
verified: 2026-02-24T06:00:00Z
status: human_needed
score: 5/5 truths verified
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  gaps_closed:
    - "Structured output pattern code in SKILL.md and anti-patterns.md now uses correct Anthropic SDK API surface (output_config: { format: zodOutputFormat(...) } and response.parsed_output)"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Run eval.ts against all three golden-set test cases"
    expected: "All three pass: chain-of-thought PASS, few-shot PASS, output-format-specification PASS"
    why_human: "Requires ANTHROPIC_API_KEY in environment and actual Claude API calls — cannot verify programmatically in this context. The eval runner logic is sound (LLM-as-judge, exit code 1 on failure) but actual pass/fail depends on live API responses."
  - test: "Copy the Clerk Quick Start block into a fresh Next.js App Router project and verify sign-in redirect works"
    expected: "Navigating to /dashboard while unauthenticated redirects to /sign-in"
    why_human: "Full-stack runtime behavior — middleware execution requires a running Next.js process"
  - test: "Copy the Better Auth middleware (Approach A) and verify cookie check correctly protects /dashboard"
    expected: "Unauthenticated request to /dashboard redirects to /sign-in; authenticated request passes through"
    why_human: "Requires a running Next.js process and a Better Auth session cookie"
---

# Phase 11: Foundation Skills Verification Report

**Phase Goal:** Two complete, shippable skills are published — developers can follow structured guidance for Prompt Engineering and Auth Systems without needing any other v1.2 skill to be complete.
**Verified:** 2026-02-24T06:00:00Z
**Status:** human_needed
**Re-verification:** Yes — after gap closure

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Developer can write a structured prompt using role/context/task/output anatomy with model-appropriate technique selection (instruction-tuned vs reasoning models tagged in frontmatter) | VERIFIED | `buildPrompt()` function present in SKILL.md section 2 with full TypeScript interface; `applies-to` schema documented and applied to all 3 patterns (9 occurrences of `applies-to` in SKILL.md); model selection table distinguishes claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001 with reasoning model notes |
| 2 | Developer can apply chain-of-thought, few-shot, and output format specification patterns and evaluate them against a golden set without an external platform | VERIFIED | All three patterns now use correct Anthropic SDK calls. SKILL.md lines 244/247 and anti-patterns.md lines 111/114 fixed: `output_config: { format: zodOutputFormat(...) }` and `response.parsed_output`. No occurrences of `response_format:`, `choices[0]`, or `message.parsed` remain in either file. |
| 3 | Developer can follow the Clerk quick-start to add sign-up, sign-in, and protected routes to a Next.js App Router app | VERIFIED | Quick Start in auth SKILL.md contains complete copy-paste block: npm install, env vars, ClerkProvider layout wrapper, and full clerkMiddleware with createRouteMatcher. All three elements present. clerk-patterns.md provides full reference implementation. |
| 4 | Developer can configure Better Auth as a self-hosted alternative with the same protected-route pattern and OAuth provider wiring (GitHub, Google) | VERIFIED | SKILL.md section 1 has full Better Auth setup (betterAuth config, route handler, migration commands). Section 2 shows side-by-side middleware (Clerk clerkMiddleware then Better Auth getSessionCookie). OAuth provider setup for GitHub and Google documented for both providers. better-auth-patterns.md provides complete reference. authjs-patterns.md properly deprecated with stub. |
| 5 | Skill documents the App Router cache pitfall and DAL re-validation pattern, and covers the Clerk webhook receiver for user lifecycle sync | VERIFIED | SKILL.md section 4 gotcha #1 documents CVE-2025-29927 with Next.js 15.2.3+ requirement. Full DAL pattern with `import { cache } from 'react'` present (line 394). Clerk webhook handler covers user.created, user.updated, user.deleted with full svix signature verification and svix-id idempotency check. clerk-patterns.md contains the same webhook handler independently. |

**Score:** 5/5 truths verified

---

## Required Artifacts

### Prompt Engineering Skill (Plan 01)

| Artifact | Min Lines | Actual Lines | Status | Details |
|----------|-----------|--------------|--------|---------|
| `.agent/skills/prompt-engineering/SKILL.md` | 80 | 281 | VERIFIED | Quick Start present; sections 1-4; 3 applies-to blocks (one per pattern); 7 real SDK calls; links to anti-patterns.md and evaluation-workflows.md in header callout; structured output pattern now uses correct output_config/parsed_output API |
| `.agent/skills/prompt-engineering/references/anti-patterns.md` | 80 | 197 | VERIFIED | 5 anti-patterns present with 10 BEFORE/AFTER code blocks. Anti-pattern #3 AFTER block fixed: now uses output_config: { format: zodOutputFormat(...) } and response.parsed_output |
| `.agent/skills/prompt-engineering/references/evaluation-workflows.md` | 50 | 212 | VERIFIED | Golden set architecture, test case format, running instructions, prompt versioning, scoring rubric all present |
| `.agent/skills/prompt-engineering/references/golden-set/eval.ts` | 40 | 131 | VERIFIED | Full TypeScript eval runner: parseTestCase, runTestCase, LLM-as-judge (claude-haiku-4-5-20251001), exit code 1 on failure, main() function |
| `.agent/skills/prompt-engineering/references/golden-set/chain-of-thought.md` | — | 22 | VERIFIED | applies-to + last-verified-against frontmatter, Input Prompt section, 5 Expected Output Criteria bullets |
| `.agent/skills/prompt-engineering/references/golden-set/few-shot.md` | — | 28 | VERIFIED | applies-to + last-verified-against frontmatter, Input Prompt with 2 example pairs + real user, 5 Expected Output Criteria bullets |
| `.agent/skills/prompt-engineering/references/golden-set/output-format.md` | — | 27 | VERIFIED | applies-to + last-verified-against frontmatter, Input Prompt, 7 Expected Output Criteria bullets |

### Auth Systems Skill (Plan 02)

| Artifact | Min Lines | Actual Lines | Status | Details |
|----------|-----------|--------------|--------|---------|
| `.agent/skills/auth-systems/SKILL.md` | 100 | 437 | VERIFIED | Quick Start (Clerk); sections 1-4; side-by-side middleware (Clerk + Better Auth); session access for server components/actions/routes (both providers); webhook handler; CVE-2025-29927 gotcha with DAL pattern |
| `.agent/skills/auth-systems/references/clerk-patterns.md` | 80 | 231 | VERIFIED | Version context table; middleware; session access (server component, server action, API route); DAL pattern with cache(); webhook handler with svix + idempotency; failure modes |
| `.agent/skills/auth-systems/references/better-auth-patterns.md` | 80 | 297 | VERIFIED | Full Better Auth reference: setup, lib/auth.ts config, auth-client.ts, route handler, migration; middleware (fast + full paths); session access (3 contexts); DAL pattern; OAuth (GitHub + Google); client-side usage; version context; failure modes |
| `.agent/skills/auth-systems/references/authjs-patterns.md` | — | 5 | VERIFIED | Deprecated stub — redirects to better-auth-patterns.md |

---

## Key Link Verification

### Prompt Engineering (Plan 01 key_links)

| From | To | Via | Status | Evidence |
|------|----|-----|--------|----------|
| `SKILL.md` | `anti-patterns.md` | header callout | WIRED | Line 8: `> See references/anti-patterns.md` |
| `SKILL.md` | `evaluation-workflows.md` | header callout | WIRED | Line 8: `> See references/evaluation-workflows.md` |
| `evaluation-workflows.md` | `golden-set/eval.ts` | npx ts-node documented | WIRED | Lines 21 and 84: `npx ts-node eval.ts` with directory path |

### Auth Systems (Plan 02 key_links)

| From | To | Via | Status | Evidence |
|------|----|-----|--------|----------|
| `SKILL.md` | `clerk-patterns.md` | header callout | WIRED | Line 8: `> See references/clerk-patterns.md` |
| `SKILL.md` | `better-auth-patterns.md` | header callout | WIRED | Line 8: `> See references/better-auth-patterns.md` |
| `SKILL.md` | `clerkMiddleware` | middleware code block | WIRED | Lines 41, 49, 167, 175 |
| `SKILL.md` | `getSessionCookie` | Better Auth middleware block | WIRED | Lines 193, 201, 204 |
| `SKILL.md` | `cache()` | DAL pattern in Gotchas | WIRED | Line 394: `import { cache } from 'react'` |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| PROMPT-01 | 11-01-PLAN | Structured prompts using role/context/task/output anatomy | SATISFIED | `buildPrompt()` function with full interface; demonstrated in SKILL.md section 2 |
| PROMPT-02 | 11-01-PLAN | Model-specific technique applicability with applies-to tags | SATISFIED | Schema documented in section 2; 9 applies-to occurrences in SKILL.md; all 3 pattern entries carry the schema; golden-set test cases carry the schema |
| PROMPT-03 | 11-01-PLAN | Chain-of-thought, few-shot, and output format specification patterns | SATISFIED | All three patterns present with correct Anthropic SDK calls. Structured output now uses output_config: { format: zodOutputFormat(...) } and response.parsed_output — matches 11-RESEARCH.md API documentation |
| PROMPT-04 | 11-01-PLAN | Anti-pattern catalogue (top 5 output-degrading patterns) | SATISFIED | 5 anti-patterns present with Before/After format. Anti-pattern #3 AFTER block fixed to use correct output_config / response.parsed_output API surface |
| PROMPT-05 | 11-01-PLAN | Version and evaluate prompts using golden set (no external platform) | SATISFIED | eval.ts runner present (131 lines, substantive, LLM-as-judge architecture); 3 golden-set .md test cases; evaluation-workflows.md documents running instructions |
| AUTH-01 | 11-02-PLAN | Clerk quick-start for Next.js App Router (sign-up, sign-in, protected routes) | SATISFIED | Full Quick Start with ClerkProvider, env vars, middleware.ts present; copy-paste ready |
| AUTH-02 | 11-02-PLAN | Better Auth as self-hosted alternative with same protected-route pattern | SATISFIED | Complete Better Auth setup in SKILL.md section 1; side-by-side middleware in section 2; better-auth-patterns.md is comprehensive |
| AUTH-03 | 11-02-PLAN | Session data in server components, server actions, and API routes | SATISFIED | SKILL.md section 3 shows 6 code blocks (3 Clerk + 3 Better Auth) covering all three contexts |
| AUTH-04 | 11-02-PLAN | OAuth providers (GitHub, Google) through Clerk and Better Auth | SATISFIED | Clerk: Dashboard config documented; Better Auth: socialProviders config + OAuth app setup instructions for both providers |
| AUTH-05 | 11-02-PLAN | App Router cache pitfall and DAL re-validation pattern | SATISFIED | CVE-2025-29927 documented (3 occurrences); Next.js 15.2.3+ requirement stated; DAL pattern with cache() present in SKILL.md section 4 and clerk-patterns.md |
| AUTH-06 | 11-02-PLAN | Clerk webhook receiver for user lifecycle sync | SATISFIED | Full webhook handler in SKILL.md section 3 and clerk-patterns.md; covers user.created/updated/deleted; svix signature verification; svix-id idempotency check |

No orphaned requirements — all 11 requirement IDs appear in plan frontmatter and have corresponding implementation in the codebase.

---

## Anti-Patterns Found

No blocker anti-patterns remain. The four lines flagged in the initial verification (SKILL.md lines 244/247 and anti-patterns.md lines 111/114) have been corrected. Scan confirmed zero remaining occurrences of `response_format:`, `choices[0]`, or the OpenAI-style `message.parsed` access pattern across both files.

---

## Human Verification Required

### 1. Eval Runner End-to-End

**Test:** With `ANTHROPIC_API_KEY` set, run `cd .agent/skills/prompt-engineering/references/golden-set/ && npx ts-node eval.ts`
**Expected:** Three lines of output — chain-of-thought PASS, few-shot PASS, output-format-specification PASS — followed by `3/3 passed` and exit code 0
**Why human:** Requires live Claude API calls; cannot execute in static analysis context

### 2. Clerk Quick Start End-to-End

**Test:** Copy the Quick Start block from `.agent/skills/auth-systems/SKILL.md` into a fresh Next.js App Router project with valid Clerk API keys. Navigate to /dashboard without signing in.
**Expected:** Browser redirects to /sign-in
**Why human:** Requires a running Next.js process and valid Clerk credentials

### 3. Better Auth Middleware End-to-End

**Test:** Implement the Approach A middleware from `.agent/skills/auth-systems/SKILL.md` section 2 in a Next.js project with Better Auth configured. Make a request to /dashboard without a session cookie.
**Expected:** Request redirects to /sign-in
**Why human:** Requires a running Next.js process with a configured Better Auth database

---

## Re-verification Summary

**Gap closed:** The single blocker from the initial verification is resolved. Both affected files now use the correct Anthropic SDK structured output API surface:

- `.agent/skills/prompt-engineering/SKILL.md` lines 244/247: `output_config: { format: zodOutputFormat(SentimentSchema, 'sentiment') }` and `response.parsed_output`
- `.agent/skills/prompt-engineering/references/anti-patterns.md` lines 111/114: same corrections

A grep scan confirms zero remaining occurrences of the wrong pattern (`response_format:`, `choices[0].message.parsed`) across both files.

**No regressions:** All 8 artifacts retain identical line counts to the initial verification. All 5 key links remain wired. All 11 requirements remain satisfied.

**Remaining items:** Three human-verification tests remain (eval runner live API test, Clerk end-to-end, Better Auth end-to-end). These were present in the initial verification and are unchanged — they require a live environment and are not blockers to shipping the skills as reference documentation.

---

*Verified: 2026-02-24T06:00:00Z*
*Verifier: Claude (gsd-verifier)*
