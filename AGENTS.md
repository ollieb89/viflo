# Viflo: Universal Agentic Development Environment

> **AI Coding Agent Reference Guide**

This document provides essential information for AI coding agents working on the Viflo project. Viflo is a comprehensive development methodology and toolchain designed to standardize and accelerate agentic software development.

---

## Project Overview

**Viflo** (short for "Visual Flow") is a development methodology and supporting infrastructure that enables hybrid AI-human software development. The core philosophy centers on:

- **Hybrid Model Strategy**: Route tasks to the most cost-effective capable model—premium models (Claude Opus, GPT-5, Gemini Pro) for planning and reasoning; cheap/fast models (Gemini Flash, GPT-Mini) for execution
- **Planning-First**: No code is written without a pre-approved, granular `PLAN.md`
- **Agentic Workflow**: Implementation is broken down into atomic, independently testable units executed by specialized CLI agents
- **5-Phase Lifecycle**: Model Strategy → Planning → Implementation → Testing/CI → Continuous Improvement

### Key Directories

| Directory              | Purpose                                                   |
| ---------------------- | --------------------------------------------------------- |
| `docs/`                | Comprehensive documentation of Viflo phases and protocols |
| `docs/plans/`          | Operational plans for each of the 5 phases                |
| `docs/implementation/` | Detailed implementation guides                            |
| `docs/planning/`       | PLAN.md and TASKS.md templates                            |
| `scripts/`             | Environment setup and verification automation             |
| `.agent/`              | AI agent configuration, rules, skills, and workflows      |
| `.agent/agents/`       | Agent persona definitions                                 |
| `.agent/rules/`        | Coding rules organized by technology/domain               |
| `.agent/skills/`       | Reusable skill packages with SKILL.md files               |
| `.agent/workflows/`    | Workflow definitions for common operations                |
| `packages/`            | Shared packages (types, tsconfig, eslint-config)          |

---

## Technology Stack

This repository uses a **monorepo structure** with the following technologies:

### Package Management

- **pnpm** (>=10.0.0) - Primary package manager
- Lockfile: `pnpm-lock.yaml`

### Supported Tech Stacks (for projects built with Viflo)

| Layer    | Technologies                                              |
| -------- | --------------------------------------------------------- |
| Frontend | Next.js 16, React 18/19, TypeScript 5.7+, Tailwind CSS v4 |
| Backend  | Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic           |
| Database | PostgreSQL, Redis, PGVector                               |
| Mobile   | React Native 0.73+, Expo SDK 50                           |
| Testing  | Vitest, Playwright, pytest                                |
| AI/ML    | PyTorch, Unsloth, Transformers, vLLM                      |

### Development Tools

- **Aider** - Multi-file git-aware refactoring
- **Claude Code** - Autonomous coding tasks
- **Ollama** - Local LLM execution (DeepSeek R1, Qwen 2.5-Coder)

---

## Project Configuration

### Environment Variables

Required API keys (see `.env.template`):

```bash
# Premium Models
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
XAI_API_KEY=

# Optional: Secrets Manager
DOPPLER_TOKEN=
```

### Aider Configuration (`.aider.conf.yml`)

```yaml
model: gemini/gemini-1.5-flash
architect: true
architect-model: anthropic/claude-3-5-sonnet-20241022
editor-model: gemini/gemini-1.5-flash
weak-model: gemini/gemini-1.5-flash
cache-prompts: true
```

### Cursor Rules (`.cursorrules`)

- Stack: Next.js, Python, TypeScript
- ALWAYS use implementation plans in `docs/implementation/`
- DO NOT invent new patterns
- Test Driven Development (TDD) is mandatory

---

## Build and Development Commands

### Environment Setup

```bash
# 1. Install toolchain (Aider, Claude Code)
./scripts/install_toolchain.sh

# 2. Setup local LLMs (Ollama + models)
./scripts/setup_local_llms.sh

# 3. Verify environment
python3 scripts/verify_env.py

# 4. Copy and fill environment variables
cp .env.template .env
```

### Package Management

```bash
# Install dependencies
pnpm install

# No build command for this meta-project (it's documentation/tooling)
```

---

## Code Style Guidelines

### General Principles

1. **Follow Existing Patterns**: Check `.agent/rules/` for technology-specific rules
2. **Conciseness**: The context window is a public good—keep code and documentation concise
3. **Test-Driven Development**: Write tests first, then implementation
4. **Type Safety**: Strict TypeScript (`strict: true`) and Python type hints

### File Organization

- **Co-located tests**: Unit tests live next to source files (`.test.ts`, `test_*.py`)
- **E2E tests**: Separate `tests/e2e/` directory
- **Skills**: Each skill is a self-contained directory with `SKILL.md`
- **Rules**: Organized by domain in `.agent/rules/`

### Naming Conventions

- **Files**: kebab-case for multi-word files
- **Components**: PascalCase (React/Vue)
- **Functions/Variables**: camelCase (JS/TS), snake_case (Python)
- **Constants**: UPPER_SNAKE_CASE

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

types: feat, fix, refactor, test, chore, docs, style, perf
```

Examples:

- `feat: add user authentication flow`
- `fix: handle null avatar URL in profile card`
- `test: add unit tests for user service`

---

## Testing Instructions

### Testing Philosophy

- **Testing Pyramid**: Many unit tests, moderate integration tests, few E2E tests
- **Coverage Targets**:
  - Business logic: 85%
  - API route handlers: 80%
  - UI components: 70%
  - Utilities: 90%

### Running Tests

This is a documentation/tooling repository; specific test commands depend on the project being built. Standard patterns:

```bash
# JavaScript/TypeScript
vitest run
playwright test

# Python
pytest
pytest --cov
```

### Pre-Commit Quality Gates

Before any commit:

- [ ] All lint rules pass
- [ ] Type checking passes
- [ ] Related unit tests pass
- [ ] No secrets or credentials in code

---

## Security Considerations

### Secret Management

- NEVER hardcode API keys, tokens, or credentials
- Use environment variables (`.env` file, excluded from git)
- Pre-commit hooks run secret detection (detect-secrets, gitleaks)

### Security Review Checklist

For every AI-generated artifact:

- [ ] No hardcoded secrets, tokens, or credentials
- [ ] Input validation at API boundaries
- [ ] Auth checks on protected routes/endpoints
- [ ] No SQL injection, XSS, or CSRF vulnerabilities

### RLS (Row Level Security)

When working with databases:

- Default deny policy
- Explicit policies for each role/permission
- Audit trails for healthcare/financial data

---

## Model Routing Strategy

When generating code or performing tasks, use this decision matrix:

| Task Type              | Model Tier | Examples                               |
| ---------------------- | ---------- | -------------------------------------- |
| Planning, Architecture | Premium    | Claude Opus 4.6, GPT-5.3, Gemini 3 Pro |
| Complex Reasoning      | Premium    | Schema design, system architecture     |
| Multi-file Refactoring | Mid        | Claude Sonnet 4.6, Gemini 2.5 Pro      |
| Single-file Generation | Cheap      | Gemini 3 Flash, GPT-5 Mini             |
| Boilerplate/Code Gen   | Cheap      | Component scaffolding, CRUD endpoints  |
| Test Generation        | Cheap      | Unit tests, test fixtures              |
| Privacy-sensitive      | Local      | Qwen, DeepSeek via Ollama              |

### Escalation Protocol

1. **Level 1 (Retry)**: Task fails → Retry with same model (1 attempt)
2. **Level 2 (Escalate)**: Fails 2x → Switch to Premium model
3. **Level 3 (Human)**: Premium fails → Tag as NEEDS_HUMAN, notify architect

---

## Working with Skills

### Skill Structure

```
skill-name/
├── SKILL.md          # Required: Instructions and metadata
├── scripts/          # Optional: Executable scripts
├── references/       # Optional: Documentation references
├── resources/        # Optional: Extended guides and topic deep-dives
└── assets/           # Optional: Templates, boilerplate
```

### Creating a New Skill

1. Run `.agent/skills/skill-creator/scripts/init_skill.py <name> --path <dir>`
2. Edit `SKILL.md` with proper frontmatter (`name`, `description`, `triggers`)
3. Add scripts/references/assets as needed
4. Package with `.agent/skills/skill-creator/scripts/package_skill.py <path>`
5. Add entry to `.agent/skills/INDEX.md`

### Available Skills Reference

See the complete index at [`.agent/skills/INDEX.md`](.agent/skills/INDEX.md) for all 35+ skills with descriptions, difficulty levels, and quick selection guide.

**Most commonly used skills:**

| Skill                     | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| `skill-creator`           | Create new skills                         |
| `app-builder`             | Scaffold new applications                 |
| `architectural-design`    | Generate PLAN.md and architecture         |
| `database-design`         | Schema design and migrations              |
| `api-patterns`            | API design patterns (REST, GraphQL, tRPC) |
| `frontend-dev-guidelines` | Frontend development best practices       |
| `backend-dev-guidelines`  | FastAPI + SQLAlchemy backend standards    |
| `e2e-testing-patterns`    | Playwright/Cypress testing patterns       |
| `containerization`        | Docker best practices                     |
| `ci-cd-pipelines`         | GitHub Actions workflow templates         |
| `cloud-deployment`        | Vercel, AWS, Railway deployment           |
| `gsd-workflow`            | Get Shit Done spec-driven development     |

---

## Working with Rules

Rules are located in `.agent/rules/` and provide technology-specific guidance:

### Rule Categories

- **Framework-specific**: `next-js-*.md`, `fastapi-*.md`
- **Language-specific**: `typescript-*.md`, `python-*.md`
- **Domain-specific**: `ai-agentic/`, `database-data/`
- **Architecture**: `turborepo-*.md`

### Rule Format

```yaml
---
trigger: always_on | conditional
description: Brief description of when this rule applies
globs: ["*.ts", "*.tsx"] # Optional file patterns
---
# Rule content in markdown
```

---

## Key Documents Reference

### Phase Documentation

| Document                                               | Purpose                                |
| ------------------------------------------------------ | -------------------------------------- |
| `docs/overview.md`                                     | Master plan and project pillars        |
| `docs/plans/phase_01.md`                               | Model Strategy & Selection             |
| `docs/plans/phase_02.md`                               | Planning Protocol & PLAN.md generation |
| `docs/plans/phase_03.md`                               | Implementation Workflow                |
| `docs/plans/phase_04.md`                               | Testing & CI/CD                        |
| `docs/plans/phase_05.md`                               | Iteration & Continuous Improvement     |
| `docs/implementation/universal_agentic_development.md` | Comprehensive implementation guide     |
| `Cost-Efficient-Development-Workflow-Extended.md`      | Extended workflow documentation        |

### Planning Templates

| Document                                                | Purpose                          |
| ------------------------------------------------------- | -------------------------------- |
| `docs/planning/PLAN.md`                                 | Architectural blueprint template |
| `docs/planning/TASKS.md`                                | Task breakdown template          |
| `.agent/skills/architectural-design/templates/PLAN.md`  | PLAN.md generator template       |
| `.agent/skills/architectural-design/templates/TASKS.md` | TASKS.md generator template      |

---

## Common Workflows

### Starting a New Project

1. Review `docs/overview.md` for methodology
2. Follow `docs/plans/phase_01.md` for model setup
3. Use `docs/plans/phase_02.md` to create `PLAN.md`
4. Generate `TASKS.md` from PLAN
5. Execute tasks following `docs/plans/phase_03.md`

### Making Changes to This Repository

1. This is a **methodology/documentation** repository
2. Follow the Planning-First principle for significant changes
3. Update relevant documentation in `docs/`
4. Maintain consistency across phase documents
5. Test scripts before committing

### Adding New Skills

1. Use the `skill-creator` skill
2. Follow the skill anatomy guidelines
3. Include proper frontmatter in `SKILL.md`
4. Test scripts if included
5. Package and validate before distribution

---

## Troubleshooting

### Environment Issues

```bash
# Verify API keys
python3 scripts/verify_env.py

# Reinstall toolchain
./scripts/install_toolchain.sh

# Reset local LLMs
./scripts/setup_local_llms.sh
```

### Common Problems

| Problem                  | Solution                                       |
| ------------------------ | ---------------------------------------------- |
| API key not recognized   | Check `.env` file is loaded; verify key format |
| Ollama models not found  | Run `ollama serve` in background               |
| Aider config not loading | Verify `.aider.conf.yml` syntax                |
| Pre-commit hooks failing | Run linting/fixing manually first              |

---

## Resources

- **README.md**: Human-facing project overview
- **docs/**: Comprehensive methodology documentation
- **.agent/skills/**: Reusable capabilities
- **.agent/skills/INDEX.md**: Complete index of all skills with descriptions
- **Cost-Efficient-Development-Workflow-Extended.md**: Extended reference

---

_This document is maintained for AI coding agents. For human contributors, see README.md._
