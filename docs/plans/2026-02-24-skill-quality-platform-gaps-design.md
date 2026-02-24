# Design: Skill Quality System & Platform Gap Skills

**Date:** 2026-02-24
**Status:** Validated
**Milestone scope:** v1.2 (Quality Foundation) + v1.3 (Platform Gaps + Deepening Pass)

---

## Problem Statement

Two compounding issues limit Viflo's real-world value:

1. **Platform gaps** — Missing skill domains that real projects repeatedly need (multi-tenancy, billing, real-time, background jobs)
2. **Skill shallowness** — Existing skills are present but too abstract to be immediately useful

The shallowness problem manifests in four failure modes:

| Failure Mode | Description |
|---|---|
| **Abstraction Trap** | Principles without concrete code — "draw the rest of the owl" |
| **Happy Path Bias** | Ignores race conditions, error states, and edge cases |
| **Analysis Paralysis** | Lists options without trade-off reasoning to choose between them |
| **Technical Rot** | Correct patterns tied to deprecated APIs or old library versions |

---

## Design

### Milestone Split Rationale

**Stop the bleeding before mopping the floor.** Creating more shallow skills while the system that produces them is unchanged just increases the cleanup backlog. The fix: establish the quality system in v1.2 so every new skill is built to standard from day one, then use it to audit and deepen the existing library in v1.3.

---

### v1.2 — Skills Expansion + Quality Foundation

**Deliverable 1: `skill-depth-standard` meta-skill**

A new skill at `.agent/skills/skill-depth-standard/` containing:
- Definitions of the four failure modes
- A self-evaluation checklist agents can run against any skill
- A Gap Report template for systematic audits

This becomes the system prompt for automated audits in v1.3.

**Deliverable 2: Updated `SKILL.md` template**

Four new mandatory sections added to the standard template:

| Section | Purpose |
|---|---|
| `## Implementation Patterns` | Working code, not prose |
| `## Failure Modes & Edge Cases` | What breaks, race conditions, null/edge inputs |
| `## Decision Matrix` | When to use X vs Y with explicit trade-off reasoning |
| `## Version Context` | Last verified library versions, known breaking changes |

**Deliverable 3: Auth as the Reference Skill**

The Auth skill (Clerk + Auth.js/NextAuth) is built first, explicitly to the new template. It serves as:
- The stress-test for the meta-skill and template (complex domain: OAuth flows, session handling, edge cases)
- The `SKILL.md` exemplar for contributors
- The benchmark when the v1.3 audit runs

The remaining four v1.2 skills (Stripe, RAG, Agent Architecture, Prompt Engineering) follow the Auth reference implementation.

---

### v1.3 — Platform Gaps + Deepening Pass

**New Skill 1: `multi-tenancy-billing`**

Full lifecycle of SaaS org isolation and monetization:
- Workspace/org data isolation patterns with decision matrix (row-level security vs. schema-per-tenant vs. database-per-tenant)
- Seat-based and usage-metered billing with Stripe
- Upgrade/downgrade flows with prorated amounts
- Plan enforcement middleware
- Edge cases: concurrent seat limit enforcement, billing state divergence between Stripe and DB, trial-to-paid conversion

**New Skill 2: `realtime-background-jobs`**

Two sub-domains packaged together (often solved simultaneously in real apps):

*Real-time:*
- WebSocket lifecycle management
- SSE as a simpler alternative (with decision matrix vs. WebSockets)
- Presence and broadcast patterns
- Reconnection handling

*Background jobs:*
- Queue selection guide: BullMQ (self-hosted) vs. Inngest/Trigger.dev (managed) — with trade-off matrix
- Job retry strategies
- Idempotency patterns
- Failure handling when a job dies mid-execution

**Deepening Pass**

- AI audit using `skill-depth-standard` generates a Gap Report across all 35 existing skills
- Top 10 by usage/impact identified for targeted depth sprint
- Each receives missing decision matrices, failure mode coverage, and version context

---

## Proposed Phase Sequence

| Phase | Milestone | Action | Output |
|---|---|---|---|
| 1 | v1.2 | Create `skill-depth-standard` meta-skill | Rubric + audit template |
| 2 | v1.2 | Update `SKILL.md` template | New mandatory sections |
| 3 | v1.2 | Build Auth skill (reference) | Gold standard exemplar |
| 4 | v1.2 | Build Stripe, RAG, Agent Arch, Prompt Eng | 4 deep skills |
| 5 | v1.3 | AI audit → Gap Report | Prioritized deepening list |
| 6 | v1.3 | Build `multi-tenancy-billing` skill | New platform skill |
| 7 | v1.3 | Build `realtime-background-jobs` skill | New platform skill |
| 8 | v1.3 | Deepen top 10 existing skills | Elevated library quality |
