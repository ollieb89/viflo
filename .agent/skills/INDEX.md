# Skills Index

> Complete reference for all available skills in `.agent/skills/`.
> Select a skill based on your current task, then read its SKILL.md.

---

## How to Use Skills

1. Find the skill matching your task in the tables below
2. Load the skill: `@.agent/skills/<skill-name>/SKILL.md`
3. Follow the skill's instructions — read only referenced sub-files as needed

### Extended Content

Skills marked with 📚 have extended content in `references/` subdirectories:
- `references/guides/` — Detailed implementation guides
- `references/examples/` — Code examples and templates  
- `references/checklists/` — Verification and review checklists

---

## Skills by Category

### API Design

| Skill                                                   | Description                                                       | Difficulty   | When to Use                         |
| ------------------------------------------------------- | ----------------------------------------------------------------- | ------------ | ----------------------------------- |
| [api-design-principles](api-design-principles/SKILL.md) 📚 | REST and GraphQL design patterns, versioning, pagination, HATEOAS | Intermediate | Designing new APIs, reviewing specs |
| [api-patterns](api-patterns/SKILL.md)                   | API style selection (REST/GraphQL/tRPC), response formats, auth   | Beginner     | Choosing API style, quick reference |

### Architecture

| Skill                                                     | Description                                                         | Difficulty | When to Use                                 |
| --------------------------------------------------------- | ------------------------------------------------------------------- | ---------- | ------------------------------------------- |
| [architectural-design](architectural-design/SKILL.md)     | Generate PLAN.md and TASKS.md using planning-first methodology      | Beginner   | Starting new project or feature             |
| [architecture-patterns](architecture-patterns/SKILL.md)   | Clean Architecture, Hexagonal Architecture, Domain-Driven Design    | Advanced   | Complex system design, refactoring          |
| [microservices-patterns](microservices-patterns/SKILL.md) | Service boundaries, event-driven communication, resilience patterns | Advanced   | Distributed systems, monolith decomposition |

### Backend Development

| Skill                                                       | Description                                                  | Difficulty   | When to Use                         |
| ----------------------------------------------------------- | ------------------------------------------------------------ | ------------ | ----------------------------------- |
| [backend-dev-guidelines](backend-dev-guidelines/SKILL.md)   | FastAPI + SQLAlchemy 2.0 + Pydantic v2 development standards | Intermediate | Python/FastAPI projects             |
| [fastapi-templates](fastapi-templates/SKILL.md) 📚             | Production-ready FastAPI with async, DI, repository pattern  | Intermediate | Starting new FastAPI applications   |
| [nodejs-backend-patterns](nodejs-backend-patterns/SKILL.md) 📚 | Node.js/Express/Fastify patterns, middleware, auth, database | Intermediate | Node.js REST APIs and microservices |

### CI/CD and DevOps

| Skill                                         | Description                                                 | Difficulty   | When to Use                         |
| --------------------------------------------- | ----------------------------------------------------------- | ------------ | ----------------------------------- |
| [ci-cd-pipelines](ci-cd-pipelines/SKILL.md)   | GitHub Actions workflows for Python, Node.js, full-stack    | Beginner     | Setting up CI/CD pipelines          |
| [cloud-deployment](cloud-deployment/SKILL.md) | Vercel, Railway, AWS deployment guides with SSL and domains | Beginner     | Deploying applications to the cloud |
| [containerization](containerization/SKILL.md) | Docker multi-stage builds, security, production patterns    | Intermediate | Containerizing applications         |

### Database

| Skill                                       | Description                                                        | Difficulty   | When to Use                                   |
| ------------------------------------------- | ------------------------------------------------------------------ | ------------ | --------------------------------------------- |
| [database-design](database-design/SKILL.md) | PostgreSQL + SQLAlchemy 2.0 schema design, migrations, indexes     | Intermediate | Schema design, migrations, query optimization |
| [postgresql](postgresql/SKILL.md)           | PostgreSQL-specific: data types, indexes, partitioning, JSONB, RLS | Advanced     | Deep PostgreSQL work                          |

### Frontend Development

| Skill                                                       | Description                                              | Difficulty   | When to Use                           |
| ----------------------------------------------------------- | -------------------------------------------------------- | ------------ | ------------------------------------- |
| [frontend-dev-guidelines](frontend-dev-guidelines/SKILL.md) | React/TypeScript/MUI v7, Suspense, TanStack Query/Router | Intermediate | React frontend projects               |
| [frontend-design](frontend-design/SKILL.md)                 | Distinctive UI creation, typography, color, animation    | Intermediate | Building visually striking interfaces |

### Methodology and Workflow

| Skill                                         | Description                                                      | Difficulty   | When to Use                                   |
| --------------------------------------------- | ---------------------------------------------------------------- | ------------ | --------------------------------------------- |
| [app-builder](app-builder/SKILL.md)           | Scaffold full-stack apps from natural language requests          | Beginner     | Starting a new application                    |
| [behavioral-modes](behavioral-modes/SKILL.md) | Agent operational modes: Brainstorm, Implement, Debug, Review    | Beginner     | Setting agent behavior                        |
| [brainstorming](brainstorming/SKILL.md)       | Socratic questioning, progress reporting, communication protocol | Beginner     | Clarifying requirements before implementation |
| [gsd-workflow](gsd-workflow/SKILL.md)         | Get Shit Done spec-driven development methodology                | Intermediate | Structured project planning and execution     |
| [skill-creator](skill-creator/SKILL.md)       | Create and update skills following best practices                | Intermediate | Adding new capabilities                       |
| [skill-depth-standard](skill-depth-standard/SKILL.md) | Rubric and checklist for auditing and writing deep skills        | Intermediate | Auditing and improving skill quality          |
| [writing-skills](writing-skills/SKILL.md) 📚     | Test-driven approach to skill documentation                      | Advanced     | Verifying skills work correctly               |

### Quality and Testing

| Skill                                                       | Description                                                      | Difficulty   | When to Use                     |
| ----------------------------------------------------------- | ---------------------------------------------------------------- | ------------ | ------------------------------- |
| [code-review-excellence](code-review-excellence/SKILL.md) 📚   | Effective code review practices and feedback techniques          | Beginner     | Reviewing pull requests         |
| [debugging-strategies](debugging-strategies/SKILL.md) 📚       | Systematic debugging, profiling, root cause analysis             | Intermediate | Tracking down bugs              |
| [e2e-testing-patterns](e2e-testing-patterns/SKILL.md) 📚       | Playwright and Cypress patterns, Page Objects, fixtures          | Intermediate | E2E test implementation         |
| [error-handling-patterns](error-handling-patterns/SKILL.md) 📚 | Exceptions, Result types, circuit breakers, graceful degradation | Intermediate | Building resilient applications |
| [temporal-python-testing](temporal-python-testing/SKILL.md) | Temporal workflow testing with pytest, time-skipping, mocking    | Advanced     | Temporal workflow test coverage |

### Authentication

| Skill                                       | Description                                                        | Difficulty   | When to Use                                   |
| ------------------------------------------- | ------------------------------------------------------------------ | ------------ | --------------------------------------------- |
| [auth-systems](auth-systems/SKILL.md)       | Clerk and Auth.js/NextAuth authentication, sessions, RBAC          | Intermediate | Adding auth to Next.js or Node.js applications |

### Payments

| Skill                                             | Description                                                              | Difficulty   | When to Use                                        |
| ------------------------------------------------- | ------------------------------------------------------------------------ | ------------ | -------------------------------------------------- |
| [stripe-payments](stripe-payments/SKILL.md)       | Stripe checkout, subscriptions, webhooks, and billing lifecycle          | Intermediate | Implementing payment flows and subscription billing |

### AI/LLM

| Skill                                                       | Description                                                              | Difficulty   | When to Use                                      |
| ----------------------------------------------------------- | ------------------------------------------------------------------------ | ------------ | ------------------------------------------------ |
| [rag-vector-search](rag-vector-search/SKILL.md)             | Embedding pipelines, pgvector/Pinecone, retrieval-augmented generation   | Advanced     | Building semantic search or RAG applications     |
| [agent-architecture](agent-architecture/SKILL.md)           | Multi-agent systems, memory patterns, orchestration frameworks           | Advanced     | Designing autonomous agents and multi-agent flows |
| [prompt-engineering](prompt-engineering/SKILL.md)           | Prompt templates, evaluation, chain-of-thought, anti-patterns            | Intermediate | Optimizing LLM prompts and evaluating quality    |

### Security

| Skill                                                             | Description                                              | Difficulty   | When to Use                  |
| ----------------------------------------------------------------- | -------------------------------------------------------- | ------------ | ---------------------------- |
| [pci-compliance](pci-compliance/SKILL.md)                         | PCI DSS requirements for payment card data               | Advanced     | Securing payment processing  |
| [security/security-scanning](security/security-scanning/SKILL.md) | SAST configuration and automated vulnerability detection | Intermediate | Setting up security scanning |

### TypeScript

| Skill                                                           | Description                                                  | Difficulty | When to Use                   |
| --------------------------------------------------------------- | ------------------------------------------------------------ | ---------- | ----------------------------- |
| [typescript-advanced-types](typescript-advanced-types/SKILL.md) 📚 | Generics, conditional types, mapped types, template literals | Advanced   | Complex TypeScript type logic |

### Documentation

| Skill                                                 | Description                      | Difficulty | When to Use                        |
| ----------------------------------------------------- | -------------------------------- | ---------- | ---------------------------------- |
| [github-readme-writer](github-readme-writer/SKILL.md) | GitHub-optimized README creation | Beginner   | Creating or improving README files |

### Specialized

| Skill                                                                       | Description                                                 | Difficulty   | When to Use                                      |
| --------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------ | ------------------------------------------------ |
| [git-advanced-workflows](git-advanced-workflows/SKILL.md)                   | Rebase, cherry-pick, bisect, worktrees, reflog              | Intermediate | Complex Git history management                   |
| [i18n-implementation](i18n-implementation/SKILL.md)                         | Internationalization with next-i18next, RTL support         | Intermediate | Adding multi-language support                    |
| [monorepo-management](monorepo-management/SKILL.md) 📚                         | Turborepo/Nx/pnpm workspace management                      | Intermediate | Multi-package repository setup                   |
| [workflow-orchestration-patterns](workflow-orchestration-patterns/SKILL.md) | Temporal durable workflows, saga patterns, state management | Advanced     | Long-running processes, distributed transactions |

---

## Quick Selection Guide

**"I need to build a new app"**
→ Start with `app-builder` or `architectural-design`

**"I need to design an API"**
→ Use `api-patterns` for style selection, `api-design-principles` for deep patterns

**"I need to write backend code"**
→ Python: `backend-dev-guidelines` or `fastapi-templates`
→ Node.js: `nodejs-backend-patterns`

**"I need to design a database schema"**
→ `database-design` for general patterns, `postgresql` for PostgreSQL specifics

**"I need to set up CI/CD"**
→ `ci-cd-pipelines` for GitHub Actions templates

**"I need to deploy my application"**
→ `cloud-deployment` for platform guides, `containerization` for Docker

**"I need to write frontend code"**
→ `frontend-dev-guidelines` for React/TypeScript, `frontend-design` for UI creation

**"I need to fix a bug"**
→ `debugging-strategies`

**"I need to write tests"**
→ `e2e-testing-patterns` for E2E, check specific framework skill for unit tests

**"I need to review code"**
→ `code-review-excellence`

**"I need to make my app secure"**
→ `pci-compliance` for payments, `security/security-scanning` for SAST

---

## Skill Conventions

All skills follow this structure:

```
skill-name/
├── SKILL.md          # Required: Instructions, triggers, metadata
├── scripts/          # Optional: Executable scripts
├── references/       # Optional: Detailed reference documentation
├── assets/           # Optional: Templates and boilerplate
└── resources/        # Optional: Additional guides
```

**Frontmatter fields:**

- `name`: Unique identifier (matches directory name)
- `description`: When to use this skill (also shown in agent tool descriptions)
- `triggers`: List of situations that call for this skill
- `allowed-tools`: Optional list of permitted tools
