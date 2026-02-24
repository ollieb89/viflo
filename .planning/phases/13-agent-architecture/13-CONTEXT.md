# Phase 13: Agent Architecture - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Create a developer skill document (SKILL.md) covering Claude agent patterns — tool use with guardrails, streaming output to a browser, and when agents are the wrong choice. This phase produces the Agent Architecture skill; it does not build agent infrastructure or a production agent system.

</domain>

<decisions>
## Implementation Decisions

### Quick Start structure
- Step 1 delivers a running agent that responds to a prompt (no tools yet) — simplest possible working state
- By the end of the Quick Start section, the developer has a tool-using agent with a hard `MAX_TURNS` guardrail wired in
- Guardrail constants (`MAX_TURNS`, `MAX_TOKENS_PER_RUN`) are present in every code example from the first tool example onward — no example ships without them
- Quick Start tool example: web search / fetch URL — demonstrates real agent value (accessing external data)

### Code example language
- Python and TypeScript side-by-side throughout the skill doc (tab-switcher or paired blocks)
- Both languages must be complete and equivalent — not one leading and the other as a port

### Gotchas section coverage
- All 3 required pitfalls get full depth: warning signs, why it happens, and how to fix it
  1. Runaway costs — agent loops without termination
  2. Untyped sub-agent handoffs — data contract failures between agents
  3. Bag-of-agents error multiplication — errors compound across agent chains
- Each pitfall includes code: anti-pattern side-by-side with the corrected version
- Tone: direct and opinionated — "Don't do this" framing, not "here's a tradeoff"

### When NOT to use agents
- A visually distinct callout box at the top of the gotchas section (or its own section)
- Brief explanation of the criteria, not a full decision tree
- Gives the developer enough to make an informed build-vs-agent decision without prescribing all cases

### Claude's Discretion
- Exact visual structure of the tab-switcher / code pairing (inline, fenced blocks, MDX tabs, etc.)
- Streaming section implementation detail — FastAPI + Next.js is the specified stack but the depth of frontend wiring within scope is Claude's call
- Number of additional gotchas beyond the required 3 (more are fine if they're real)
- Exact formatting of the "When NOT to use agents" callout

</decisions>

<specifics>
## Specific Ideas

- The Quick Start 15-minute target is a success criterion — examples must be concise enough to achieve this
- `MAX_TURNS` and `MAX_TOKENS_PER_RUN` as named constants (not magic numbers inline) — the requirement calls them out explicitly
- Streaming: SSE from FastAPI `StreamingResponse` → Next.js client via Vercel AI SDK v6 — this specific stack is locked by the success criteria

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 13-agent-architecture*
*Context gathered: 2026-02-24*
