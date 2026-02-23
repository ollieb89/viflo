# Viflo: The Universal Agentic Development Environment

> **Maximize velocity, minimize cost, and eliminate technical debt through hybrid AI strategies.**

Viflo is a comprehensive development methodology and toolchain designed to standardize and accelerate agentic software development. By combining detailed planning protocols with a hybrid model strategy (proprietary reasoning + open-source execution), Viflo ensures that AI-generated code is robust, maintainable, and cost-effective.

## Key Features

- **Hybrid Model Strategy**: Intelligent routing of tasks to the most effective model — premium models (Claude Opus, Gemini Pro) for planning; fast/cheap models (Gemini Flash, GPT Mini) for execution.
- **Structured Planning Protocol**: A mandatory "Planning-First" approach where no code is written without a granular, pre-approved `PLAN.md`.
- **Agentic Workflow**: Implementation is broken down into atomic, independently testable units executed by specialized CLI agents.
- **5-Phase Lifecycle**: A complete framework covering everything from initial Model Strategy to Continuous Improvement and Iteration.
- **34 Reusable Skills**: A library of skill packages covering frontend, backend, database, security, CI/CD, and more.

## Getting Started

### Prerequisites

- **Git**
- **Python 3.10+** (for verification scripts)
- **Node.js & npm** (for Claude Code)
- **Ollama** (optional, but recommended for local model execution)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/viflo.git
   cd viflo
   ```

2. **Configure Environment**
   Copy the template and add your API keys.
   ```bash
   cp .env.template .env
   # Edit .env and add:
   # GEMINI_API_KEY=...
   # ANTHROPIC_API_KEY=...
   ```

3. **Install Toolchain**
   Installs core dependencies like `aider-chat` and `claude-code`.
   ```bash
   ./scripts/install_toolchain.sh
   ```

4. **Setup Local LLMs** (optional)
   Installs Ollama and pulls the required local models (`deepseek-r1`, `qwen2.5-coder`).
   ```bash
   ./scripts/setup_local_llms.sh
   ```

5. **Verify Setup**
   Ensure all environment variables and tools are correctly configured.
   ```bash
   python3 scripts/verify_env.py
   ```

## Usage

### Planning Phase

Start by defining your project's roadmap using the Viflo planning templates.

- Review **[Phase 1: Model Strategy](./docs/plans/phase_01.md)** to select your model portfolio.
- Use **[Phase 2: Planning Protocol](./docs/plans/phase_02.md)** to generate your `PLAN.md`.

### Execution Phase

Execute your plans using the agentic workflow described in **[Phase 3: Implementation](./docs/plans/phase_03.md)**.

- Break down tasks into small batches.
- Use the installed CLI tools to dispatch agents for implementation.

### Verification & Iteration

Ensure quality and continuous improvement.

- Follow **[Phase 4: Testing & CI](./docs/plans/phase_04.md)** for validation.
- Use **[Phase 5: Iteration](./docs/plans/phase_05.md)** for retrospective and refinement.

## Available Skills

Skills are reusable packages in `.agent/skills/` that provide specialized AI guidance for specific tasks.

| Category | Skill | Description |
|----------|-------|-------------|
| **API** | `api-design-principles` | REST and GraphQL API design patterns |
| **API** | `api-patterns` | API style selection and decision-making |
| **Architecture** | `architectural-design` | Create PLAN.md and architecture blueprints |
| **Architecture** | `architecture-patterns` | Clean Architecture, Hexagonal, DDD |
| **Architecture** | `microservices-patterns` | Service boundaries and event-driven patterns |
| **Backend** | `backend-dev-guidelines` | FastAPI + SQLAlchemy development standards |
| **Backend** | `fastapi-templates` | Production-ready FastAPI project templates |
| **Backend** | `nodejs-backend-patterns` | Node.js/Express/Fastify patterns |
| **Build** | `app-builder` | Full-stack application scaffolding orchestrator |
| **CI/CD** | `ci-cd-pipelines` | GitHub Actions workflow templates |
| **Cloud** | `cloud-deployment` | Vercel, AWS, Railway deployment guides |
| **Cloud** | `containerization` | Docker best practices and multi-stage builds |
| **Database** | `database-design` | PostgreSQL schema and migration patterns |
| **Database** | `postgresql` | PostgreSQL-specific schema design |
| **Frontend** | `frontend-dev-guidelines` | React/TypeScript/MUI development guidelines |
| **Frontend** | `frontend-design` | Distinctive, production-grade UI creation |
| **Git** | `git-advanced-workflows` | Rebase, cherry-pick, bisect, worktrees |
| **Methodology** | `behavioral-modes` | Agent operational mode definitions |
| **Methodology** | `brainstorming` | Socratic questioning and communication protocol |
| **Methodology** | `gsd-workflow` | Get Shit Done spec-driven development |
| **Methodology** | `skill-creator` | Create and update skills |
| **Methodology** | `writing-skills` | Test-driven skill documentation |
| **Quality** | `code-review-excellence` | Effective code review practices |
| **Quality** | `debugging-strategies` | Systematic debugging techniques |
| **Quality** | `e2e-testing-patterns` | Playwright and Cypress E2E testing |
| **Quality** | `error-handling-patterns` | Exception handling and resilience patterns |
| **Quality** | `temporal-python-testing` | Temporal workflow testing with pytest |
| **README** | `github-readme-writer` | GitHub-optimized README creation |
| **Security** | `pci-compliance` | PCI DSS compliance implementation |
| **Security** | `security/security-scanning` | SAST configuration and vulnerability detection |
| **TypeScript** | `typescript-advanced-types` | Advanced TypeScript type system patterns |
| **Workflows** | `monorepo-management` | Turborepo/Nx/pnpm workspace management |
| **Workflows** | `workflow-orchestration-patterns` | Temporal durable workflow patterns |

See **[AGENTS.md](./AGENTS.md)** for a comprehensive AI agent reference guide, including model routing strategy, code style guidelines, and working with skills and rules.

## Project Structure

```
.
├── AGENTS.md               # AI agent reference guide
├── README.md               # This file
├── .agent/
│   ├── rules/              # Coding rules by technology/domain
│   ├── skills/             # 34 reusable skill packages
│   └── workflows/          # Workflow definitions
├── docs/
│   ├── overview.md         # Master Plan and project pillars
│   └── plans/              # Operational plans for each phase
├── scripts/
│   ├── install_toolchain.sh
│   ├── setup_local_llms.sh
│   └── verify_env.py
└── packages/               # Shared packages (types, tsconfig, eslint)
```

## Contributing

We welcome contributions! Please see our [Master Plan](./docs/overview.md) to understand the core philosophy before submitting pull requests. Ensure all changes follow the "Planning-First" methodology.

When contributing new skills, use the `skill-creator` skill as a guide:

```bash
python .agent/skills/skill-creator/scripts/init_skill.py <name>
```

## License

(Proprietary / Internal Use Only - Placeholder)
