---
phase: 13-agent-architecture
plan: "01"
subsystem: agent-skills
tags:
  [
    agent-architecture,
    tool-use,
    langgraph,
    streaming,
    fastapi,
    sse,
    pgvector,
    mcp,
    anthropic-sdk,
  ]

requires:
  - phase: 12-rag-vector-search
    provides: pgvector episodic memory patterns, HNSW index setup, embedding_model_version column convention
provides:
  - agent-architecture-skill
  - tool-use-loop-with-guardrails
  - fastapi-sse-streaming-pattern
  - langgraph-create-react-agent-pattern
  - episodic-memory-pgvector-pattern
  - mcp-overview
affects:
  - phase-15-integration-review

tech-stack:
  added:
    [
      anthropic-sdk-0.37,
      anthropic-python-0.40,
      fastapi-0.115,
      langgraph-1.x,
      langgraph-checkpoint-postgres,
      langchain-anthropic,
      ai-sdk-6,
      ai-sdk-anthropic,
      ai-sdk-react,
    ]
  patterns:
    [
      manual-tool-use-loop,
      max-turns-guardrail,
      fastapi-sse-streaming,
      langgraph-react-agent,
      episodic-memory-pgvector,
    ]

key-files:
  created: []
  modified:
    - .agent/skills/agent-architecture/SKILL.md

key-decisions:
  - "Manual tool-use loop over tool_runner() shortcut — guardrail placement is explicit and auditable; shortcut mentioned as callout only"
  - "Python primary for LangGraph — TypeScript SDK (@langchain/langgraph) noted but not covered"
  - "Next.js API route proxy pattern for streaming — avoids CORS, keeps API key server-side, simpler than direct FastAPI-to-useChat bridge"
  - "MAX_TURNS and MAX_TOKENS_PER_RUN as named constants in every tool-use example — no magic numbers, grep-able"
  - "InMemorySaver for dev only, PostgresSaver for production — distinction called out explicitly in LangGraph section"
  - "embedding_model_version column mandatory in episodic memory schema — cross-referenced to RAG skill pattern"

patterns-established:
  - "MAX_TURNS / MAX_TOKENS_PER_RUN: required named constants in all agent loop examples"
  - "fetch_url as the canonical Quick Start tool — demonstrates real external data access"
  - "for turn in range(MAX_TURNS) / for (let turn = 0; turn < MAX_TURNS; turn++) — paired Python/TypeScript loop pattern"
  - "raise RuntimeError / throw new Error on MAX_TURNS breach — required error, not silent exit"

requirements-completed: [AGENT-01, AGENT-02, AGENT-03, AGENT-04, AGENT-05]

duration: 4min
completed: 2026-02-24
---

# Phase 13 Plan 01: Agent Architecture SKILL.md Rewrite Summary

**Tool-using Claude agent SKILL.md expanded from 81 to 498 lines: Quick Start with MAX_TURNS guardrails, FastAPI SSE streaming to Next.js AI SDK v6, LangGraph 1.x create_react_agent, episodic memory via pgvector, MCP overview, and 3 Gotchas with BAD/GOOD code pairs.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-24T07:21:02Z
- **Completed:** 2026-02-24T07:25:42Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Rewrote the 81-line thin-shell SKILL.md to 498 lines at auth-systems depth
- Promoted production-essential patterns from references/ files into the main document body
- Established MAX_TURNS and MAX_TOKENS_PER_RUN as required named constants across 14 and 11 occurrences respectively
- Added all 3 required Gotchas (Runaway Costs, Untyped Handoffs, Bag-of-Agents) with warning signs, why-it-happens, and BAD/GOOD code pairs
- Cross-referenced the rag-vector-search skill for episodic memory and HNSW index setup
- Included verbatim MCP overview paragraph from RESEARCH.md

## Verification Results

| Check                                | Expected | Result | Status |
| ------------------------------------ | -------- | ------ | ------ |
| Line count                           | 380–500  | 498    | PASS   |
| MAX_TURNS occurrences                | ≥3       | 14     | PASS   |
| MAX_TOKENS_PER_RUN occurrences       | ≥2       | 11     | PASS   |
| StreamingResponse occurrences        | ≥1       | 4      | PASS   |
| "LangGraph 1" occurrences            | ≥1       | 1      | PASS   |
| "Model Context Protocol" occurrences | ≥1       | 1      | PASS   |
| "rag-vector-search" cross-reference  | ≥1       | 1      | PASS   |
| Runaway/runaway occurrences          | ≥1       | 4      | PASS   |
| Untyped/untyped occurrences          | ≥1       | 2      | PASS   |
| Bag-of-Agents occurrences            | ≥1       | 2      | PASS   |

## Task Commits

1. **Task 1: Rewrite SKILL.md to auth-systems depth** — `adecdf7` (feat)

**Plan metadata:** (docs commit to follow)

## Files Created/Modified

- `.agent/skills/agent-architecture/SKILL.md` — Expanded from 81 to 498 lines; complete agent-architecture skill at auth-systems depth

## Decisions Made

- **Manual loop over tool_runner():** The manual tool-use loop (`for turn in range(MAX_TURNS)`) is the teaching pattern because it makes guardrail placement explicit. `tool_runner()` is mentioned as a shortcut callout only.
- **Python primary for LangGraph:** `@langchain/langgraph` exists but TypeScript LangGraph parity is unclear for `create_react_agent` + `PostgresSaver` in 1.x — Python only, with a note.
- **Next.js proxy pattern for streaming:** Direct FastAPI-to-useChat wiring requires AI SDK-compatible SSE format (not raw Anthropic SSE). The Next.js API route proxy is simpler and keeps API key server-side.
- **LangGraph version cited as "1.x (stable since October 2025)":** Not a specific patch version — avoids stale version pins while communicating stability guarantee.

## Deviations from Plan

None — plan executed exactly as written. Line count required 3 trim passes to reach 498 (from initial 550), all prose/whitespace reductions with no content removed.

## Issues Encountered

Initial write produced 550 lines (50 over the ≤500 limit). Applied targeted prose tightening and whitespace reduction across 7 edits to reach 498 lines. All required content, code, and structure preserved throughout.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Agent Architecture skill complete and cross-referenced to rag-vector-search
- Phase 15 (Integration Review) can now reference this skill for INDEX.md descriptions and cross-ref links
- references/multi-agent-patterns.md and references/memory-orchestration.md remain as deeper references (unchanged — out of scope for this plan)

---

_Phase: 13-agent-architecture_
_Completed: 2026-02-24_
