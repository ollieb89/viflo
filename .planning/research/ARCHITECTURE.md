# Architecture Research

**Domain:** Skill file integration — viflo v1.2 Skills Expansion
**Researched:** 2026-02-24
**Confidence:** HIGH (based on direct inspection of existing codebase)

## Standard Architecture

### Existing Skill System Overview

```
.agent/skills/
├── INDEX.md                        ← Central discovery file (MUST be updated)
├── <skill-name>/
│   ├── SKILL.md                    ← Required: YAML frontmatter + instructions (≤500 lines)
│   ├── references/                 ← Optional: Deep content loaded on demand
│   │   ├── guides/                 ← Detailed how-to content
│   │   └── <topic>.md              ← Domain-specific reference files
│   ├── assets/                     ← Optional: Templates/boilerplate (not loaded into context)
│   └── scripts/                    ← Optional: Executable helpers
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| SKILL.md frontmatter | Trigger matching — agent reads this to decide whether to load the skill | YAML with `name` and `description`; description doubles as "when to use" signal |
| SKILL.md body | Core instructions, quick-reference patterns, links to references | Markdown ≤500 lines; cross-references via skill name, not @ syntax |
| references/ | Detailed content loaded lazily when Claude determines it is needed | One file per sub-topic (e.g. `references/clerk-setup.md`, `references/webhook-patterns.md`) |
| assets/ | Boilerplate copied into user projects, not read into context | Templates, example configs, starter code |
| scripts/ | Deterministic helpers run without loading file contents into context | Python/Bash generators, validators |
| INDEX.md | Skill discovery — the top-level table of contents for all skills | Markdown tables by category; must be updated whenever a skill is added |

---

## Recommended Structure for Each New Skill

### Directory Layout

```
.agent/skills/
├── auth-systems/
│   ├── SKILL.md
│   └── references/
│       ├── clerk-setup.md          ← Clerk provider: install, env, middleware, protected routes
│       ├── nextauth-setup.md       ← Auth.js/NextAuth: config, providers, session, callbacks
│       └── oauth-patterns.md      ← OAuth flow diagrams, token refresh, PKCE
│
├── stripe-payments/
│   ├── SKILL.md
│   └── references/
│       ├── checkout-sessions.md    ← Stripe Checkout: one-time payments, redirect flow
│       ├── subscriptions.md        ← Products, prices, billing portal, proration
│       └── webhooks.md             ← Event handling, signature verification, idempotency keys
│
├── rag-vector-search/
│   ├── SKILL.md
│   └── references/
│       ├── embedding-pipelines.md  ← Chunking strategies, embedding models, batch upsert
│       ├── pgvector-setup.md       ← Extension install, vector columns, HNSW/IVFFlat indexes
│       └── retrieval-patterns.md   ← Similarity search, hybrid search, re-ranking
│
├── agent-architecture/
│   ├── SKILL.md
│   └── references/
│       ├── multi-agent-patterns.md ← Orchestrator/worker, handoffs, task routing
│       ├── memory-systems.md       ← Short-term (context), long-term (vector store), episodic
│       └── tool-use-patterns.md    ← Tool schemas, parallel calls, error recovery
│
└── prompt-engineering/
    ├── SKILL.md
    └── references/
        ├── template-patterns.md    ← System prompts, few-shot, chain-of-thought structures
        ├── evaluation-methods.md   ← Scoring rubrics, LLM-as-judge, regression suites
        └── anti-patterns.md        ← Known failure modes and their fixes
```

### Structure Rationale

- **Single SKILL.md per skill:** The existing convention is one SKILL.md per domain. No skill in the current library splits across multiple SKILL.md files. The 500-line limit is enforced by extracting detail into `references/`, not by creating sibling SKILL.md files.
- **Three references files per skill:** Each of the 5 new skills is complex enough to warrant 3 reference files (covering provider variants or major sub-topics). This matches how existing complex skills are structured (e.g. `database-design` has `postgresql-patterns.md`, `index-optimization.md`; `containerization` has 4 reference files).
- **No assets/ or scripts/ initially:** None of the 5 skills have obvious code generators or boilerplate templates that differ from what the frontend/backend skills already provide. Add these only when a concrete repeated task emerges.
- **Flat reference structure:** The skill-creator canon explicitly says "Avoid deeply nested references — keep references one level deep from SKILL.md." All 5 new skills follow this.

---

## Architectural Patterns

### Pattern 1: Progressive Disclosure

**What:** SKILL.md holds only the essentials (decision logic, selection guidance, quick-reference tables). Details live in `references/` and are loaded only when the specific sub-topic is needed.

**When to use:** Always. This is the viflo skill architecture invariant.

**Trade-offs:** Requires Claude to explicitly navigate to reference files; benefits are reduced context bloat for the common case.

**Example (auth-systems):**

```markdown
## Providers

| Provider | When to use |
|----------|-------------|
| Clerk    | Next.js App Router, managed auth, DX speed |
| Auth.js  | Self-hosted, custom providers, Pages Router |

For Clerk setup see [references/clerk-setup.md](references/clerk-setup.md).
For Auth.js/NextAuth setup see [references/nextauth-setup.md](references/nextauth-setup.md).
```

### Pattern 2: Cross-Skill References via Skill Name

**What:** When one skill depends on knowledge from another, reference by skill name in the SKILL.md body — not with an @ path (which force-loads the file).

**When to use:** Whenever a skill assumes prerequisite knowledge from another skill.

**Trade-offs:** Requires the agent to actively load the referenced skill; does not burn context if not needed.

**Example:**

```markdown
## Prerequisites

This skill assumes working knowledge of:
- `backend-dev-guidelines` — FastAPI endpoint structure
- `database-design` — SQLAlchemy models and migrations
```

### Pattern 3: Domain-Split References

**What:** When a skill covers multiple provider variants or sub-domains, split references into one file per variant so only the relevant file gets loaded.

**When to use:** Skills with mutually exclusive paths (auth providers, cloud targets, retrieval strategies).

**Trade-offs:** Requires an explicit selection decision in SKILL.md; pays off when variants diverge significantly.

**Example (rag-vector-search):**

```
references/
├── pgvector-setup.md       # Postgres-native vector storage
└── retrieval-patterns.md   # Querying patterns (shared)
```

When user chooses Pinecone, Claude reads `retrieval-patterns.md` only; when user sets up local pgvector, Claude reads `pgvector-setup.md` first.

---

## Data Flow

### Skill Selection Flow

```
User request
    ↓
Agent reads INDEX.md (passive — already in context)
    ↓
Agent reads SKILL.md frontmatter (description + triggers)
    ↓
Decision: skill applies?
    YES → Load SKILL.md body
    NO  → Skip
    ↓
SKILL.md body instructs which references/ to load
    ↓
Claude loads only the relevant reference file(s)
    ↓
Claude executes task with loaded context
```

### Cross-Reference Flow (for dependent skills)

```
auth-systems/SKILL.md
    ↓ mentions dependency
"See backend-dev-guidelines for FastAPI protected route patterns"
    ↓
Agent loads backend-dev-guidelines/SKILL.md if not already loaded
    ↓
Proceeds with combined context
```

---

## Integration Points

### INDEX.md Updates (Modified File)

INDEX.md at `.agent/skills/INDEX.md` must be updated for each new skill. The update pattern is:

1. Add a new row to the appropriate category table (or create a new category section).
2. Use the 📚 emoji marker if the skill has `references/` content (all 5 new skills qualify).
3. Add a Quick Selection Guide entry if the use case is not covered by existing entries.

**Category placement for new skills:**

| Skill | Existing Category | Rationale |
|-------|------------------|-----------|
| auth-systems | Security | Auth is a security boundary concern |
| stripe-payments | New category: "Payments" | No payments category exists; `pci-compliance` is compliance-focused, not integration-focused |
| rag-vector-search | New category: "AI / LLM" | No AI/LLM category exists yet |
| agent-architecture | New category: "AI / LLM" | Belongs alongside rag-vector-search |
| prompt-engineering | New category: "AI / LLM" | Belongs alongside the other AI skills |

**Recommended INDEX.md additions:**

```markdown
### Security

| Skill | Description | Difficulty | When to Use |
|-------|-------------|------------|-------------|
| [auth-systems](auth-systems/SKILL.md) 📚 | Clerk and Auth.js/NextAuth: session handling, protected routes, OAuth flows | Intermediate | Adding authentication to Next.js apps |
| [pci-compliance](pci-compliance/SKILL.md) | ... (existing row) | ... | ... |
| [security/security-scanning](security/security-scanning/SKILL.md) | ... (existing row) | ... | ... |

### Payments

| Skill | Description | Difficulty | When to Use |
|-------|-------------|------------|-------------|
| [stripe-payments](stripe-payments/SKILL.md) 📚 | Stripe checkout, subscriptions, webhooks, billing patterns | Intermediate | Integrating payments into web apps |

### AI / LLM

| Skill | Description | Difficulty | When to Use |
|-------|-------------|------------|-------------|
| [rag-vector-search](rag-vector-search/SKILL.md) 📚 | Embedding pipelines, pgvector/Pinecone, similarity retrieval | Advanced | Adding semantic search or RAG to an app |
| [agent-architecture](agent-architecture/SKILL.md) 📚 | Multi-agent systems, handoffs, memory, orchestration | Advanced | Building AI agent systems |
| [prompt-engineering](prompt-engineering/SKILL.md) 📚 | Prompt templates, evaluation, iteration workflows, anti-patterns | Intermediate | Designing or improving LLM prompts |
```

**Quick Selection Guide additions:**

```markdown
**"I need to add login/auth to my app"**
→ `auth-systems`

**"I need to accept payments"**
→ `stripe-payments` for integration, `pci-compliance` for compliance requirements

**"I need semantic search or RAG"**
→ `rag-vector-search`

**"I'm building an AI agent"**
→ `agent-architecture` for multi-agent design, `prompt-engineering` for prompt quality
```

### Cross-References Between New Skills

The 5 skills form a dependency graph. Cross-references should be explicit in SKILL.md bodies:

```
auth-systems
  ├── references backend-dev-guidelines (FastAPI protected routes)
  └── references frontend-dev-guidelines (Next.js middleware, protected pages)

stripe-payments
  ├── references auth-systems (user identity for billing)
  ├── references backend-dev-guidelines (webhook endpoint structure)
  └── references pci-compliance (compliance obligations)

rag-vector-search
  ├── references database-design (pgvector extension, migrations)
  ├── references postgresql (vector column types, HNSW index setup)
  └── references backend-dev-guidelines (FastAPI retrieval endpoints)

agent-architecture
  ├── references prompt-engineering (system prompt design for agents)
  └── references workflow-orchestration-patterns (durable agent loops)

prompt-engineering
  └── references agent-architecture (prompts in agent context)
```

Note: auth-systems and stripe-payments have a coupling point (user identity → billing). The stripe-payments SKILL.md should note the dependency explicitly: "Requires an auth layer to associate charges with users — see `auth-systems`."

### Existing Skills That Reference New Skills

These existing skills contain partial coverage of topics the new skills will own. They should be updated to cross-reference rather than duplicate:

| Existing Skill | Existing Coverage | Action |
|----------------|------------------|--------|
| `api-patterns/auth.md` | JWT/session pattern overview | Add note: "For full auth provider integration see `auth-systems`" |
| `pci-compliance/SKILL.md` | Stripe tokenization code examples | Add note: "For complete Stripe integration patterns see `stripe-payments`" |
| `postgresql/SKILL.md` | Mentions `pgvector` extension | Add note: "For RAG/embedding pipeline patterns see `rag-vector-search`" |

---

## Build Order

Skill dependencies determine the correct build order:

```
Phase 1: Foundation skills (no new-skill dependencies)
  1. prompt-engineering    — standalone; no dependency on other new skills
  2. auth-systems          — depends only on existing skills (backend-dev-guidelines, frontend-dev-guidelines)

Phase 2: Skills that depend on Phase 1
  3. rag-vector-search     — depends only on existing skills (database-design, postgresql)
  4. agent-architecture    — depends on prompt-engineering (Phase 1)

Phase 3: Skills that depend on Phase 1 + existing
  5. stripe-payments       — depends on auth-systems (Phase 1); also cross-refs pci-compliance
```

**Rationale for this order:**

- `prompt-engineering` first because `agent-architecture` references it. Building prompts before agents lets the agent skill reference complete content.
- `auth-systems` second because `stripe-payments` references it for user identity. A complete auth skill lets the stripe skill reference accurate patterns.
- `rag-vector-search` third because it has no new-skill dependencies; its references to `database-design` and `postgresql` are already stable.
- `agent-architecture` fourth so it can reference `prompt-engineering` as a complete skill.
- `stripe-payments` last because it depends on `auth-systems` and cross-references `pci-compliance`, both of which are stable by this point.

---

## New vs Modified Files

### New Files (create from scratch)

```
.agent/skills/auth-systems/SKILL.md
.agent/skills/auth-systems/references/clerk-setup.md
.agent/skills/auth-systems/references/nextauth-setup.md
.agent/skills/auth-systems/references/oauth-patterns.md

.agent/skills/stripe-payments/SKILL.md
.agent/skills/stripe-payments/references/checkout-sessions.md
.agent/skills/stripe-payments/references/subscriptions.md
.agent/skills/stripe-payments/references/webhooks.md

.agent/skills/rag-vector-search/SKILL.md
.agent/skills/rag-vector-search/references/embedding-pipelines.md
.agent/skills/rag-vector-search/references/pgvector-setup.md
.agent/skills/rag-vector-search/references/retrieval-patterns.md

.agent/skills/agent-architecture/SKILL.md
.agent/skills/agent-architecture/references/multi-agent-patterns.md
.agent/skills/agent-architecture/references/memory-systems.md
.agent/skills/agent-architecture/references/tool-use-patterns.md

.agent/skills/prompt-engineering/SKILL.md
.agent/skills/prompt-engineering/references/template-patterns.md
.agent/skills/prompt-engineering/references/evaluation-methods.md
.agent/skills/prompt-engineering/references/anti-patterns.md
```

Total: 5 SKILL.md files + 15 references files = **20 new files**

### Modified Files (update existing)

```
.agent/skills/INDEX.md
  — Add 3 new category sections (Payments, AI / LLM)
  — Add auth-systems row to Security section
  — Add 4 Quick Selection Guide entries

.agent/skills/api-patterns/auth.md
  — Add forward-reference to auth-systems skill

.agent/skills/pci-compliance/SKILL.md
  — Add forward-reference to stripe-payments skill

.agent/skills/postgresql/SKILL.md
  — Add forward-reference to rag-vector-search skill
```

Total: **4 modified files**

---

## Anti-Patterns

### Anti-Pattern 1: Splitting One Skill Across Multiple SKILL.md Files

**What people do:** Create `auth-clerk/SKILL.md` and `auth-nextauth/SKILL.md` as separate top-level skills.

**Why it's wrong:** Doubles the INDEX.md surface area for one conceptual domain. Agents must now choose between two skills for "auth" at discovery time, not at implementation time. Existing viflo practice uses one skill per domain with variant selection handled inside via references/.

**Do this instead:** Single `auth-systems/SKILL.md` with a provider selection table at the top, then "for Clerk see references/clerk-setup.md / for Auth.js see references/nextauth-setup.md."

### Anti-Pattern 2: Duplicating Content Across Skills

**What people do:** Put Stripe tokenization code in both `stripe-payments/` and `pci-compliance/` because both cover payment security.

**Why it's wrong:** Creates drift — when Stripe API changes, two files need updating. The skill-creator canon explicitly states: "Information should live in either SKILL.md or references files, not both."

**Do this instead:** `pci-compliance` owns the compliance rules and data minimization principles; `stripe-payments` owns the implementation patterns. Each references the other for the complementary concern.

### Anti-Pattern 3: Using @ Syntax for Cross-Skill Links

**What people do:** Write `@.agent/skills/backend-dev-guidelines/SKILL.md` in a cross-reference.

**Why it's wrong:** `@` syntax force-loads the file immediately, consuming context budget before Claude knows whether it is needed. The `writing-skills` reference explicitly prohibits this.

**Do this instead:** Reference by skill name only: "See `backend-dev-guidelines` for FastAPI endpoint structure."

### Anti-Pattern 4: Exceeding 500 Lines in SKILL.md

**What people do:** Put full webhook implementation code and full Stripe API reference in `stripe-payments/SKILL.md`.

**Why it's wrong:** v1.1 enforced the 500-line limit as a hard requirement (CONTENT-01). Overlong SKILL.md files bloat the context window on every trigger.

**Do this instead:** Keep SKILL.md to decision logic, quick-reference tables, and links. Move implementation code to `references/webhooks.md`.

---

## Sources

- Direct inspection of `.agent/skills/` directory (HIGH confidence — first-party codebase)
- `.agent/skills/INDEX.md` — skill discovery conventions
- `.agent/skills/skill-creator/SKILL.md` — canonical skill authoring guide
- `.agent/skills/writing-skills/references/guides/prompt-engineering.md` — cross-referencing and description conventions
- `.planning/PROJECT.md` — v1.1 CONTENT-01 requirement (≤500 line enforcement), v1.2 requirements (AUTH-01, STRIPE-01, RAG-01, AGENT-01, PROMPT-01)

---

*Architecture research for: viflo v1.2 Skills Expansion*
*Researched: 2026-02-24*
