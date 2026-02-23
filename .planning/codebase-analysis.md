# Viflo Codebase Analysis

## Project Overview

**Viflo** (Visual Flow) is a comprehensive development methodology and toolchain designed to standardize and accelerate agentic software development. It provides a 5-phase lifecycle for hybrid AI-human software development.

## Tech Stack

| Layer              | Technology          |
| ------------------ | ------------------- |
| Documentation      | Markdown            |
| Package Management | pnpm (>=10.0.0)     |
| Monorepo           | TurboRepo structure |
| Languages          | TypeScript, Python  |

## Directory Structure

```
viflo/
├── .agent/                    # AI agent configuration
│   ├── agents/               # Agent persona definitions
│   ├── rules/                # Coding rules by tech/domain
│   ├── skills/               # Reusable skill packages
│   │   └── gsd-workflow/     # GSD methodology skill (NEW)
│   └── workflows/            # Workflow definitions
├── docs/                     # Comprehensive documentation
│   ├── plans/               # 5-phase operational plans
│   ├── implementation/      # Implementation guides
│   └── planning/            # PLAN.md templates
├── packages/                # Shared packages
│   ├── types/
│   ├── tsconfig/
│   └── eslint-config/
├── scripts/                 # Environment setup scripts
└── AGENTS.md               # AI agent reference guide
```

## Key Components

### 1. Documentation (`docs/`)

- **Phase Plans**: 5 phases of Viflo methodology
  - Phase 1: Model Strategy & Selection
  - Phase 2: Planning Protocol
  - Phase 3: Implementation Workflow
  - Phase 4: Testing & CI/CD
  - Phase 5: Iteration & Continuous Improvement
- **Templates**: PLAN.md and TASKS.md templates
- **Implementation Guides**: Universal agentic development guide

### 2. Agent Configuration (`.agent/`)

- **Skills**: Reusable capabilities with SKILL.md
- **Rules**: Technology-specific coding rules
- **Workflows**: Common operation definitions

### 3. GSD Workflow Skill (`.agent/skills/gsd-workflow/`)

**NEW**: Complete Get Shit Done methodology implementation

- 12 helper scripts
- 9 templates
- 2 examples
- 2 reference guides

## Architecture Patterns

### Skill Structure

```
skill-name/
├── SKILL.md          # Required metadata + instructions
├── scripts/          # Executable scripts
├── references/       # Documentation references
└── assets/           # Templates, boilerplate
```

### Rule Format

```yaml
---
trigger: always_on | conditional
description: When this rule applies
globs: ["*.ts", "*.tsx"]
---
```

## Code Conventions

### Naming

- Files: kebab-case
- Components: PascalCase
- Functions: camelCase (JS/TS), snake_case (Python)
- Constants: UPPER_SNAKE_CASE

### File Organization

- Co-located tests: `.test.ts`, `test_*.py`
- E2E tests: `tests/e2e/`
- Skills: Self-contained directories

### Commits

Conventional Commits: `type(scope): description`
Types: feat, fix, refactor, test, chore, docs, style, perf

## Dependencies

### External Tools

- **Aider**: Multi-file refactoring
- **Claude Code**: Autonomous coding
- **Ollama**: Local LLM execution

### API Keys Required

- GEMINI_API_KEY
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- XAI_API_KEY

## Current State

- ✅ Comprehensive documentation
- ✅ Agent configuration structure
- ✅ GSD Workflow skill created and installed
- ✅ Helper scripts (12 total)
- ✅ Templates and examples
- ⏳ PROJECT.md needs customization
- ⏳ REQUIREMENTS.md needs v1/v2 definitions

## Next Steps

1. Customize PROJECT.md with Viflo vision
2. Define REQUIREMENTS.md with phases
3. Create ROADMAP.md with milestones
4. Use GSD workflow for future enhancements
