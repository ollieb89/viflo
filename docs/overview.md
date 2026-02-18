# Project Viflo: Development Master Plan

## 🛠️ Core Project Pillars

This project follows a strict **Hybrid, Planning-First, Agentic** methodology designed to maximize velocity while minimizing cost and technical debt.

1.  **Hybrid Model Strategy**: Leveraging the specific strengths of different LLMs (Proprietary for reasoning, Open-Source for execution).
2.  **Structured Planning**: No code is written without a granular, pre-approved `PLAN.md`.
3.  **Agentic Workflow**: Implementation is granular, test-driven, and executed by specialized CLI agents.

---

## 📅 Execution Phases

### [Phase 1: Model Strategy & Selection](./plans/phase_01.md)
**Status:** ✅ **Rewritten & Active**
**Focus:** Defining the LLM portfolio.
-   **Proprietary Models:** Gemini 3 Pro, GPT-5.2, Claude Opus 4.5 for high-reasoning tasks.
-   **Execution Models:** GPT-5 Mini, Claude Sonnet 4.5, Gemini 3 Flash for code generation.
-   **Open-Source Models:** Qwen, DeepSeek V3 for local/private tasks.

### [Phase 2: Planning & Architectural Design](./plans/phase_02.md)
**Status:** ✅ **Rewritten & Active**
**Focus:** The Protocol for generating the `PLAN.md`.
-   **Template Structure:** Detailed 9-section template for system design.
-   **Context Prompts:** specific context to feed the planning model (Tech Stack, Constraints).
-   **Refinement Process:** Iterative loop to ensure the plan is "Specific, Actionable, Granular".

### [Phase 3: Implementation Workflow](./plans/phase_03.md)
**Status:** ✅ **Rewritten & Active**
**Focus:** The protocol for converting `PLAN.md` into code.
-   **Task Granulation:** Breaking features into ACID-T units (Atomic, Completable, Independently Testable).
-   **Agent Selection:** Routing tasks to the most cost-effective capable agent.
-   **Review Cycle:** Strict "Human-in-the-Loop" review checklist for every artifact.

### [Phase 4: Testing & Continuous Integration](./plans/phase_04.md)
**Status:** ✅ **Rewritten & Active**
**Focus:** Automated verification and quality gates.
-   **Test Strategy:** Testing pyramid, tooling by ecosystem, coverage targets per layer.
-   **AI-Assisted Test Generation:** Prompting templates and quality criteria for LLM-generated tests.
-   **Code Quality Enforcement:** Linting, formatting, pre-commit hooks (Husky / pre-commit).
-   **CI/CD Pipeline:** GitHub Actions stages (install → lint → build → test → E2E → deploy).
-   **Cost & Performance Monitoring:** Token usage, agent success rate, pipeline latency, cost optimization triggers.

### [Phase 5: Iteration & Continuous Improvement](./plans/phase_05.md)
**Status:** ✅ **Rewritten & Active**
**Focus:** The feedback loop that evolves the workflow.
-   **Post-Sprint Retrospective:** Structured 45-min review protocol with metrics, assessment, and action items.
-   **Model Performance Evaluation:** Per-model scorecards, comparison matrices, and decision trees for model swaps.
-   **Cost Optimization Loop:** Budget allocation framework, cost reduction strategies, and monthly cost reviews.
-   **Workflow Refinement:** Data-driven improvements to planning, implementation, and testing processes (Phases 2–4).
-   **Model Reassessment & Migration:** Quarterly benchmarking, internal test suite, safe migration protocol.
-   **Knowledge Management:** Prompt library, pattern library, and institutional memory practices.
-   **Scaling:** Onboarding new projects, team members, and multi-project governance.

---

## 🚀 Key Objectives

-   **Maximize Velocity:** Automate boilerplate and testing.
-   **Cost Efficiency:** Route simple tasks to cheaper models.
-   **Scalability:** Maintain a clean, documented architecture.
