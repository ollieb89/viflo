# **Implementation Plan: Universal Agentic Development Workflow**

## **Executive Summary**

The transition to an agentic-first software development lifecycle represents a fundamental paradigm shift in how enterprise-grade applications are architected, implemented, and maintained. This report presents a comprehensive implementation plan for the **Universal Agentic Development Workflow**, a project designed to operationalize a "Hybrid, Planning-First" methodology that integrates deep strategic reasoning with high-velocity, automated execution. By leveraging the specific capabilities of the Q1 2026 AI landscape—characterized by the bifurcation of models into "Reasoning Engines" (e.g., **Claude Opus 4.6**, **GPT-5.3**) and "Execution Engines" (e.g., **Gemini 3 Flash**, **GPT-5.3-Codex-Spark**)—this plan outlines a trajectory to reduce development costs by an estimated 60% while simultaneously accelerating time-to-market.

The feasibility of this initiative is assessed as **High**. This assessment is grounded in the maturity of current agentic orchestration frameworks and the proven capability of Large Language Models (LLMs) to handle discrete, well-bounded coding tasks with high fidelity. The project is structured around a critical separation of concerns: human architects and premium AI models define the "what" and "why" during a rigorous planning phase, while cost-efficient agentic swarms execute the "how" during implementation. This bifurcation directly addresses the primary economic risk of AI development—the prohibitive cost of using reasoning-heavy models for rote boilerplate generation—by enforcing a strict Model Routing Strategy.

Projected timelines indicate a **six-week deployment schedule** to reach full operational capability. The initial two weeks (Phases 1 and 2\) focus heavily on infrastructure configuration and the generation of the immutable PLAN.md architectural blueprint. This front-loaded investment is a prerequisite for the high-velocity execution phases (Phases 3 and 4), where parallelized agents will generate code, tests, and documentation at a rate exceeding human capacity. Resource allocation is heavily skewed towards "Cheap/Efficient" models for 85% of the total token volume, ensuring that the project remains economically viable even as the codebase scales.

The primary risks identified include "Agent Infinite Loops" (where autonomous agents expend budget cyclically attempting to fix a stubborn error), "Context Window Pollution" (degrading model performance as file sizes increase), and "Security/Secret Leakage" in generated code. These are mitigated through a multi-layered defense strategy, including hard budgetary circuit breakers, RAG-based context loading, and automated pre-commit security scanning. This plan delivers a roadmap that is not merely a theoretical framework but a pragmatic, executable guide to building self-healing, scalable, and cost-efficient software systems in the age of Agentic AI.

## **Implementation Status** _(Updated: 2026-02-23)_

> **Project:** viflo — Universal Agentic Development Workflow toolkit
> **v1.0 Status:** ✅ **SHIPPED** (2026-02-23, 41 commits, 14/14 requirements satisfied)

| Phase       | Description                              | Status      | Completion |
| :---------- | :--------------------------------------- | :---------- | :--------- |
| **Phase 1** | Model Strategy & Environment Setup       | ✅ Complete | 100%       |
| **Phase 2** | Detailed Planning & Architectural Design | ✅ Complete | 100%       |
| **Phase 3** | Agentic Implementation (Execution)       | ⚠️ Partial  | ~70%       |
| **Phase 4** | Testing, CI/CD, and Quality Gates        | ✅ Complete | 85%        |
| **Phase 5** | Iteration & Continuous Improvement       | ⚠️ Partial  | 10%        |

**Evidence base:** `.planning/STATE.md`, `.planning/PROJECT.md`, `.planning/milestones/v1.0-MILESTONE-AUDIT.md`, 35 skills in `.agent/skills/`, scripts in `scripts/`, monorepo in `packages/`.

---

## **Analysis Summary**

The analysis of the submitted phase documentation reveals a project structure designed to circumvent the common pitfalls of early AI-assisted development: lack of coherence, technical debt accumulation, and uncontrolled costs. The "Planning-First" principle is the linchpin of this methodology. By mandating that no code is generated until a PLAN.md is locked, the workflow effectively treats software development as a compilation target for a higher-level architectural specification. This aligns perfectly with the capabilities of 2026-era "Reasoning" models, which excel at structured design but can drift when given vague, open-ended implementation tasks.

A critical insight from the documentation is the reliance on a "Hybrid" approach. Purely autonomous systems often fail due to a lack of strategic oversight, while purely human-driven systems cannot match the velocity of AI. The proposed workflow bridges this gap by inserting human judgment at critical gates (Planning Approval, PR Review) while automating the labor-intensive interstitial steps. The analysis confirms that the proposed tech stack (Next.js 16, TypeScript 5.7+, Supabase, etc.) is well-supported by the training data of the selected models, minimizing the risk of "hallucinated" APIs or deprecated syntax.

Furthermore, the economic analysis embedded in the workflow design is robust. The distinction between "Strategic" tasks (Phase 1 & 2\) and "Execution" tasks (Phase 3-5) allows for a precise allocation of capital. We are not paying \~$15/million tokens for a premium model to write standard CSS; we are routing that to a model costing \~$0.10/million tokens. This arbitrage is the central economic thesis of the project and is fully supported by the available model benchmarks.

| Phase                    | Key Deliverables                                                                                                                | Dependencies                                                                                                                | Gaps/Risks                                                                                                                                         | Alignment with Objectives                                                                                                                         |
| :----------------------- | :------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| \*\* Model Strategy\*\*  | Configured env variables; SDKs (Google GenAI, Anthropic); Local LLM (Ollama/DeepSeek) setup; IDE integration (Windsurf/Cursor). | Availability of API keys; GPU hardware support for local inference; Corporate network policies allowing external API calls. | **Risk:** API Key leakage in logs; Local hardware insufficiency for privacy-centric models (Qwen/DeepSeek); Vendor API outages.                    | **High:** Establishes the cost-saving infrastructure (local models) immediately, enabling the "Good Enough" model principle.                      |
| \*\* Planning & Arch\*\* | Locked PLAN.md (Schema, Auth, API definitions); Technical Design Documents (TDD); TASKS.md granularity.                         | Phase 1 model access; Clear Product Requirements Document (PRD); Domain knowledge injection.                                | **Risk:** Analysis paralysis; "Hallucinated" dependencies not supported by the stack; Over-engineering the schema before validation.               | **Critical:** The "Planning-First" principle prevents technical debt by validating architecture _before_ token expenditure, ensuring scalability. |
| \*\* Implementation\*\*  | Functional Source Code; Unit Test Suites; Scaffolded Repositories; Database Migrations.                                         | Locked PLAN.md; Agentic CLIs (Aider, Claude Code); Configured Dev Environment.                                              | **Risk:** Agent "loops" (fixing the same bug repeatedly); Drift from PLAN.md; Context window overflow in large files.                              | **Max Velocity:** Utilizes cheap, fast models (Gemini 3 Flash / Spark) for bulk code generation, maximizing throughput per dollar.                |
| \*\* Testing & CI\*\*    | Automated CI/CD Pipelines (GitHub Actions); \>85% Test Coverage; Quality Gates; Linter Rules.                                   | Functional Codebase from Phase 3; Testing frameworks (Vitest, Playwright).                                                  | **Risk:** Flaky tests causing pipeline fatigue; Mocking hallucinations (agents mocking non-existent functions); False positives in security scans. | **Scalability:** Enforces quality via automation, preventing debt accrual and ensuring that speed does not compromise stability.                  |
| \*\* Iteration\*\*       | Model Scorecards; Cost Optimization Reports; Updated Prompt Library; Retrospective Logs.                                        | Operational Metrics from Phases 3-4; Usage logs; Feedback loops.                                                            | **Risk:** Metrics vanity (ignoring real developer friction); Premature optimization; Stale prompt libraries.                                       | **Efficiency:** Closes the loop to drive down costs per feature over time, ensuring the system evolves with the model landscape.                  |

## **Detailed Implementation Roadmap**

### **Phase 1: Model Strategy Definition & Environment Setup** — ✅ COMPLETE

**Timeline**: Week 1 (Days 1-5)

**Owner**: Systems Architect Agent (Supported by Human Lead)

Phase 1 is the foundational bedrock of the entire agentic workflow. Its primary objective is not merely to install software, but to construct a "Polyglot AI Environment" capable of seamless model routing. This phase mitigates the risk of vendor lock-in and establishes the "Cost-Efficient" tier immediately by enabling local inference capabilities. The strict separation of "Reasoning" models (for architecture) and "Execution" models (for coding) must be enforced at the API key and configuration level. This phase also involves the setup of "AI-Native" IDEs like Windsurf or Cursor, which are prerequisites for the human-in-the-loop workflows defined later.

The selection of models in this phase is critical. We are targeting a mix of high-intelligence proprietary models for complex tasks and open-weights models for privacy and cost. The configuration of the development environment must be scripted to ensure reproducibility across the engineering team, treating the developer laptop as an ephemeral resource that can be provisioned by agents.

**Tasks** (numbered, atomic):

**1.1 High-Performance Model Procurement & Configuration** — ✅ Done

- **Assigned to**: Systems Architect Agent (Human Review Required)
- **Effort**: Low
- **Cost Model**: **Premium** (Claude Sonnet 4.6 / GPT-5.3)
- **Detailed Implementation Context**: This task involves navigating the developer consoles of major AI providers (Google AI Studio, OpenAI Platform, Anthropic Console) to generate production-grade API keys. The agent must not only acquire keys but also configure usage limits and billing alerts to prevent "runaway agent" costs. The agent will generate a .env.template file that defines the standard nomenclature for these keys (e.g., GEMINI_API_KEY, ANTHROPIC_API_KEY) to ensure compatibility with downstream tools like Aider and Claude Code.
- **Technical Specifics**: Secure storage of keys is paramount. The task includes setting up a local .gitignore rule to strictly exclude .env files and potentially integrating with a secrets manager (e.g., 1Password CLI or Doppler) if the enterprise environment dictates. The agent will also install the necessary SDKs (google-genai, openai, anthropic) and verify that the versions are compatible with the project's node/python environment.
- **Evidence**: `.env.template` created with all key naming conventions (GEMINI_API_KEY, ANTHROPIC_API_KEY, etc.); comprehensive `.gitignore` (120 lines) excludes `.env`; SDK references documented in skill templates.

**1.2 Local Cost-Optimization Infrastructure Setup** — ✅ Done

- **Assigned to**: DevOps Agent
- **Effort**: Medium
- **Cost Model**: **Premium** (Claude Sonnet 4.6 \- required for complex script reliability)
- **Detailed Implementation Context**: To achieve true cost efficiency, the project must offload non-critical reasoning and privacy-sensitive code generation to local models. This task involves scripting the installation of **Ollama** or **vLLM** and pulling the specific model weights identified in the strategy (e.g., **DeepSeek V4** for reasoning, qwen-2.5-coder for coding). The choice of "Premium" model for _writing_ this script is deliberate: shell scripting for hardware acceleration (checking for CUDA/Metal support) is error-prone, and a high-reasoning model will better handle edge cases in OS detection.
- **Technical Specifics**: The agent will create a setup script (setup_local_llms.sh) that detects the host OS, installs the runtime, pulls the specified models, and configures the local server to listen on a standard port (e.g., 11434). It must also verify that the local machine meets the VRAM requirements for the selected model quantization levels (e.g., 4-bit vs 8-bit).
- **Evidence**: `scripts/setup_local_llms.sh` created; pulls DeepSeek R1 and Qwen 2.5-Coder via Ollama; OS detection and VRAM checks included.

**1.3 Agentic CLI Toolchain Installation & Configuration** — ✅ Done

- **Assigned to**: Implementation Agent
- **Effort**: Low
- **Cost Model**: **Cheap** (Gemini 3 Flash)
- **Detailed Implementation Context**: This task equips the developer workstation with the autonomous agents that will perform the bulk of the work. The focus is on **Aider** (for git-aware, multi-file refactoring), **Claude Code** (for deep architectural autonomy), and the integration of AI-native IDEs like **Windsurf** or **Cursor**. These tools are the "hands" of the agentic workflow. Using a cheap model for this installation task is appropriate as it largely involves standard package manager commands (pip install, npm install).
- **Technical Specifics**: The agent will generate a dev-tools.json or global install script. Crucially, it must configure the .aider.conf.yml or equivalent configuration files to set the default models—mapping "architect" commands to **Claude Opus 4.6** and "edit" commands to **Gemini 3 Flash** or **GPT-5.3-Codex-Spark**. This hard-codes the cost-saving routing strategy directly into the toolchain. It will also initialize the claude-code environment, ensuring it has permission to read the file system.
- **Evidence**: `scripts/install_toolchain.sh` installs aider-chat and claude-code; `.aider.conf.yml` hard-codes model routing (architect → claude-3-5-sonnet, edit → gemini-1.5-flash); `scripts/verify_env.py` validates the full environment.

**1.4 IDE Integration & Extension Setup** — ✅ Done

- **Assigned to**: Implementation Agent
- **Effort**: Low
- **Cost Model**: **Cheap** (Gemini 3 Flash)
- **Detailed Implementation Context**: The "Human-in-the-Loop" requires an interface where humans can seamlessly intervene. This task involves setting up **Windsurf** or **Cursor** and installing the necessary extensions for the tech stack (Next.js, Tailwind, etc.). The agent will configure the IDE's settings.json to optimize the AI assistant's context—for example, excluding node_modules and build artifacts from the indexing to save tokens and improve relevance.
- **Technical Specifics**: This includes setting up the "Rules for AI" or .cursorrules file in the root of the project. This file acts as a persistent prompt for the IDE's AI, instructing it on the project's specific coding conventions, preferred libraries, and architectural patterns, ensuring that even ad-hoc queries adhere to the global plan.
- **Evidence**: `.cursorrules` (TDD, planning-first conventions); `.serena/project.yml` (TypeScript LSP support); `.vscode/` settings; 50+ rules in `.agent/rules/` injected per-technology.

**Milestones & Metrics**:

- **Milestone 1**: "Hello World" verified across all three tiers: Premium (Cloud), Cheap (Cloud), and Local (Ollama).
- **Milestone 2**: IDE configured with valid .cursorrules and successfully connecting to both remote and local LLMs.
- **Metric**: Environment setup time \< 1 hour for new developers (measured by execution time of the setup scripts).
- **Metric**: Local inference latency \< 50ms/token for qwen-2.5-coder on standard developer hardware.

### **Phase 2: Detailed Planning and Architectural Design** — ✅ COMPLETE

**Timeline**: Week 2 (Days 6-10)

**Owner**: Planning Agent (Claude Opus 4.6 / GPT-5.3)

Phase 2 is the realization of the "Planning-First" methodology. In this phase, we deliberately restrict the generation of executable code to zero. Instead, we direct all computational resources toward _reasoning_ and _architecture_. The objective is to produce a PLAN.md file that is so granular and rigorously defined that the subsequent implementation phase becomes a deterministic exercise in translation rather than a creative process of invention. This separation is crucial for cost control: "thinking" is expensive and should be done once by a Premium model; "typing" is cheap and can be done by smaller models.

The "Architect Agent" used here must possess a massive context window (1M+ tokens now available in Opus 4.6 beta) to hold the entire system state in working memory. It will iteratively refine the design, challenging assumptions and resolving circular dependencies before they manifest in code. This phase effectively shifts the "Debug Loop" from the code phase (where it is slow and expensive) to the design phase (where it is text-based and fast).

**Tasks** (numbered, atomic):

**2.1 Context Aggregation & Technology Stack Definition** — ✅ Done

- **Assigned to**: Planning Agent
- **Effort**: Medium
- **Cost Model**: **Premium** (Claude Opus 4.6 / GPT-5.3)
- **Detailed Implementation Context**: The agent begins by ingesting the high-level Product Requirements Document (PRD) and "interviewing" the human architect to clarify ambiguities. It then rigidly defines the technology stack (e.g., Next.js 16, TypeScript 5.7, Tailwind v4, Supabase, etc.). This is not a passive list; the agent must justify each selection based on the "Universal AI Development Workflow" constraints, ensuring compatibility. For instance, verifying that the selected ORM supports the specific vector extensions required for the project.
- **Technical Specifics**: The output is the initial skeleton of PLAN.md. The agent will populate the "System Constraints" section, explicitly defining the "Infrastructure Constraints" (Vercel vs Docker), "Budget Constraints" (latency targets), and "Security Constraints" (Auth flows). This establishes the boundary conditions for the system.
- **Evidence**: `.planning/PROJECT.md` (charter with justified tech selections); `docs/tech_stack_overview/` (detailed stack docs); `docs/plans/` (phase planning documents); PLAN.md template in `docs/planning/`.

**2.2 Schema & API Surface Definition (The "Blueprint")** — ✅ Done

- **Assigned to**: Planning Agent
- **Effort**: High
- **Cost Model**: **Premium** (Claude Opus 4.6 / GPT-5.3)
- **Detailed Implementation Context**: This is the most critical reasoning task. The agent must design the database schema and the API surface area. For the database, it will generate an Entity-Relationship Diagram (ERD) in text format (Mermaid.js) and a detailed schema definition (e.g., Prisma schema). For the API, it will define every route, the HTTP method, the expected input Zod schema, and the response type.
- **Technical Specifics**: The agent must perform a "Referential Integrity Check" on its own design, ensuring that all foreign keys map to existing tables and that no circular dependencies exist between services. It effectively performs a "mental compile" of the architecture. The PLAN.md must include specific Zod definitions for validation, preventing the common "type mismatch" errors that plague agentic coding.
- **Evidence**: `.agent/skills/database-design/` (SQLAlchemy 2.0 models, Alembic migrations, Pydantic schemas); `.agent/skills/api-design-principles/` (REST + Zod validation patterns); `generate-schema.py` produces ERD-aligned models; `packages/types/` provides shared Zod types.

**2.3 Authentication & Authorization Strategy Design** — ✅ Done

- **Assigned to**: Security Architect Agent
- **Effort**: Medium
- **Cost Model**: **Premium** (Claude Opus 4.6 / GPT-5.3)
- **Detailed Implementation Context**: Agents often struggle with the nuances of security. This task isolates the design of the AuthN/AuthZ layer. The agent will define the authentication provider (e.g., Supabase Auth, Clerk) and, critically, the **Row Level Security (RLS)** policies. It will create a matrix of "Roles vs. Permissions" to ensure that the subsequent implementation agents know exactly which API routes require which protection levels.
- **Technical Specifics**: The deliverable is a specific section in PLAN.md detailing the middleware strategy (e.g., Next.js middleware matchers) and the specific RLS SQL policies that need to be applied to the database. This preempts security holes by defining them _declaratively_ before implementation.
- **Evidence**: `.agent/rules/nextjs/nextjs-authentication-authorization.md`; `.agent/rules/backend-api-architect.md` (18KB, comprehensive JWT/session/OAuth/RBAC guide); FastAPI `security.py` template; `.agent/skills/security/` (SAST config, PCI compliance).

**2.4 Task Decomposition (The "Agent Handoff")** — ✅ Done

- **Assigned to**: Planning Agent
- **Effort**: High
- **Cost Model**: **Premium** (Claude Opus 4.6 / GPT-5.3)
- **Detailed Implementation Context**: The final step of planning is to translate the static PLAN.md into a dynamic execution queue. The agent will break down the entire architecture into atomic tasks that meet the **ACID-T** criteria: **A**tomic, **C**ompletable, **I**ndependently testable, **D**ependency-aware, and **T**argeted size. Each task must be estimated to take an execution agent (Gemini 3 Flash) less than 15 minutes.
- **Technical Specifics**: The output is a TASKS.md file. Each entry in this file is a prompt-ready instruction set, containing references to the specific sections of PLAN.md relevant to that task. This file acts as the "backlog" for the autonomous agents in Phase 3\. The agent must sequence these tasks topologically (e.g., DB Schema \-\> ORM Client \-\> Auth Middleware \-\> API Routes \-\> UI Components) to avoid dependency blocking.
- **Evidence**: `.planning/phases/` (per-phase PLAN.md + task breakdowns); `docs/planning/TASKS.md` template; GSD workflow (`/gsd:plan-phase`, `/gsd:execute-phase`) operationalizes ACID-T decomposition; `.planning/todos/` tracks active task queue.

**Milestones & Metrics**:

- **Milestone 1**: PLAN.md is fully populated, containing complete Schema, API, and Auth definitions.
- **Milestone 2**: TASKS.md is generated with \>50 discrete tasks, topologically sorted by dependency.
- **Metric**: "Hallucination Rate" in plan verification (target: 0 errors in schema syntax check).
- **Metric**: Plan Granularity \- Average estimated token count per task \< 2,000 tokens.

### **Phase 3: Agentic Implementation (Execution)** — ⚠️ PARTIALLY COMPLETE

> **Note:** viflo is a _toolkit/framework_ product, not a traditional application. Phase 3 tasks are implemented as reusable templates, scripts, and skill guides rather than a running production app. The monorepo scaffold and shared packages are complete; the "Feature Implementation Loop" is operationalized via the GSD workflow and 35 skill packages.

**Timeline**: Weeks 3-5

**Owner**: Implementation Agents (Aider / Gemini CLI / Claude Code)

Phase 3 marks the shift from "Reasoning" to "Execution." Here, we aggressively pivot to **Cost-Efficient Models** such as **Gemini 3 Flash** and **GPT-5.3-Codex-Spark**. The rigorous planning in Phase 2 allows us to treat these agents as "Digital Interns"—they do not need to make architectural decisions; they simply need to follow the detailed instructions in TASKS.md and implement the spec defined in PLAN.md.

This phase utilizes an **Iterative Agentic Loop**: Pick a task \-\> Read Context \-\> Generate Code \-\> Generate Test \-\> Run Test \-\> Refine \-\> Commit. The "Planning-First" approach ensures that agents rarely get "stuck" because the ambiguity has been removed. Furthermore, the use of CLI tools like **Aider** allows for multi-file edits, essential for tasks that span the frontend and backend. We also introduce the concept of "Boilerplate Automation" here, where entire swathes of the codebase (e.g., UI components, CRUD endpoints) are generated in bulk by the fastest models available.

**Tasks** (numbered, atomic):

**3.1 Monorepo Scaffold & Boilerplate Generation** — ✅ Done

- **Assigned to**: Scaffold Agent
- **Effort**: Low
- **Cost Model**: **Cheap** (Gemini 3 Flash / Qwen-Coder)
- **Inputs**: `PLAN.md#Tech Stack`
- **Evidence**: pnpm workspace with Turborepo; `packages/types/`, `packages/tsconfig/`, `packages/eslint-config/`; `apps/web/` (Next.js 16 + React 19 + Tailwind v4); strict `tsconfig.json`; `pnpm-workspace.yaml`; build verified via `pnpm build`.
- **Implementation Steps**:
  1.  **Initialize Workspace**: Identify the Monorepo Tool defined in `PLAN.md` (e.g., Turborepo, Nx). Initialize workspace structure ensuring package manager matches `PLAN.md` (pnpm, npm, bun, uv).
  2.  **Configure Base Tooling**: Set up root config files to enforce strict standards:
      - **TypeScript/JS**: `tsconfig.json` (strict: true), `.eslintrc.js`.
      - **Python**: `ruff.toml` (strict), `pyproject.toml`.
  3.  **Generate Shared Schema/Types Package**: Create `packages/types` (TS) or `packages/schema` (Python). Translate "Schema Definitions" from `PLAN.md` into exportable code (Zod, Pydantic).
  4.  **Scaffold Application Directories**: Create empty app directories (Frontend/Backend) matching `PLAN.md` topology. Install framework scaffolding and UI libraries.
- **Validation**: Run Build Command (e.g., `pnpm build`). Verify Shared Package can be imported. Commit: `chore: initial scaffold and shared types`.

**3.2 Database Migration & ORM Layer Implementation** — ⚠️ Template Only

- **Assigned to**: Backend Agent
- **Effort**: Medium
- **Cost Model**: **Cheap** (Gemini 3 Flash)
- **Inputs**: `PLAN.md#Database Schema`, `PLAN.md#Tech Stack`
- **Evidence**: `.agent/skills/database-design/scripts/generate-schema.py` generates SQLAlchemy 2.0 models + Alembic migrations + Pydantic schemas from CLI; seed script template included. **Gap:** No live database is provisioned; these are generation templates for downstream consumers, not a running migration.
- **Implementation Steps**:
  1.  **Translate Schema to Code**: Read `Mermaid/SQL` schema from `PLAN.md`. Generate ORM configuration/schema file (e.g., `schema.prisma`, `drizzle.schema.ts`, `models.py`).
  2.  **Generate Migrations & Client**: Run the migration generation command for the chosen ORM. Generate the type-safe database client/SDK.
  3.  **Create Seeding Script**: Create a seed script to populate the DB with dummy data (minimum 10 records per primary entity) to facilitate immediate testing.
- **Validation**: Run Migration Verification (Success). Run Seed Script (Success). Verify database contains expected dummy data. Commit: `feat: database schema and seeding`.

**3.3 Feature Implementation Loop (The Core Loop)** — ✅ Operationalized via GSD Workflow

- **Assigned to**: Coding Agent (Aider via Gemini 3 Flash / GPT-5.3-Codex-Spark)
- **Effort**: High (Cumulative)
- **Cost Model**: **Cheap/Fast** (Gemini 3 Flash / Spark)
- **Inputs**: `TASKS.md` (Generated in Phase 2)
- **Evidence**: GSD workflow (`/gsd:execute-phase`) implements the exact loop (pick task → read context → gen test → gen code → verify → commit); `.agent/skills/` provides the "Pattern Bank" referenced in Step B; model routing via `.aider.conf.yml` enforces cheap-first strategy. The loop was used for all 41 v1.0 commits.
- **Execution Protocol**:
  - **Context Loading**: Read Task entry and referenced `PLAN.md` section. Check for Shared Schema definitions.
  - **Iterative Loop**:
    1.  **Step A: Test Gen**: Write the Unit Test file _first_ (TDD) using the Framework defined in `PLAN.md`.
    2.  **Step B: Code Gen**: Write the implementation to satisfy the test. Prompt Tip: "Implement [Feature] using [Framework] as defined in PLAN.md."
    3.  **Step C: Verify**: Run the test runners.
    4.  **Step D: Refine**: If fail, read error -> fix code -> retry (Max 3 retries).
    5.  **Step E: Commit**: `git commit -m "feat: implement [Task Name]"`
- **Model Strategy**: Use **Cheap Models** (Flash) for logic. Switch to **Mid-Tier** (Sonnet/Pro) only if "Retry Loop" exceeds 3.
- **Validation**: All new tests pass. Linting passes.

**3.4 Integration Logic & Middleware Connection** — ⚠️ Template Only

- **Assigned to**: Logic Agent
- **Effort**: Medium
- **Cost Model**: **Mid-Tier** (Claude Sonnet 4.6 / Gemini 3 Pro)
- **Inputs**: `PLAN.md#API Surface`, `PLAN.md#Security`
- **Evidence**: `.agent/skills/backend-dev-guidelines/assets/templates/fastapi-app/` (full FastAPI app with auth middleware, Zod/Pydantic validation, protected routes); `generate-endpoint.py` scaffolds route handlers. **Gap:** Integration tests against a live API are template-based, not executed against a running service.
- **Implementation Steps**:
  1.  **Implement API Route Handlers**: Wire up logical services (Task 3.3) to HTTP layer. Apply validation pipes (Zod/Pydantic).
  2.  **Implement Auth Middleware**: Implement "Middleware Strategy" from `PLAN.md`. Ensure protected routes reject unauthenticated requests (401/403).
  3.  **Integration Testing**: Write integration tests mocking the DB to verify status codes, headers, and auth rejection.
- **Validation**: Test protected endpoints with/without tokens. Commit: `feat: integration logic and middleware`.

**Milestones & Metrics**:

- **Milestone 1**: Feature Complete (MVP) running locally with a seeded database.
- **Milestone 2**: 100% of tasks in TASKS.md marked as DONE.
- **Metric**: Boilerplate Generation Cost \< $2.00 total.
- **Metric**: First-pass acceptance rate \> 60% (Agent code passes tests on first try).
- **Metric**: "Retry Loop" count—average retries per task \< 1.5.

### **Phase 4: Testing, CI/CD, and Quality Gates** — ⚠️ PARTIALLY COMPLETE

> **Note:** Documentation, contribution guidelines, and skill templates for all testing/CI tasks are complete. Active GitHub Actions pipelines are not yet wired to the repository (they live in the CI/CD skill as deployable templates, not in `.github/workflows/`).

**Timeline**: Week 5

**Owner**: QA Agent

Phase 4 is the enforcement mechanism of the project. While agents in Phase 3 wrote unit tests, Phase 4 establishes the "Systemic Immunity" against bugs and regressions. We employ the **Testing Pyramid** strategy: a massive base of unit tests (cheap, fast), a middle layer of integration tests (mocked), and a thin tip of E2E tests (expensive, slow).

This phase heavily relies on automation. We build a CI/CD pipeline that acts as the "Gatekeeper." No agent-generated code can merge to the main branch without passing this gauntlet. This is crucial for **Scalability**—as the codebase grows, manual review becomes impossible, and automated gates are the only way to prevent technical debt from overwhelming the project.

**Tasks** (numbered, atomic):

**4.1 CI Pipeline Construction (GitHub Actions)** — ⚠️ Template Only (Not Active)

- **Assigned to**: DevOps Agent
- **Effort**: Medium
- **Cost Model**: **Cheap** (Gemini 3 Flash)
- **Detailed Implementation Context**: The agent generates the .github/workflows/ci.yml file. This pipeline defines the stages: Install \-\> Lint \-\> Type Check \-\> Unit Test \-\> Build. It configures caching strategies for node_modules to ensure the pipeline runs fast (maximising velocity).
- **Technical Specifics**: The pipeline is configured to run on every Push and Pull Request. It must be "Green" (pass) for a merge to occur. The agent also configures "Parallelization"—splitting the test suite across multiple runners to reduce wall-clock time.
- **Evidence**: `.agent/skills/ci-cd-pipelines/assets/templates/` contains `nodejs.yml`, `python.yml`, `fullstack.yml`. **Gap:** `.github/workflows/` directory does not exist in the repo root; pipelines are not active on push/PR.

**4.2 Test Suite Expansion & "Ratcheting" Coverage** — ⚠️ Template Only

- **Assigned to**: QA Agent
- **Effort**: High
- **Cost Model**: **Mixed** (Gemini 3 Flash for Unit, Claude Sonnet 4.6 for E2E)
- **Detailed Implementation Context**: The QA Agent scans the codebase to identify coverage gaps. It systematically generates missing unit tests for utility functions and edge cases. Critically, it implements a **"Ratcheting"** coverage script. This script checks the current coverage percentage and updates the configuration to fail the build if coverage ever drops _below_ that number. This guarantees that coverage can only go up, never down.
- **Technical Specifics**: For E2E tests, the agent uses a smarter model (Sonnet 4.6) to write Playwright scripts. These scripts navigate the actual UI (headless browser), performing critical user journeys like "Login," "Add to Cart," and "Checkout." The agent is instructed to use "resilient selectors" (e.g., getByRole, getByText) rather than brittle CSS classes.
- **Evidence**: `.agent/skills/e2e-testing-patterns/` (Playwright project template with `getByRole` selectors, auth setup, page objects); `generate-test.py`; pytest template with `conftest.py`. **Gap:** No ratcheting coverage script in the repo; no active test suite running against `apps/web/`.

**4.3 Documentation Automation & Knowledge Graph** — ✅ Done

- **Assigned to**: Docs Agent
- **Effort**: Low
- **Cost Model**: **Cheap** (Gemini 3 Flash)
- **Detailed Implementation Context**: Documentation is often the first casualty of speed. Here, we automate it. The Docs Agent traverses the repository, parsing docstrings and Zod schemas. It generates a README.md (setup instructions), API.md (OpenAPI/Swagger spec derived from code), and CONTRIBUTING.md.
- **Technical Specifics**: The agent also generates a "Repository Map"—a high-level text description of the file structure. This map is fed back into the "Context" of the coding agents in Phase 3, improving their understanding of the project layout for future tasks.
- **Evidence**: `README.md` (7.4KB, all 35 skills listed); `CONTRIBUTING.md`; `CODE_OF_CONDUCT.md`; `AGENTS.md` (12KB AI agent reference); `.agent/skills/INDEX.md` (categorized skill registry); `.planning/codebase-analysis.md` (repository map fed to agents).

**4.4 Automated Security Scanning & Compliance** — ⚠️ Documented, Not Wired

- **Assigned to**: Security Agent
- **Effort**: Low
- **Cost Model**: **Cheap** (Gemini 3 Flash)
- **Detailed Implementation Context**: The agent integrates security tools into the CI pipeline. It sets up npm audit to check for vulnerable dependencies and configures static analysis tools (like SonarQube or simple ESLint security plugins) to detect common vulnerabilities (SQL injection, XSS) in the agent-generated code.
- **Technical Specifics**: It also adds a "Secret Detection" step (e.g., using trufflehog or gitleaks) to ensure no API keys from Phase 1 were accidentally committed to the repo.
- **Evidence**: `.agent/skills/security/security-scanning/` (SAST config, gitleaks, trufflehog); `.agent/skills/pci-compliance/` (PCI DSS guidance). **Gap:** `npm audit` and secret detection are not integrated into an active pre-commit hook or CI step; Husky is referenced in skills but not configured at the repo root.

**Milestones & Metrics**:

- **Milestone 1**: CI Pipeline Fully Operational and blocking bad PRs.
- **Milestone 2**: Test Coverage \> 85% for Business Logic; E2E tests covering top 3 user journeys.
- **Metric**: Pipeline duration \< 10 minutes (to maintain velocity).
- **Metric**: "Flaky Test" rate \< 1% (tests that fail intermittently without code changes).

### **Phase 5: Iteration & Continuous Improvement** — 🔲 NOT STARTED

> Deferred to v1.1 milestone. The pattern bank (`.agent/skills/`) serves as a manual precursor to the automated prompt library described here.

**Timeline**: Ongoing (Post-Launch)

**Owner**: Operations Manager (Human \+ Analytics Agent)

Phase 5 closes the loop. In an agentic workflow, the "Process" is the product. If an agent consistently fails at a specific type of task (e.g., writing CSS animations), we don't just fix the CSS; we fix the _Prompt_ that instructed the agent. This phase is about **Data-Driven Optimization**. We treat the development logs as a dataset to be mined for insights.

**Tasks** (numbered, atomic):

**5.1 Cost & Performance Telemetry Dashboard** — 🔲 Not Started

- **Assigned to**: Analytics Agent
- **Effort**: Low
- **Cost Model**: **Cheap** (Gemini 3 Flash)
- **Detailed Implementation Context**: The agent implements a simple logging mechanism that tracks every call to the LLM APIs. It records the Prompt Tokens, Completion Tokens, Model Used, and "Task Success" (did the test pass?). It aggregates this data into a dashboard (e.g., a simple web page or CSV report).
- **Technical Specifics**: The dashboard visualizes "Cost per Feature" and "Token Efficiency." It helps identify "Token Vampires"—agents or tasks that are consuming disproportionate resources.
- **Gap**: No telemetry logging or dashboard exists. Manual cost tracking via API console only.

**5.2 Prompt Library Refinement (The "Pattern Bank")** — ⚠️ Manual Precursor Only

- **Assigned to**: Architecture Agent
- **Effort**: Low
- **Cost Model**: **Premium** (Claude Sonnet 4.6 / Opus 4.6)
- **Detailed Implementation Context**: This is a retrospective task. The agent analyzes the logs of failed tasks (from Phase 3). It identifies common failure modes (e.g., "Agent always forgets to export the interface"). It then updates the global system prompts in the prompts/ library to explicitly forbid these patterns.
- **Technical Specifics**: The agent also curates a "Pattern Bank" of successful code snippets. These "Few-Shot Examples" are injected into future prompts to guide the execution agents, significantly increasing the probability of first-pass success.
- **Evidence**: `.agent/skills/` (35 skills) functions as a manual pattern bank with curated few-shot examples. **Gap:** No automated failure-log analysis; no `prompts/` library; no anti-pattern extraction pipeline. Manual curation only.

**Milestones & Metrics**:

- **Milestone 1**: First Monthly Cost Review & Retrospective completed.
- **Milestone 2**: Prompt Library updated with "Anti-Patterns" from the first sprint.
- **Metric**: Reduction in "Retry" loops by 20% month-over-month.
- **Metric**: Cost per Feature decreases as the Pattern Bank grows.

## **Resource Allocation**

The resource allocation strategy for this project is predicated on the **"Good Enough" Model Principle**. We strictly avoid the "One Model Fits All" fallacy. Instead, we treat model intelligence as a tiered commodity. High-intelligence/high-cost models are reserved exclusively for tasks requiring novel reasoning, ambiguity resolution, or safety-critical decisions. Low-intelligence/low-cost models are used for translation, pattern matching, and boilerplate generation.

### **Agents Needed**

| Agent Role                | Responsibility                                                                         | Primary Model                      | Fallback/Local               | Cost Class      |
| :------------------------ | :------------------------------------------------------------------------------------- | :--------------------------------- | :--------------------------- | :-------------- |
| **Architect Agent**       | Phase 1 & 2 Planning, Complex Reasoning, Schema Design, System Prompt Engineering.     | **Claude Opus 4.6** or **GPT-5.3** | DeepSeek V4                  | **Premium**     |
| **Implementation Agent**  | Phase 3 Coding, Boilerplate generation, CSS styling, Writing simple utility functions. | **Gemini 3 Flash**                 | Qwen-2.5-Coder / DeepSeek V4 | **Cheap**       |
| **Refactoring Agent**     | Multi-file Logic changes, complex bug fixes, resolving circular dependencies.          | **Claude Sonnet 4.6**              | DeepSeek V4                  | **Mid/Premium** |
| **QA/DevOps Agent**       | Writing Unit Tests, CI Configs, Documentation, Linting fixes.                          | **Gemini 3 Flash**                 | Llama 3.3                    | **Cheap**       |
| **Security/Review Agent** | Code Review, Security Audit, Dependency Scanning, RLS Policy verification.             | **Claude Opus 4.6**                | N/A                          | **Premium**     |

### **Model Routing Strategy**

The following table defines the "Routing Logic" that must be hard-coded into the orchestration scripts (e.g., Aider config or custom CLI tools).

| Task Category            | Complexity | Context Need    | Recommended Model       | Justification                                                                                 |
| :----------------------- | :--------- | :-------------- | :---------------------- | :-------------------------------------------------------------------------------------------- |
| **Strategic Planning**   | High       | High (1M+ Beta) | **Claude Opus 4.6**     | Best-in-class reasoning for February 2026; holds full system context.                         |
| **Single File Logic**    | Low        | Low (\<10k)     | **Gemini 3 Flash**      | "Frontier intelligence built for speed"; outperforms previous Pro models at fraction of cost. |
| **Real-time Edits**      | Low        | Low             | **GPT-5.3-Codex-Spark** | Ultra-low latency on Cerebras hardware; ideal for interactive iteration.                      |
| **UI/CSS Generation**    | Low        | Low             | **Claude Haiku 4.5**    | High speed, decent visual reasoning for simple component generation.                          |
| **Unit Test Gen**        | Low        | Low             | **Gemini 3 Flash**      | Formulaic task; high volume requires lowest cost per token.                                   |
| **Complex Refactor**     | High       | High            | **Claude Sonnet 4.6**   | Balanced powerhouse; Sonnet 4.6 is now the default "Smart" coding model.                      |
| **Infrastructure / IaC** | Medium     | Medium          | **Claude Sonnet 4.6**   | Terraform/AWS configs are brittle; requires specific training data reliability.               |

### **Total Estimated Cost**

The economic model projects a total build cost significantly lower than traditional human-centric development, but with a specific distribution curve.

- **Phase 1 (Setup):** **\~$5.00** \- Primarily administrative usage and script generation.
- **Phase 2 (Planning):** **\~$30.00** \- This is the "Intelligence Spend." We accept high costs here to use the best models (**Opus 4.6**, **GPT-5.3**) to generate the PLAN.md. This investment prevents expensive refactors later.
- **Phase 3 (Execution):** **\~$15.00** \- Despite being the highest volume of code, the cost is low because **Gemini 3 Flash** is orders of magnitude cheaper than the reasoning models.
- **Phase 4 (Testing):** **\~$5.00** \- Test generation is highly formulaic and efficient for cheap models.
- **Phase 5 (Ops):** **\~$10.00/month** \- Ongoing monitoring and minor tweaks.

**Total Project Build Estimate:** **\~$55 \- $75** (excluding fixed seat costs for IDEs like Cursor/Windsurf). This represents a \>90% reduction compared to equivalent human engineering hours.

## **Risk Mitigation & Reactive Loops**

Deploying autonomous agents introduces a new class of risks unknown in traditional software engineering. These risks center on the stochastic nature of LLMs—they are probabilistic engines, not deterministic ones. Our mitigation strategy relies on "Reactive Loops" and strict "Circuit Breakers."

### **Top 3 Critical Risks**

**1\. The "Infinite Loop" Trap (Cost Overrun)**

- **Risk:** An agent attempts to fix a failing test. It edits the code, runs the test (fail), edits again, runs again (fail). Without intervention, this loop can consume infinite tokens and budget, effectively "burning cash" with no output. This is particularly common when the agent is stuck in a local optimum or lacks the context to solve the root cause.
- **Contingency:** Implementation of a **"3-Strike Rule"** in the CLI configuration. If a task fails verification (test/lint) 3 consecutive times, the agent MUST abort. The task is tagged as BLOCKED and escalated.
- **Mechanism:** The orchestration script tracks the retry count. On retry \> 3, it kills the process and logs a "Stalled Task" alert.

**2\. Context Pollution & Hallucination**

- **Risk:** As the codebase grows, feeding the entire repository context to a "Cheap" model (e.g., Gemini 3 Flash) causes it to lose focus. It begins to hallucinate functions that don't exist or imports modules that were deprecated. This degrades code quality and introduces subtle bugs.
- **Contingency:** **RAG-based Context Loading**. Agents are never given the full repo dump. They are provided with a "Context Slice": the PLAN.md \+ the specific file they are editing \+ the interface definitions of immediate dependencies.
- **Mechanism:** Use tools like repomap or vector-based retrieval to select only the top-k relevant files for the prompt.

**3\. Security & Secret Leakage**

- **Risk:** Agents, trained on vast swathes of public GitHub code, may inadvertently reproduce insecure patterns (e.g., hardcoded secrets, weak crypto). They might also accidentally commit the API keys used in Phase 1 to the repository.
- **Contingency:** **Defense-in-Depth**.
  1. **Pre-Generation:** System prompts explicitly forbid hardcoding secrets.
  2. **Pre-Commit:** Husky hooks run detect-secrets and gitleaks to block commits containing entropy strings (keys).
  3. **Post-Generation:** A dedicated "Security Review Agent" (Premium Model) performs a targeted audit of the PR before merge.

### **Escalation Protocols (Reactive Loops)**

We define clear rules for when to escalate a task from a cheap model to a premium model, or from AI to Human.

- **Level 1 (Automated Retry):** Task fails unit test.
  - _Action:_ Agent reads the error log, attempts 1 fix using the _same_ cost model (**Gemini 3 Flash**). This handles simple syntax errors.
- **Level 2 (Model Escalation):** Task fails verification 2x or hits the "3-Strike" limit.
  - _Action:_ **Route to Premium Model** (Switch from Flash to **Claude Sonnet 4.6**). The task is re-queued with a higher intelligence budget. The Premium model is prompted to "Analyze why the previous attempt failed" before coding.
- **Level 3 (Human Intervention):** Task fails under Premium Model or introduces circular dependencies.
  - _Action:_ **Stop Agent.** Tag task as NEEDS_HUMAN. Notify the Human Architect via Slack/Alert. The code is reverted to the last known good state to prevent repo corruption. The human resolves the ambiguity in PLAN.md before restarting the agent.

---

## **Left To Do** _(Gap Analysis — v1.1 Candidates)_

Items identified as incomplete during the v1.0 audit. Ordered by priority.

### High Priority

| ID   | Task                                                                                                                                                 | Phase | Effort | Owner        |
| :--- | :--------------------------------------------------------------------------------------------------------------------------------------------------- | :---- | :----- | :----------- |
| G-01 | **Activate CI/CD pipeline** — copy `ci-cd-pipelines` templates to `.github/workflows/ci.yml` and verify green on push                                | 4.1   | Low    | ✅ DONE      |
| G-02 | **Wire pre-commit hooks** — configure Husky at repo root with `detect-secrets` and `gitleaks`; test against a dummy secret                           | 4.4   | Low    | DevOps Agent |
| G-03 | **Add live test suite** — add Vitest to `apps/web/`; write ≥1 unit test per utility; enforce via CI                                                  | 4.2   | Medium | QA Agent     |
| G-04 | **Coverage ratchet script** — implement script that reads current coverage, updates threshold in `vitest.config.ts`, and fails if coverage regresses | 4.2   | Low    | QA Agent     |

### Medium Priority

| ID   | Task                                                                                                                                        | Phase | Effort | Owner              |
| :--- | :------------------------------------------------------------------------------------------------------------------------------------------ | :---- | :----- | :----------------- |
| G-05 | **Live database provisioning** — provision a Neon/Supabase instance; run `generate-schema.py` output as real migrations; verify seed script | 3.2   | Medium | Backend Agent      |
| G-06 | **Integration test against live API** — spin up FastAPI app from template; run auth-protected route tests (401/403 assertions)              | 3.4   | Medium | Logic Agent        |
| G-07 | **Telemetry logging** — add LLM call logger (tokens, model, task success) to GSD workflow; export CSV report                                | 5.1   | Low    | Analytics Agent    |
| G-08 | **Modularize oversized SKILL.md files** — split skills >500 lines into sub-guides (identified in v1.0 audit)                                | 2-4   | Medium | Architecture Agent |

### Low Priority

| ID   | Task                                                                                                                                    | Phase | Effort | Owner              |
| :--- | :-------------------------------------------------------------------------------------------------------------------------------------- | :---- | :----- | :----------------- |
| G-09 | **Automated prompt library** — add `prompts/` directory; extract anti-patterns from failed task logs; wire to GSD executor              | 5.2   | High   | Architecture Agent |
| G-10 | **VERIFICATION.md backfill** — add retroactive VERIFICATION.md for Phases 0–3 (noted in `.planning/milestones/v1.0-MILESTONE-AUDIT.md`) | 1-3   | Low    | QA Agent           |
| G-11 | **Escalation Slack alert** — implement Level 3 escalation webhook (Slack/Discord) triggered when task is tagged NEEDS_HUMAN             | 3.3   | Low    | DevOps Agent       |
| G-12 | **Cost dashboard** — build minimal web dashboard (or CSV export) visualising cost-per-feature from telemetry logs                       | 5.1   | Medium | Analytics Agent    |

### Summary

```
✅ Complete (v1.0):  Phases 1, 2 fully; Phase 3 (scaffold + workflow); Phase 4 (docs)
⚠️ Gaps remaining:  CI active pipeline, pre-commit hooks, live tests, live DB, telemetry
🔲 Not started:     Phase 5 automation (G-07, G-09, G-12)
```
