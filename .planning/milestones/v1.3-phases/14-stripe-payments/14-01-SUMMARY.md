---
phase: 14-stripe-payments
plan: "01"
subsystem: payments
tags: [stripe, typescript, nextjs, postgres, webhooks, subscriptions, checkout, pci]

# Dependency graph
requires: []
provides:
  - stripe-payments SKILL.md at auth-systems depth (363 lines)
  - Quick Start for one-time payments via Stripe Checkout
  - Raw-body webhook handler with atomic idempotency SQL
  - Subscription lifecycle for all four critical events
  - Customer Portal pattern with billingPortal.sessions.create()
  - Trial periods with trial_period_days
  - Five Gotchas in Symptom -> Cause -> Fix format
affects: [15-integration-review]

# Tech tracking
tech-stack:
  added: [stripe@20.3.1]
  patterns:
    - Stripe SDK initialized once in lib/stripe.ts — all route handlers import, never re-initialize
    - await req.text() as first operation in webhook handler before any other body access
    - Atomic idempotency via INSERT ... ON CONFLICT (stripe_event_id) DO NOTHING
    - Stripe status strings stored directly — no app-specific enum mapping
    - Customer ID always looked up from DB using authenticated user — never trust client-provided

key-files:
  created: []
  modified:
    - .agent/skills/stripe-payments/SKILL.md

key-decisions:
  - "Stripe Checkout (hosted page) as primary Quick Start path — SAQ A vs SAQ A-EP callout included"
  - "await req.text() as headline of webhook section — not a footnote"
  - "ON CONFLICT (stripe_event_id) DO NOTHING in main body — atomic guard, not SELECT-then-INSERT"
  - "Stripe status strings stored directly — no app-specific enum mapping (e.g., sub.status directly into DB)"
  - "Smart Retries for failed payment recovery — no custom dunning logic"
  - "API version updated to 2026-01-28.clover (stripe@20.3.1)"

patterns-established:
  - "Raw body extraction: await req.text() must be the absolute first line of any Stripe webhook handler"
  - "Atomic idempotency: INSERT ON CONFLICT at DB level prevents race window from SELECT-then-INSERT"
  - "Auth-before-portal: always authenticate and DB-lookup customerId — never accept from request body"

requirements-completed: [STRIPE-01, STRIPE-02, STRIPE-03, STRIPE-04, STRIPE-05]

# Metrics
duration: 2min
completed: 2026-02-24
---

# Phase 14 Plan 01: Stripe Payments Summary

**Stripe Checkout, raw-body webhooks with atomic SQL idempotency, four-event subscription lifecycle, Customer Portal, trial periods, and five Gotchas — 363-line SKILL.md at auth-systems depth**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-24T08:21:17Z
- **Completed:** 2026-02-24T08:22:54Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Rewrote SKILL.md from 91 lines to 363 lines (INFRA-02 compliant, 350-500 range)
- All five requirements delivered: Quick Start (STRIPE-01), webhooks + idempotency (STRIPE-02), subscription lifecycle (STRIPE-03), Gotchas (STRIPE-04), Customer Portal + trials (STRIPE-05)
- Updated API version from stale 2025-01-27.acacia to 2026-01-28.clover and SDK from 17.x to 20.3.1

## Task Commits

1. **Task 1: Rewrite SKILL.md to auth-systems depth** - `660a372` (feat)

**Plan metadata:** (see final commit below)

## Verification Results

All automated checks passed:

| Check | Result |
|---|---|
| Line count | PASS: 363 lines (350-500 range) |
| `await req.text()` | 3 occurrences |
| `ON CONFLICT (stripe_event_id) DO NOTHING` | 2 occurrences |
| `invoice.payment_failed` | 3 occurrences |
| `billingPortal.sessions.create` | 1 occurrence |
| `trial_period_days` | 2 occurrences |
| PCI | 2 occurrences |
| `2026-01-28` | 2 occurrences |
| `Quick Start` | 1 occurrence |

## Files Created/Modified

- `.agent/skills/stripe-payments/SKILL.md` - Complete rewrite: Quick Start, Webhooks, Subscription Lifecycle, Customer Portal, Trial Periods, Gotchas, Version Context

## Decisions Made

- Used raw `pg.Pool` for idempotency SQL examples — matches plan requirement to show `INSERT ... ON CONFLICT` in main body without Prisma abstraction hiding the SQL
- Inlined subscription lifecycle events in the webhook handler code block for a single complete example, with a summary table below
- Kept five Gotchas as terse three-liners with no narrative prose, using `---` dividers for visual separation without horizontal rules between every section

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required (skill documentation only).

## Next Phase Readiness

- Phase 14 Plan 01 complete — all STRIPE-01 through STRIPE-05 requirements addressed
- Phase 15 (Integration Review) can now reference stripe-payments SKILL.md for INDEX.md and cross-reference updates
- No blockers

---
*Phase: 14-stripe-payments*
*Completed: 2026-02-24*
