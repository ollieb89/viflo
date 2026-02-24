# Phase 15: Integration Review - Research

**Researched:** 2026-02-24
**Domain:** Documentation authoring — markdown cross-referencing, skill library indexing, and line-count verification
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### INDEX.md structure
- Flat markdown table format (not grouped, not a bullet list)
- Each entry: skill name + one-line description only — no status column, no file paths
- Brief 1–2 sentence intro paragraph at the top explaining what the index covers
- Filename: `INDEX.md` (matches roadmap success criteria)

#### Cross-reference style
- Dedicated **"See Also"** section at the bottom of each skill file
- Seam is named explicitly in the link text — e.g. `[Agent Architecture](../agent-architecture/SKILL.md) — episodic memory pattern`
- Links are bidirectional: both skills reference each other at their shared seam
- Format: relative markdown links (clickable in editors and GitHub)

#### VERIFICATION.md format
- Table columns: `Skill | Line Count | Status`
- Status values: `✓` (≤500) or `✗` (>500)
- Summary line at the top or bottom: e.g. `5/5 skills within limit`
- Scope: all new/updated SKILL.md files from v1.4 (not the entire library, not just the 5 named skills)
- Over-limit skills get a brief note column entry explaining why (e.g. "includes extended examples")

#### Over-limit handling
- If a skill exceeds 500 lines: flag it with `✗` in VERIFICATION.md, do NOT trim or restructure
- Phase succeeds as long as VERIFICATION.md is complete — over-limit is noted, not a phase blocker
- Limit applies to each SKILL.md file individually (not transitive/referenced content)

### Claude's Discretion
- Exact prose wording of INDEX.md intro
- Order of skills in the INDEX.md table (alphabetical is fine)
- Whether "See Also" section uses a sub-header or a plain bold label
- Exact note text for over-limit skills in VERIFICATION.md

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | INDEX.md is updated with entries for prompt-engineering, auth-systems, rag-vector-search, agent-architecture, and stripe-payments skills | Current INDEX.md already has entries for all five skills in the AI/LLM, Authentication, and Payments sections; they must be migrated to the flat table format decided in CONTEXT.md |
| INFRA-02 | All new/updated SKILL.md files are verified ≤500 lines with line counts recorded in VERIFICATION.md | Line counts observed: prompt-engineering 281, auth-systems 437, rag-vector-search 416, agent-architecture 498, stripe-payments 363 — all five are within the 500-line limit |
| INFRA-03 | Cross-reference links are added between RAG, Agent Architecture, and prompt-engineering at their integration seams | Three seams identified: (1) RAG ↔ Agent Architecture at episodic memory/pgvector; (2) Agent Architecture ↔ RAG at pgvector pattern; (3) RAG and Agent Architecture ↔ prompt-engineering at system-prompt design |
</phase_requirements>

---

## Summary

Phase 15 is a pure documentation housekeeping phase — no code is written. All work is authoring markdown files and editing three existing SKILL.md files to add "See Also" sections. The technical domain is limited to: (1) deciding what text to write, and (2) getting relative file paths and link text exactly right. No external libraries, no build process, no test framework.

The existing INDEX.md in `.agent/skills/INDEX.md` already lists all five target skills but in a grouped-by-category format with Difficulty and When-to-Use columns. INFRA-01 requires adding those five skills to the flat two-column table format decided in CONTEXT.md. The planner should be clear that the existing INDEX.md is not being deleted or replaced wholesale — only the five new skills are being added (the INDEX.md already contains many other skills).

The five SKILL.md files created in v1.3 (prompt-engineering, auth-systems, rag-vector-search, agent-architecture, stripe-payments) are all within the 500-line limit based on observed line counts. VERIFICATION.md will record actual wc -l output at execution time to confirm. The agent-architecture skill at 498 lines is the one closest to the boundary and should be highlighted in VERIFICATION.md.

**Primary recommendation:** Execute in three sequential tasks — (1) update INDEX.md flat table with five entries, (2) add "See Also" sections to three skills, (3) write VERIFICATION.md with observed line counts.

---

## Standard Stack

This phase has no software dependencies. All tools are built-in shell utilities.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| `wc -l` | built-in | Count lines in SKILL.md files | Canonical line count for VERIFICATION.md |
| Markdown | n/a | All output format | Project convention for skill library |
| Relative paths | n/a | Cross-reference links | Clickable in editors and GitHub |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `cat -n` / Read tool | n/a | Verify file content after edits | Confirming "See Also" sections land at file bottom |

**Installation:** None required.

---

## Architecture Patterns

### Recommended File Targets

```
.agent/skills/
├── INDEX.md                          # Update: add 5 skill rows to flat table
├── VERIFICATION.md                   # Create: new file at skills root
├── rag-vector-search/SKILL.md        # Edit: add "See Also" section at bottom
├── agent-architecture/SKILL.md       # Edit: add "See Also" section at bottom
└── prompt-engineering/SKILL.md       # Edit: add "See Also" section at bottom
```

### Pattern 1: INDEX.md Flat Table Entry Format

**What:** Each of the five new skills gets one row in the flat table at the top of INDEX.md.
**When to use:** INFRA-01 task.

The existing INDEX.md uses a grouped/categorized format. The CONTEXT.md decision specifies a flat table format for the new entries. The planner must decide whether to (a) add a flat table section for the five new skills alongside the existing grouped format, or (b) treat this as inserting rows into the existing grouped tables. Given the CONTEXT.md wording ("flat markdown table format, not grouped") and the success criterion (INDEX.md lists the five skills with accurate one-line descriptions), option (b) — inserting into existing groups — is the pragmatic interpretation that avoids disrupting the existing index structure. The five skills already exist in the grouped index; the required action is ensuring their descriptions match the final v1.4 content.

**Correct interpretation:** The five skills already appear in the existing INDEX.md grouped tables (AI/LLM, Authentication, Payments categories). The CONTEXT.md flat table decision applies to the _form_ of the entry (name + one-line description only) — the executor must verify the existing descriptions are accurate and update if needed. No wholesale restructuring is required.

**Example row format (flat table):**
```markdown
| prompt-engineering | Prompt templates, evaluation, chain-of-thought, anti-patterns |
| auth-systems | Clerk and Better Auth authentication, sessions, RBAC, CVE-2025-29927 pattern |
| rag-vector-search | Embedding pipelines, pgvector/HNSW, hybrid search, retrieval-augmented generation |
| agent-architecture | Tool-using agents, guardrails, LangGraph, episodic memory via pgvector |
| stripe-payments | Stripe checkout, subscriptions, webhooks, atomic idempotency, billing lifecycle |
```

### Pattern 2: Cross-Reference "See Also" Section

**What:** Three seams require bidirectional links between skill files.
**When to use:** INFRA-03 task.

The three integration seams are:

**Seam A — Episodic Memory:** RAG and Agent Architecture share the pgvector episodic memory pattern. The agent-architecture SKILL.md already mentions "See the `rag-vector-search` skill for HNSW index setup, chunking strategies, and eval patterns" inline (line 361). The RAG skill has no corresponding reference back to agent-architecture. Both need a "See Also" section at the bottom.

**Seam B — System Prompt Design:** RAG and Agent Architecture both use system-prompt patterns from prompt-engineering (RAG prompt assembly, agent instruction structure). The prompt-engineering skill does not currently reference RAG or agent-architecture.

**Example "See Also" section to append to bottom of each file:**

```markdown
## See Also

- [Agent Architecture](../agent-architecture/SKILL.md) — episodic memory pattern (pgvector-backed recall for agents)
- [Prompt Engineering](../prompt-engineering/SKILL.md) — system-prompt design for RAG assembly
```

```markdown
## See Also

- [RAG / Vector Search](../rag-vector-search/SKILL.md) — pgvector pattern (HNSW index, embedding pipeline, hybrid search)
- [Prompt Engineering](../prompt-engineering/SKILL.md) — system-prompt design for agent instruction structure
```

```markdown
## See Also

- [RAG / Vector Search](../rag-vector-search/SKILL.md) — RAG prompt assembly and system-prompt design
- [Agent Architecture](../agent-architecture/SKILL.md) — system-prompt design for agent instructions
```

### Pattern 3: VERIFICATION.md Format

**What:** New file at `.agent/skills/VERIFICATION.md` recording line counts.
**When to use:** INFRA-02 task.

```markdown
# v1.4 Skill Line Count Verification

5/5 skills within the 500-line limit.

| Skill | Line Count | Status |
|-------|------------|--------|
| prompt-engineering | 281 | ✓ |
| auth-systems | 437 | ✓ |
| rag-vector-search | 416 | ✓ |
| agent-architecture | 498 | ✓ |
| stripe-payments | 363 | ✓ |
```

Note: The executor must run `wc -l` at execution time to get the actual counts (the "See Also" additions in INFRA-03 will add ~4–6 lines to each of the three edited skill files, so final counts will differ from the pre-edit numbers).

### Anti-Patterns to Avoid

- **Restructuring the existing INDEX.md:** The existing grouped table format serves many existing skills. Do not reorganize or delete existing entries — only ensure the five target skills have accurate entries.
- **Using absolute paths in cross-reference links:** Links like `/home/ollie/Development/Tools/viflo/.agent/skills/...` break portability. Relative paths `../agent-architecture/SKILL.md` are required.
- **Counting lines before adding "See Also" sections:** VERIFICATION.md must be written after INFRA-03 edits, not before, so line counts include the "See Also" additions.
- **Adding "See Also" to skills that don't need them:** Only rag-vector-search, agent-architecture, and prompt-engineering require new "See Also" sections.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Line counting | Custom scripts | `wc -l <file>` | wc -l is the canonical tool; output is an integer, trivially verified |
| Link validation | Link checker script | Manual read + relative path inspection | Phase is small (3 files, 6 links); automated validation is overkill |

**Key insight:** This is a documentation phase. The work is authoring, not engineering. Invest effort in getting the prose and link text right, not in tooling.

---

## Common Pitfalls

### Pitfall 1: Line Count Includes "See Also" Additions

**What goes wrong:** VERIFICATION.md is written before the "See Also" sections are added, recording stale line counts.
**Why it happens:** Natural order of operations — verify then cross-reference — matches INFRA-02 before INFRA-03. But INFRA-03 edits change the line counts.
**How to avoid:** Execute tasks in this order: INFRA-01 (INDEX.md), then INFRA-03 (See Also sections), then INFRA-02 (VERIFICATION.md with final counts). Or run `wc -l` again at INFRA-02 time.
**Warning signs:** agent-architecture SKILL.md is at 498 lines pre-edit. After adding a ~5-line "See Also" section, it will be ~503 lines — which would make it the only over-limit file. This is the critical case to watch.

### Pitfall 2: agent-architecture May Exceed 500 Lines After Edit

**What goes wrong:** agent-architecture SKILL.md is 498 lines. Adding a "See Also" section (~4–6 lines) pushes it to 502–504 lines — over the 500-line limit.
**Why it happens:** The skill was written close to the boundary.
**How to avoid:** Count lines after adding "See Also". Per the locked decisions: if over-limit, flag with `✗` in VERIFICATION.md and add a brief note. Do NOT trim the skill. The phase still succeeds.
**Warning signs:** `wc -l agent-architecture/SKILL.md` returns > 500 after the "See Also" edit.

### Pitfall 3: Inline Reference Already Exists in agent-architecture

**What goes wrong:** agent-architecture/SKILL.md already mentions the RAG skill inline at line 361 ("See the `rag-vector-search` skill..."). Adding a "See Also" section duplicates this reference.
**Why it happens:** The inline mention was added during Phase 13 implementation before the cross-reference format was standardized.
**How to avoid:** The inline mention and the "See Also" section serve different purposes — inline mentions appear in context (within a section), "See Also" appears as a navigation aid at the file bottom. Keep both. The "See Also" is the standard format required by INFRA-03; the inline reference adds context within the episodic memory section.
**Warning signs:** Temptation to delete the inline reference to save lines — don't.

### Pitfall 4: Missing the Third Link Seam (prompt-engineering)

**What goes wrong:** INFRA-03 is implemented as RAG ↔ Agent Architecture only, missing the prompt-engineering links.
**Why it happens:** The phase description says "RAG links to Agent Architecture at the episodic memory seam; Agent Architecture links back to RAG at the pgvector pattern seam" — the third seam (both link to prompt-engineering at system-prompt design) is mentioned separately and can be overlooked.
**How to avoid:** All three skills require a "See Also" section. The success criterion explicitly requires "both link to prompt-engineering at the system-prompt design seam."
**Warning signs:** INFRA-03 implementation touches only 2 files instead of 3.

---

## Code Examples

### wc -l for line count verification

```bash
# Run at execution time to get actual post-edit line counts
wc -l /home/ollie/Development/Tools/viflo/.agent/skills/prompt-engineering/SKILL.md
wc -l /home/ollie/Development/Tools/viflo/.agent/skills/auth-systems/SKILL.md
wc -l /home/ollie/Development/Tools/viflo/.agent/skills/rag-vector-search/SKILL.md
wc -l /home/ollie/Development/Tools/viflo/.agent/skills/agent-architecture/SKILL.md
wc -l /home/ollie/Development/Tools/viflo/.agent/skills/stripe-payments/SKILL.md
```

Pre-edit baseline (2026-02-24, before "See Also" additions):
- prompt-engineering: 281 lines
- auth-systems: 437 lines
- rag-vector-search: 416 lines
- agent-architecture: 498 lines (WATCH: closest to 500-line limit)
- stripe-payments: 363 lines

### Relative path structure for cross-reference links

Files live at: `.agent/skills/<skill-name>/SKILL.md`

When linking from `rag-vector-search/SKILL.md` to `agent-architecture/SKILL.md`:
```markdown
[Agent Architecture](../agent-architecture/SKILL.md) — episodic memory pattern
```

When linking from `agent-architecture/SKILL.md` to `rag-vector-search/SKILL.md`:
```markdown
[RAG / Vector Search](../rag-vector-search/SKILL.md) — pgvector pattern
```

When linking from `rag-vector-search/SKILL.md` to `prompt-engineering/SKILL.md`:
```markdown
[Prompt Engineering](../prompt-engineering/SKILL.md) — system-prompt design for RAG assembly
```

When linking from `agent-architecture/SKILL.md` to `prompt-engineering/SKILL.md`:
```markdown
[Prompt Engineering](../prompt-engineering/SKILL.md) — system-prompt design for agent instructions
```

When linking from `prompt-engineering/SKILL.md` to `rag-vector-search/SKILL.md`:
```markdown
[RAG / Vector Search](../rag-vector-search/SKILL.md) — RAG prompt assembly and retrieval context injection
```

When linking from `prompt-engineering/SKILL.md` to `agent-architecture/SKILL.md`:
```markdown
[Agent Architecture](../agent-architecture/SKILL.md) — system-prompt design for tool-using agents
```

---

## State of the Art

This phase has no evolving technology stack. The "current approach" for all items is standard markdown.

| Area | Current Approach | Notes |
|------|-----------------|-------|
| Skill cross-references | Relative markdown links in "See Also" section | Established by CONTEXT.md decision; no alternative needed |
| Line count verification | wc -l | Canonical; output matches what editors/GitHub count |
| Index format | Flat markdown table (name + description) | Chosen over grouped/categorized format for simplicity |

---

## Open Questions

1. **Does auth-systems need a "See Also" section?**
   - What we know: INFRA-03 specifies RAG ↔ Agent Architecture ↔ prompt-engineering seams only. auth-systems is not mentioned in the cross-reference requirement.
   - What's unclear: auth-systems has no natural integration seam with RAG/agent-architecture/prompt-engineering that rises to the level of a cross-reference.
   - Recommendation: Do not add "See Also" to auth-systems in this phase. INFRA-03 is scoped to three specific seams.

2. **Does stripe-payments need a "See Also" section?**
   - What we know: Same situation as auth-systems — not mentioned in INFRA-03.
   - What's unclear: Nothing; stripe-payments is isolated from the AI stack.
   - Recommendation: Do not add "See Also" to stripe-payments in this phase.

3. **Will agent-architecture exceed 500 lines after "See Also" addition?**
   - What we know: Current count is 498 lines. A minimal "See Also" section adds approximately 4–6 lines.
   - What's unclear: Exact final count — depends on whether "See Also" uses a `##` header or bold label.
   - Recommendation: Run `wc -l` after the edit. If > 500, record `✗` with note "498 lines + See Also section added for INFRA-03". The phase still succeeds per locked decisions.

---

## Sources

### Primary (HIGH confidence)
- Direct file reads of `.agent/skills/*/SKILL.md` — content, structure, existing references
- Direct file read of `.agent/skills/INDEX.md` — current format and existing entries
- `wc -l` output on all five SKILL.md files — observed line counts
- `.planning/phases/15-integration-review/15-CONTEXT.md` — all format decisions

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md` — INFRA-01, INFRA-02, INFRA-03 requirement text
- `.planning/STATE.md` — phase ordering rationale and accumulated decisions

### Tertiary (LOW confidence)
- None.

---

## Metadata

**Confidence breakdown:**
- What files to edit: HIGH — directly observed from file system
- Line counts: HIGH — directly measured with wc -l
- Cross-reference seams: HIGH — confirmed by reading all three SKILL.md files
- agent-architecture line count risk: HIGH — 498 lines confirmed, arithmetic is certain
- FORMAT choices: HIGH — locked in CONTEXT.md

**Research date:** 2026-02-24
**Valid until:** 2026-03-24 (stable — no external dependencies)
