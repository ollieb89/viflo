# Phase 01: Foundation & Planning Infrastructure

> **Goal:** Establish the development environment, select core LLMs, create
> planning infrastructure, and produce a minimal-viable system architecture —
> all before any feature implementation begins.

> [!IMPORTANT]
> This phase is about **building the machine that builds the application**.
> Keep every task at the minimum-viable level needed to unblock Phase 02.
> Depth comes from iteration, not upfront over-engineering.

---

## Phase Overview

| Property             | Value                                                              |
| -------------------- | ------------------------------------------------------------------ |
| **Phase**            | 01 — Foundation & Planning Infrastructure                          |
| **Estimated Effort** | 2–3 days (solo) · 1–2 days (team)                                  |
| **Parallel Tracks**  | 2 (Toolchain Track + Planning Track)                               |
| **Tasks**            | 6                                                                  |
| **Deliverables**     | Working env, quality gates, LLM picks, PLAN.md, ARCHITECTURE.md, CI pipeline, bootstrap script |

---

## Execution Tracks

```
Track A — Toolchain                Track B — Planning
─────────────────────              ─────────────────────
Task 1: Dev Environment  ───┐     Task 3: LLM Selection (3 picks)
          │                  │               │
Task 2: Code Quality         │     Task 4: Planning Infrastructure
          │                  │               │
Task 6: CI/CD Pipeline  ────┘     Task 5: System Architecture (MV)
```

**Dependencies:**
- Task 2 depends on Task 1
- Task 6 depends on Task 1 + Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4

---

## Fork-in-the-Road Decisions (Resolve Before Task 5)

> [!WARNING]
> These architectural forks must be decided explicitly during Phase 01.
> Deferring them will create ambiguity in every subsequent phase.

### Decision 1: Backend Shape [RESOLVED]

**Selected: Option B (Next.js Frontend + Express API)**

> Rationale: GeriApp architecture defines a clear separation with a dedicated Node.js/Express User Service (Port 8100) and separate Python services. This supports the complex domain requirements and future scaling.

### Decision 2: Python Integration Model [RESOLVED]

**Selected: Option A (Separate Python Service)**

> Rationale: The Computer Vision (AI Service) and Care Service are core components defined in the stack (Ports 8101, 8102) using FastAPI. Direct synchronous access is required for real-time interactions.

---

## Task 1: Development Environment Setup

**Objective:** Install and verify all tooling for the Node.js / Next.js / Python stack and 2–3 core CLI agents.

**Deliverable:** Working dev environment + `scripts/bootstrap.sh` (or `bootstrap.md`)

### Todos

- [ ] **1.1** Install Node.js v22+
  - Recommend usage of `nvm` or `fnm`
  - Verify: `node --version` (expect >= 22.0.0)
- [ ] **1.2** Initialize Monorepo with pnpm workspaces
  - `pnpm init` in root
  - Create `pnpm-workspace.yaml`
  - Verify: `pnpm --version` (expect >= 10.0.0)
- [ ] **1.3** Install Python 3.11+ via Pixi
  - Install `pixi` (global or local project)
  - Verify: `pixi --version`
- [ ] **1.4** Initialize Python project structure
  - Create `pixi.toml` for Python services
  - Verify: `pixi run start` (or similar bootstrap command) works
- [ ] **1.5** Install core CLI agents (pick 2–3)
  - **Aider** — multi-file refactoring workhorse
  - **Claude Code CLI** — planning brain, architectural reasoning
  - **Gemini CLI** or equivalent — fast single-file code gen
  - Verify each with `--help` / `--version` + a trivial prompt
- [ ] **1.6** *(Deferred)* Codex CLI, Amazon Q CLI, Qwen Code
  - Install only when a Phase 02+ task specifically needs them
- [ ] **1.7** Create `scripts/bootstrap.sh`
  - Automate or document everything above
  - New contributor should go from zero to working env in < 1 hour
  - Include `.env.example` with required API keys listed

### Acceptance Criteria
- [ ] Node.js + Python runtimes installed and on `$PATH`
- [ ] Project scaffolds exist
- [ ] 2–3 CLI agents installed and responding to basic prompts
- [ ] `scripts/bootstrap.sh` exists and is documented
- [ ] API keys configured (`.env` from `.env.example`)

---

## Task 2: Code Quality Toolchain

**Objective:** Configure linters, formatters, and pre-commit hooks so every commit meets quality standards automatically.

**Deliverable:** Pre-commit hooks running lint + format on every commit.

### Todos

- [ ] **2.1** Install and configure ESLint
  - TypeScript + React/Next.js rules
  - Verify: `npx eslint . --ext .ts,.tsx`
- [ ] **2.2** Install and configure Prettier
  - `.prettierrc` + `eslint-config-prettier`
  - Verify: `npx prettier --check .`
- [ ] **2.3** Install Husky + lint-staged
  - Pre-commit hook triggers ESLint + Prettier on staged files
  - Verify: a staged file triggers lint on `git commit`
- [ ] **2.4** Install Black for Python
  - Configure in `pyproject.toml`
  - Verify: `black --check .`
- [ ] **2.5** Install Flake8 for Python
  - `.flake8` config (line length = 88 to match Black)
  - Verify: `flake8 .`
- [ ] **2.6** Create unified quality script
  - `Makefile` with targets: `lint`, `format`, `check`
  - Runs all JS + Python checks
  - Verify: `make check` exits 0
- [ ] **2.7** Run full pass on scaffold + commit
  - `chore: initial code quality setup`

### Acceptance Criteria
- [ ] ESLint + Prettier for JS/TS
- [ ] Black + Flake8 for Python
- [ ] Pre-commit hooks intercept every `git commit`
- [ ] `make check` passes end-to-end

---

## Task 3: LLM Selection (Focused — 3 Picks)

**Objective:** Select exactly 3 models, one for each role, with a simple routing strategy. Expand evaluation in later iteration loops.

**Deliverable:** `llm_selection.md` with 3 picks and routing table.

> [!TIP]
> Phase 01 is not a benchmark paper. Pick models you can start using **today**,
> then reassess in the Section 5 iteration loop.

### Model Roles

| Role | Purpose | Selection Criteria |
| ---- | ------- | ------------------ |
| 🧠 **Planning Brain** | PLAN.md, ARCHITECTURE.md, specs, complex reasoning | Best structured reasoning, long context |
| ⚡ **Coding Workhorse** | Multi-file implementation, refactoring, code gen | Fast, accurate code, good repo context |
| 💰 **Cheap Bulk / Local Fallback** | Repetitive edits, doc formatting, privacy-sensitive | Lowest cost, acceptable quality, local option |

### Todos

- [ ] **3.1** Define lightweight evaluation rubric
  - Criteria: cost/1K tokens, coding quality (subjective 1–5), context window, API stability
  - Keep it to a single comparison table
- [ ] **3.2** Test 2–3 candidates per role
  - Planning Brain candidates: Claude Opus 4.5, Gemini 3 Pro, GPT-5.2
  - Coding Workhorse candidates: Gemini 3 Pro, Claude Sonnet, GPT-5.2
  - Cheap Bulk candidates: DeepSeek V3.x, Qwen (local), GLM-5
  - Use 1–2 representative prompts per role (not a full suite)
- [ ] **3.3** Pick one model per role
  - Document rationale (2–3 sentences each)
  - Document fallback model for each role
- [ ] **3.4** Define agent ↔ model routing
  - Map: Aider → Coding Workhorse model
  - Map: Claude Code CLI → Planning Brain model
  - Map: Fast CLI agent → Coding Workhorse or Bulk model
  - Document in `llm_selection.md`
- [ ] **3.5** Estimate monthly cost
  - Based on expected usage patterns (rough order of magnitude)

### Acceptance Criteria
- [ ] 3 models selected (one per role), documented with rationale
- [ ] Fallback model defined for each role
- [ ] Agent-to-model routing table documented
- [ ] Monthly cost estimate included (order of magnitude)

---

## Task 4: Planning Infrastructure

**Objective:** Create PLAN.md with complete project context so any LLM can generate useful architecture from it.

**Deliverable:** `PLAN.md` in repo root + `prompts/` directory.

### Todos

- [ ] **4.1** Create `PLAN.md` with sections
  - Overview, Tech Stack, Infrastructure, Budget & Latency, Auth & Security
- [ ] **4.2** Fill in Tech Stack
  - **Frontends:** Next.js 16 (App Router), React 18, Tailwind CSS 4
  - **Backends:** Node.js/Express (Port 8100), FastAPI (Ports 8101, 8102)
  - **Data:** PostgreSQL (Port 5435), Redis (Port 6479)
  - **Package Managers:** pnpm (JS), Pixi (Python)
  - **Decisions Recorded:** Backend Shape (B), Python Integration (A)
- [ ] **4.3** Fill in Infrastructure Constraints
  - Hosting, compute limits, networking
- [ ] **4.4** Fill in Budget & Latency
  - Infra budget, LLM budget (from Task 3.5), latency targets (p95)
- [ ] **4.5** Fill in Auth & Security
  - Provider, auth flow, authorization model, encryption, compliance
- [ ] **4.6** Create prompt templates (2–3 to start)
  - `prompts/generate-system-design.md`
  - `prompts/generate-api-route.md`
  - `prompts/generate-db-migration.md`

### Acceptance Criteria
- [ ] `PLAN.md` exists with all sections filled
- [ ] Tech stack versions pinned, fork-in-the-road decisions recorded
- [ ] Budget constraints documented with numbers
- [ ] At least 2 prompt templates created

---

## Task 5: System Architecture Design (Minimal Viable)

**Objective:** Produce the initial system architecture — enough to start the first vertical slice in Phase 02. Depth comes from iteration.

**Deliverable:** `ARCHITECTURE.md`

> [!NOTE]
> Keep this deliberately **thin**. The goal is a shared blueprint that's
> detailed enough to start coding, not a 50-page design doc.

### Todos

- [ ] **5.1** Design API route tree
  - List planned routes (method, path, purpose)
  - Group by domain (auth, users, data, etc.)
  - Minimum: cover the first vertical slice
- [ ] **5.2** Design PostgreSQL database schema
  - ERD (Mermaid or text)
  - Tables, columns, types, constraints, relationships
  - **ORM:** SQLAlchemy (shared models in `backend/shared/`)
  - **Validation:** Pydantic schemas
  - Migration strategy (Alembic)
- [ ] **5.3** Define authentication model
  - Auth flow: login, register, token refresh
  - Token format + storage
  - Middleware/guard pattern
- [ ] **5.4** Backend integration decision pattern
  - **Selected:** Synchronous REST API calls (Node -> Python)
  - Define contract: OpenAPI/Swagger for FastAPI services
  - Define shared models in `backend/shared/`
- [ ] **5.5** Define error handling strategy
  - Standard error response format
  - Logging framework and levels
  - Monitoring approach (can be "TBD — revisit in Phase 03")
- [ ] **5.6** Create testing plan (targets only)
  - Unit test coverage target (e.g., ≥ 80%)
  - Integration test scope
  - E2E test strategy
  - **Defer** performance testing tooling to when endpoints exist
  - **Keep** latency targets as p95 goals (from PLAN.md)
- [ ] **5.7** Iterate with Planning Brain LLM
  - Feed PLAN.md context → generate draft → review → refine
  - Minimum 2 refinement passes

### Acceptance Criteria
- [ ] `ARCHITECTURE.md` exists with all sections
- [ ] API routes cover the first vertical slice
- [ ] Database schema has ≥ 3 tables with relationships
- [ ] Auth model specifies the complete flow
- [ ] Backend integration decision documented with rationale
- [ ] Testing plan has coverage targets (tooling deferred)

---

## Task 6: CI/CD Pipeline Foundation

**Objective:** Every push and PR is automatically linted, tested, and built. Start simple, expand later.

**Deliverable:** Green CI pipeline on push and PR.

### Todos

- [ ] **6.1** Create `.github/workflows/ci.yml`
  - Trigger: `push` to `main`, `pull_request`
  - Ubuntu latest runner
- [ ] **6.2** JavaScript/TypeScript job
  - Install Node.js → install deps → ESLint → Prettier check → Jest (if tests exist) → `npm run build`
- [ ] **6.3** Python job
  - Install Python → install deps → Flake8 → Black check → pytest (if tests exist)
- [ ] **6.4** Failure policies
  - `fail-fast: true`, require all checks, timeout 10 min
- [ ] **6.5** Branch protection
  - Require CI pass before merge to `main`
  - Prevent force-push to `main`
- [ ] **6.6** Verify pipeline
  - Push a clean commit → all green
  - Break a lint rule → pipeline fails
  - Fix → green again

### Acceptance Criteria
- [ ] CI runs on push + PR
- [ ] JS/TS and Python jobs both pass
- [ ] Pipeline fails on lint errors (verified)
- [ ] Branch protection active on `main`

---

## Phase 01 Risk Register

| Risk | Impact | Likelihood | Mitigation |
| ---- | ------ | ---------- | ---------- |
| LLM API costs exceed budget | High | Medium | Start with free tiers; pick only 3 models |
| CLI agent auth/setup overhead | Medium | Medium | Install only 2–3 agents; defer the rest |
| Over-engineering architecture | Medium | High | Keep MV — detail only the first vertical slice |
| Tool version conflicts | Low | Medium | Use version managers (nvm, pyenv); pin versions |
| Fork-in-the-road decisions deferred | Low | Low | Decisions 1 & 2 resolved in Phase 01 setup |

---

## Phase 01 Success Criteria (Gate Check)

> [!CAUTION]
> **Do NOT proceed to Phase 02 until all criteria are met.**

- [ ] All runtimes and 2–3 CLI agents installed and verified
- [ ] Pre-commit hooks active (lint + format on every commit)
- [ ] 3 LLMs selected (Planning Brain, Coding Workhorse, Cheap Bulk) with routing
- [ ] `PLAN.md` populated — fork-in-the-road decisions resolved
- [ ] `ARCHITECTURE.md` covers first vertical slice (API, DB, auth)
- [ ] CI/CD pipeline green on `main`
- [ ] `scripts/bootstrap.sh` or `bootstrap.md` — new contributor zero-to-working in < 1 hour

---

## Artifact Naming

| Artifact | File |
| -------- | ---- |
| Phase plan | `phase_01.md` |
| LLM selection | `llm_selection.md` |
| Project plan & context | `PLAN.md` |
| System architecture | `ARCHITECTURE.md` |
| CI/CD workflow | `.github/workflows/ci.yml` |
| Quality scripts | `Makefile` |
| Prompt templates | `prompts/*.md` |
| Bootstrap script | `scripts/bootstrap.sh` |

---

## What's Deferred to Later Phases

| Item | Deferred To | Trigger |
| ---- | ----------- | ------- |
| Full LLM benchmark suite | Iteration loop (Section 5) | Quarterly or when model costs spike |
| Microservice refactor | Phase 02–03 | First vertical slice reveals separation need |
| Performance testing tooling | Phase 03+ | Endpoints exist to measure |
| Additional CLI agents (Codex, Q, Qwen) | As needed | Specific task requires them |
| Detailed monitoring/alerting setup | Phase 03+ | Production deployment imminent |
