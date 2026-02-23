# 3. Implementation Workflow

## Overview

This phase translates the finalized `PLAN.md` (Phase 2) into working software using a disciplined, agent-assisted development loop. The workflow is designed to be **framework-agnostic** — the steps, principles, and decision matrices apply regardless of whether the project uses Next.js, Nuxt, SvelteKit, FastAPI, Django, React Native, or any other stack.

**Inputs:** A locked `PLAN.md` with defined API routes, database schema, auth model, and testing plan.

**Outputs:** Working, tested, reviewed code committed in small increments.

**Model Selection (from Phase 1):** Use **Code Execution** models (e.g., GPT-5 Mini, Claude Sonnet 4.5, Gemini 3 Flash) for implementation tasks. Reserve **High Performance** models for complex debugging or architectural pivots mid-sprint.

---

## 3.1 Task Granulation

### Purpose

Convert the `PLAN.md` into a flat list of discrete, agent-executable tasks. Each task should be completable in **2–15 minutes** by a single agent or developer, with a clear input, output, and verification step.

### Granulation Methodology

**Step 1: Extract features from `PLAN.md`**

Identify every deliverable entity: each API route, each database table, each UI page, each auth flow, each utility module.

**Step 2: Decompose each feature into atomic tasks**

Each task must satisfy the **ACID-T** criteria:

- **Atomic** — One concern per task (one endpoint, one component, one migration)
- **Completable** — Can be finished in a single agent session
- **Independently testable** — Has a verification step that doesn't depend on other incomplete tasks
- **Dependency-aware** — Prerequisites are explicitly listed

**Step 3: Categorize by ecosystem**

Assign each task to a language/runtime ecosystem so the correct agent and model can be selected:

| Category         | Examples                                                   |
| ---------------- | ---------------------------------------------------------- |
| Frontend (JS/TS) | UI components, pages, layouts, client state, form handling |
| Backend (JS/TS)  | API route handlers, middleware, server actions             |
| Backend (Python) | FastAPI endpoints, SQLAlchemy models, Pydantic schemas     |
| Database         | Migrations, seed data, index creation                      |
| Infrastructure   | Docker configs, CI pipelines, deployment scripts           |
| Cross-cutting    | Auth integration, error handling, shared types/schemas     |

### Example Transformation

**High-level feature:**

> "Build user profile feature"

**Granulated tasks:**

1. Create database migration for `users` table
2. Define ORM model / schema for `User` entity
3. Implement `GET /api/users/:id` endpoint
4. Write unit test for `GET /api/users/:id`
5. Implement `PATCH /api/users/:id` endpoint
6. Write unit test for `PATCH /api/users/:id`
7. Create frontend profile page component
8. Connect profile page to API with data fetching
9. Write component test for profile page
10. Add route protection / auth guard for profile route

### Task Sizing Guidelines

| Size | Description                         | Example                             |
| ---- | ----------------------------------- | ----------------------------------- |
| XS   | Single-file change, <20 lines       | Add an env variable, fix a typo     |
| S    | One function/component, 20–80 lines | Write a utility, create a component |
| M    | One feature slice, 80–200 lines     | Full CRUD endpoint + test           |
| L    | Multi-file coordinated change       | Auth flow across frontend + backend |

**Target:** Most tasks should be **S** or **M**. Break **L** tasks further if possible.

---

## 3.2 Strategic Agent & Model Selection

### Decision Matrix

Select the agent/model combination based on task characteristics, not brand loyalty. The table below maps task attributes to recommended tools.

| Task Characteristic                 | Recommended Agent Type           | Model Tier (Phase 1)   |
| ----------------------------------- | -------------------------------- | ---------------------- |
| Single-file generation (<100 lines) | Inline CLI (Gemini CLI, Copilot) | Code Execution (Flash) |
| Multi-file refactoring              | Aider, Claude Code               | Code Execution (Mid)   |
| Complex reasoning / debugging       | Claude Code, Codex CLI           | High Performance       |
| Repository-wide changes             | Codex CLI, Aider (architect)     | High Performance       |
| Cloud infrastructure / IaC          | Google Q CLI, AWS Q              | Code Execution (Mid)   |
| Privacy-sensitive / offline         | Qwen Code, local Ollama          | Open-Source            |
| Test generation                     | Any CLI agent                    | Code Execution (Cheap) |
| Documentation / comments            | Any CLI agent                    | Code Execution (Cheap) |

### Agent Capabilities Reference

| Agent             | Strengths                                   | Best For                               |
| ----------------- | ------------------------------------------- | -------------------------------------- |
| Aider             | Multi-file edits, git-aware, architect mode | Refactoring, feature slices            |
| Gemini CLI        | Fast, cheap, large context                  | Single-file generation, quick fixes    |
| Codex CLI         | Multi-step reasoning, repo-wide context     | Complex multi-step tasks               |
| Claude Code CLI   | Deep reasoning, structured output           | Architecture, debugging, complex logic |
| Google Q CLI      | GCP-native, cloud infrastructure            | Infrastructure, deployment             |
| Qwen Code         | Local execution, no API cost                | Privacy-sensitive, offline work        |
| Cursor / Windsurf | IDE-integrated, visual diff                 | Interactive development, exploration   |

### Cost-Optimized Routing

Apply the **cheapest capable model** principle:

```
Is the task trivial (boilerplate, types, simple CRUD)?
  → Use Code Execution Cheap tier (Gemini 3 Flash, GPT-5 Mini)

Does it require multi-file coordination?
  → Use Code Execution Mid tier (Claude Sonnet 4.5, Gemini 2.5 Pro)

Does it require deep reasoning or architecture decisions?
  → Use High Performance tier (Claude Opus 4.5, GPT-5.2, Gemini 3 Pro)

Is it privacy-sensitive or must run offline?
  → Use Open-Source tier (Qwen, DeepSeek V3.x, GLM-5)
```

---

## 3.3 Task Execution Order & Dependency Management

### Dependency Graph

Before executing any task, establish a dependency order. The general pattern for most web applications:

```
1. Database schema / migrations        (no dependencies)
2. ORM models / entity definitions      (depends on 1)
3. Shared types / validation schemas    (depends on 2)
4. Backend API endpoints                (depends on 2, 3)
5. Authentication / authorization       (depends on 4)
6. Frontend data fetching layer         (depends on 4)
7. Frontend UI components               (depends on 3)
8. Frontend pages / routes              (depends on 6, 7)
9. Integration tests                    (depends on 4, 5)
10. E2E tests                           (depends on 8)
```

### Parallelization Opportunities

Tasks at the same dependency level can be executed in parallel by different agents or developers:

- **Level 1:** All database migrations (independent tables)
- **Level 2:** All ORM models (independent entities)
- **Level 4:** Independent API endpoints (e.g., `/users` and `/posts`)
- **Level 7:** Independent UI components (e.g., `ProfileCard` and `SettingsForm`)

### Blocked Task Handling

When a task is blocked by an incomplete dependency:

1. **Stub the dependency** — Create a minimal interface/type/mock that satisfies the contract
2. **Proceed with the blocked task** using the stub
3. **Replace the stub** when the real dependency is complete
4. **Re-run tests** to verify integration

---

## 3.4 Contextual Code Generation Best Practices

### Universal Prompting Principles

Regardless of framework, every code generation prompt must include:

1. **Exact file path** — Where the generated code should live
2. **Required exports** — What the module exposes (function names, types, classes)
3. **Dependency requirements** — What packages/modules it imports
4. **Framework constraints** — Version, conventions, patterns to follow
5. **Verification criteria** — How to confirm it works (test command, expected output)

### Per-Ecosystem Prompting Templates

#### JavaScript / TypeScript (Any Framework)

```
Generate: [component / route handler / utility / hook]
File: [exact/path/to/file.ts]
Framework: [Next.js 16 / Nuxt 4 / SvelteKit / React Native / Express / Hono]
Exports: [named exports with TypeScript signatures]
Dependencies: [npm packages with versions]
Conventions:
  - [Use App Router / pages/ directory / file-based routing]
  - [Server Components / Client Components / composables / stores]
  - [Styling approach: Tailwind / CSS Modules / styled-components]
Test file: [tests/path/to/file.test.ts]
```

#### Python (Any Framework)

```
Generate: [endpoint / model / service / schema / utility]
File: [exact/path/to/module.py]
Framework: [FastAPI / Django / Flask]
Exports: [classes, functions with type hints]
Dependencies: [pip/uv/pixi packages with versions]
Conventions:
  - [ORM: SQLAlchemy 2.0 / Django ORM / Tortoise]
  - [Validation: Pydantic v2 / marshmallow / Django forms]
  - [Async: asyncio / sync]
Type hints: Required (Python 3.10+ syntax)
Test file: [tests/path/to/test_module.py]
```

#### Infrastructure / Configuration

```
Generate: [Docker config / CI pipeline / deployment script / migration]
File: [exact/path/to/file]
Platform: [GitHub Actions / GitLab CI / Docker / Kubernetes / Vercel / Railway]
Conventions:
  - [Environment strategy: dev / staging / prod]
  - [Secret management approach]
  - [Hosting target and runtime constraints]
```

### Anti-Patterns to Avoid

| Anti-Pattern                   | Why It Fails                                           | Correct Approach                                                                                    |
| ------------------------------ | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| "Add validation"               | Ambiguous — what fields, what rules, what error format | "Add Zod schema for `CreateUserInput` with email (string, email format), name (string, 2-50 chars)" |
| "Build the user page"          | Too broad for a single task                            | Decompose into data fetching, layout, form, tests                                                   |
| "Use best practices"           | Means nothing to an LLM                                | Specify exact patterns, error boundaries, etc.                                                      |
| No file path specified         | Agent will guess wrong                                 | Always provide exact path relative to project root                                                  |
| No framework version specified | API differences between versions cause bugs            | Always specify major + minor version                                                                |

---

## 3.5 Context Management

### The Context Budget Problem

Every agent has a limited context window. Stuffing the entire codebase into context wastes tokens and degrades output quality. Manage context deliberately.

### Context Loading Strategy

| Task Type        | Context to Provide                                                    |
| ---------------- | --------------------------------------------------------------------- |
| New endpoint     | Related model/schema, existing endpoint patterns, API error format    |
| New UI component | Design system tokens, similar existing components, shared types       |
| Bug fix          | Failing test output, relevant source file, stack trace                |
| Refactoring      | All files being touched, their tests, dependency graph                |
| Infrastructure   | Existing configs (docker-compose, CI yaml), environment variable list |

### Context Layering

Build prompts in layers, from most to least important:

1. **Task description** — What to build, acceptance criteria
2. **Target file(s)** — Where the code goes
3. **Immediate dependencies** — Types, schemas, interfaces this code uses
4. **Pattern examples** — 1–2 similar files from the codebase as style reference
5. **Project conventions** — Linting rules, naming conventions, error handling patterns

**Rule of thumb:** If context isn't directly referenced in the expected output, don't include it.

### Repository Map Technique

For agents that support it (Aider, Claude Code), provide a repository map rather than full file contents:

```
# Repository structure (relevant subset)
src/
  models/         # SQLAlchemy / Prisma / Drizzle models
    user.py       # User entity (id, email, name, created_at)
    post.py       # Post entity (id, title, body, author_id FK→users)
  routes/
    users.py      # GET/POST/PATCH /api/users — the file you are editing
  schemas/
    user.py       # Pydantic / Zod validation schemas
  tests/
    test_users.py # Existing tests for user routes
```

---

## 3.6 Human-in-the-Loop Review Cycle

### Core Principle

AI output is a **first draft**, not a final product. Every generated artifact must pass through a structured review before merging.

### Review Checklist

Apply this checklist to every AI-generated code artifact:

#### Correctness

- [ ] Does the code compile / type-check without errors?
- [ ] Does it handle edge cases (empty input, null values, unauthorized access)?
- [ ] Are all imports resolved and correct?
- [ ] Does it match the `PLAN.md` specification?

#### Security

- [ ] No hardcoded secrets, tokens, or credentials?
- [ ] Input validation present at API boundaries?
- [ ] Auth checks on protected routes/endpoints?
- [ ] No SQL injection, XSS, or CSRF vulnerabilities?

#### Quality

- [ ] Follows project naming conventions?
- [ ] No unnecessary complexity (YAGNI)?
- [ ] No duplicated logic (DRY)?
- [ ] Proper error handling with meaningful messages?
- [ ] Type-safe (no `any` in TypeScript, proper type hints in Python)?

#### Testing

- [ ] Unit test exists and covers the primary behavior?
- [ ] Test passes locally?
- [ ] Edge case tests exist for critical paths?

### Review Severity Levels

| Level    | Action Required                  | Example                                      |
| -------- | -------------------------------- | -------------------------------------------- |
| Critical | Block merge, fix immediately     | Security vulnerability, data loss risk       |
| Major    | Fix before merge                 | Missing error handling, broken test          |
| Minor    | Fix in same PR if easy           | Naming convention violation, missing comment |
| Nit      | Optional, developer's discretion | Style preference, alternative approach       |

### Iterative Refinement Process

When AI output needs improvement, **refine through prompts rather than manual rewriting**:

1. **Identify the issue** — Be specific about what's wrong
2. **Provide a targeted correction prompt** — Don't regenerate the whole file

   Example:

   ```
   The `createUser` function is missing input validation.
   Add Zod/Pydantic schema validation for the request body.
   Reject requests where email is missing or malformed.
   Return a 422 response with the standardized error format from PLAN.md.
   ```

3. **Verify the fix** — Run tests, type-check, review the diff
4. **Accept or iterate** — Maximum 3 refinement rounds before manual intervention

### When to Override AI

Switch to manual coding when:

- The agent is looping on the same error after 3 attempts
- The fix requires understanding of runtime behavior the agent can't observe
- The change involves security-critical logic that must be hand-verified
- Coordinating across 4+ files where agent context is insufficient

---

## 3.7 Commit & Branch Strategy

### Branch Convention

Use a consistent branch naming pattern regardless of git workflow:

```
feature/<feature-name>        # New features
fix/<issue-description>        # Bug fixes
refactor/<scope>               # Refactoring without behavior change
chore/<scope>                  # Config, dependencies, tooling
```

### Commit Cadence

**Commit after every completed task**, not after every session. Each commit should represent one working, tested increment.

```
feat: add GET /api/users/:id endpoint with validation
feat: add user profile page component
fix: handle null avatar URL in profile card
test: add unit tests for user service
chore: add user migration script
```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <description>

[optional body]
[optional footer]
```

Types: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`, `style`, `perf`

### PR Strategy

Group related tasks into a single Pull Request that represents a **complete feature slice**:

- All tasks for "user profile" → one PR
- All tasks for "auth flow" → one PR
- Infrastructure tasks → separate PR

Each PR should be independently deployable and not break existing functionality.

---

## 3.8 Progress Tracking

### Task Board

Maintain a simple task tracker (GitHub Issues, Linear, or even a checklist in `PLAN.md`) with these states:

| State         | Meaning                                      |
| ------------- | -------------------------------------------- |
| `TODO`        | Task defined, not started                    |
| `IN_PROGRESS` | Agent or developer is actively working on it |
| `IN_REVIEW`   | Code generated, awaiting human review        |
| `BLOCKED`     | Waiting on a dependency or decision          |
| `DONE`        | Reviewed, tested, committed                  |

### Sprint Metrics

Track per sprint/iteration (feeds into Phase 5 — Continuous Improvement):

- **Tasks completed** vs **tasks planned**
- **Agent success rate** — % of tasks that passed review on first generation
- **Refinement rounds** — Average prompt iterations per task
- **Cost per task** — Token usage × model price
- **Blocked time** — Hours spent waiting on dependencies

### Done Criteria for Phase 3

The implementation phase is complete when:

- [ ] All tasks from PLAN.md are in `DONE` state
- [ ] All unit tests pass
- [ ] Code compiles / type-checks without errors across the entire project
- [ ] All PRs have been reviewed and merged
- [ ] No critical or major review findings remain open
- [ ] The application runs locally end-to-end
- [ ] Ready to proceed to Phase 4 (Testing & CI)
