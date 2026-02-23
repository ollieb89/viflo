# Phase 3 Implementation Plan: Agentic Implementation (Execution)

> **For Implementation Agents (Aider/Gemini CLI):** REQUIRED SUB-SKILL: use `executing-plans` to implement this plan task-by-task.
> **Rule:** If `PLAN.md` specifies Python, incorporate `.agent/rules/prioritize-python-3-10-features.md`.

**Goal:** Execute the `TASKS.md` backlog generated in Phase 2, transforming the architectural blueprint into functional, tested software using the Agentic Implementation Loop.
**Scope:** Framework-agnostic execution based on the Tech Stack defined in `docs/planning/PLAN.md`.

**Timeline:** Weeks 3-5
**Owner:** Implementation Agents (Aider / Gemini CLI / Claude Code)

**Architecture:**

- **Agentic Loop:** Prompt -> Code -> Test -> Refine -> Commit.
- **Model Routing:** Use Cheap/Fast models (Gemini Flash, Spark) for bulk code, Mid-Tier (Claude Sonnet) for logic.
- **TDD:** Tests are written _before_ or _alongside_ code.
- **Boilerplate First:** Scaffold structure before business logic.

---

### Task 1: Monorepo Scaffold & Boilerplate Generation

**Context:** `universal_agentic_development.md`, Section 3.1.
**Agent:** Scaffold Agent (Cheap - Gemini 3 Flash / Qwen-Coder).
**Inputs:** `PLAN.md#Tech Stack`.

#### Step 1: Initialize Workspace

Identify the Monorepo Tool defined in `PLAN.md` (e.g., Turborepo, Nx, Lerna, or Python Workspace).

- Action: Initialize the workspace structure.
- **Constraint:** Ensure package manager matches `PLAN.md` (pnpm, npm, bun, uv, poetry).

#### Step 2: Configure Base Tooling

Set up the root configuration files to enforce strict standards suitable for the language(s).

- **TypeScript/JS:** `tsconfig.json` (strict: true), `.eslintrc.js`.
- **Python:** `ruff.toml` (strict), `pyproject.toml`.
- **General:** `.gitignore`, `.editorconfig`.

#### Step 3: Generate Shared Schema/Types Package

Create a lightweight package for maintaining the canonical data definitions.

- Action: Create `packages/types` (TS) or `packages/schema` (Python).
- Action: Translate the "Schema Definitions" from `PLAN.md` into exportable code (Zod, Pydantic, TypeBox).

#### Step 4: Scaffold Application Directories

- Action: Create empty application directories (Frontend/Backend) matching the `PLAN.md` topology.
- Action: Install framework-specific scaffolding (e.g., `create-next-app`, `fastapi-template`).
- Action: Install the UI Component Library defined in `PLAN.md` (e.g., `shadcn/ui`, `MUI`, `Tailwind`).

**Verification:**

- Run Build Command (e.g., `pnpm build`, `uv build`).
- Verify Shared Package can be imported by the applications.
- Commit: `chore: initial scaffold and shared types`

---

### Task 2: Database Migration & ORM Layer Implementation

**Context:** `universal_agentic_development.md`, Section 3.2.
**Agent:** Backend Agent (Cheap - Gemini 3 Flash).
**Inputs:** `PLAN.md#Database Schema`, `PLAN.md#Tech Stack`.

#### Step 1: Translate Schema to Code

- Action: Read the `Mermaid/SQL` schema from `PLAN.md`.
- Action: Generate the ORM configuration/schema file for the tool defined in `PLAN.md` (e.g., `schema.prisma`, `drizzle.schema.ts`, `models.py`).

#### Step 2: Generate Migrations & Client

- Action: Run the migration generation command for the chosen ORM.
- Action: Generate the type-safe database client/SDK.

#### Step 3: Create Seeding Script

- Action: Create a seed script (in the language of the stack) that populates the DB with dummy data.
- **Requirement:** Must include at least 10 records for primary entities to facilitate UI testing.

**Verification:**

- Run Migration Verification (Success).
- Run Seed Script (Success).
- Verify database contains expected dummy data.
- Commit: `feat: database schema and seeding`

---

### Task 3: Feature Implementation Loop (The Core Engine)

**Context:** `universal_agentic_development.md`, Section 3.3.
**Agent:** Coding Agent (Aider via Gemini 3 Flash / GPT-GenCode).
**Inputs:** `docs/planning/TASKS.md` (Generated in Phase 2).

**Execution Protocol:**
This task is a recursive loop processing the backlog in `TASKS.md`.

**For each TASK in TASKS.md:**

1.  **Context Loading:**
    - Read the specific Task entry.
    - Read the referenced section in `PLAN.md`.
    - Check for Shared Schema definitions (from Task 1).

2.  **Implementation (Iterative Loop):**
    - **Step A: Test Gen:** Write the Unit Test file first (using the Framework defined in `PLAN.md`).
    - **Step B: Code Gen:** Write the implementation to satisfy the test.
      - _Prompt Tip:_ "Implement [Feature] using [Framework] as defined in PLAN.md."
    - **Step C: Verify:** Run the test runners.
    - **Step D: Refine:** If fail, read error -> fix code -> retry (Max 3 retries).
    - **Step E: Commit:** `git commit -m "feat: implement [Task Name]"`

**Model Strategy:**

- Use **Cheap Models** (Flash) for component/service logic.
- Switch to **Mid-Tier** (Sonnet/Pro) only if "Retry Loop" exceeds 3.

**Verification:**

- All new tests pass.
- Linting passes.

---

### Task 4: Integration Logic & Middleware Connection

**Context:** `universal_agentic_development.md`, Section 3.4.
**Agent:** Logic Agent (Mid-Tier - Claude Sonnet / Gemini Pro).
**Inputs:** `PLAN.md#API Surface`, `PLAN.md#Security`.

#### Step 1: Implement API Route Handlers

- Action: Wire up the logical services (Task 3) to the HTTP layer defined in `PLAN.md`.
- Action: Apply validation pipes (Zod/Pydantic) to inputs.

#### Step 2: Implement Auth Middleware

- Action: Implement the "Middleware Strategy" from `PLAN.md` using the chosen Auth Provider.
- Action: Ensure protected routes reject unauthenticated requests (401/403).

#### Step 3: Integration Testing

- Action: Write integration tests mocking the DB to verify status codes, headers, and auth rejection.

**Verification:**

- Test protected endpoints with/without tokens.
- Commit: `feat: integration logic and middleware`

---

**Exit Criteria for Phase 3:**

- 100% of items in `TASKS.md` are checked off.
- CI Build passes.
- Project runs locally with seeded data.
