# Phase 11: Foundation Skills - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Two complete, shippable skills are published — Prompt Engineering and Auth Systems. Developers can follow either skill without needing any other v1.2 skill. Creating posts, AI/LLM patterns, and payments are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Skill structure & navigation

- Open with a quick start first — minimal working example developers can copy, then build depth
- File/split decision is Claude's discretion based on final content size
- Numbered sections (1. Setup, 2. Config, 3. Patterns) for clear tutorial progression
- Dedicated named **Gotchas / Pitfalls** section (not inline warnings) — AUTH-05 cache pitfall and PROMPT-04 anti-patterns land here

### Clerk vs Better Auth treatment

- Clerk is the primary path; Better Auth is framed as the self-hosted alternative
- Side-by-side comparison for the protected-route/middleware pattern — show the Clerk version, then the Better Auth equivalent
- Clerk webhook lifecycle sync only (AUTH-06) — Better Auth users manage their own DB so no equivalent webhook section needed
- App Router cache pitfall (AUTH-05) documented once at the framework level — it's a Next.js App Router issue, not Clerk-specific

### Code example depth

- Copy-paste ready — full working files where possible; developer should be able to drop in with minimal adjustment
- Full TypeScript with proper type annotations throughout (target stack is Next.js App Router + TypeScript)
- Prompt engineering examples use real Claude TypeScript SDK calls with real model IDs — not pseudocode
- Anti-pattern examples (PROMPT-04) use Before/After format: bad code block followed by corrected version

### Prompt golden set & evaluation

- Golden set: a folder of `.md` test case files (input prompt + expected output criteria) + a TypeScript script that calls Claude and compares results. Developer runs: `npx ts-node eval.ts` and sees pass/fail
- Prompt versioning: Git-tracked files — each prompt variant is a file, git history is the version history. The skill explains: version prompts like code
- `applies-to:` and `last-verified-against:` frontmatter: defined schema with valid values (e.g. `applies-to: [claude-opus-4-6, claude-sonnet-4-6]`, `last-verified-against: claude-sonnet-4-6`)
- Golden set includes one example per pattern — three total: chain-of-thought, few-shot, and output format specification

### Claude's Discretion

- Whether to split auth skill into one file or two (clerk.md + better-auth.md) based on final content size
- Exact number of anti-patterns in the PROMPT-04 catalogue (requirements say top 5)
- Spacing, typography, and exact prose style within sections

</decisions>

<specifics>
## Specific Ideas

No specific references or "I want it like X" moments captured — open to standard approaches within the decisions above.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

_Phase: 11-foundation-skills_
_Context gathered: 2026-02-24_
