# Phase 01 — Foundation & Planning Infrastructure

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bootstrap the GeriApp monorepo from a greenfield directory into a fully-scaffolded, quality-gated, CI-enabled development environment with planning docs and architecture — before any feature code.

**Architecture:** pnpm-managed monorepo with Next.js 16 web portal, Express user service, two Python/FastAPI services (care + AI), PostgreSQL (5435), and Redis (6479). Python services managed by Pixi in a separate `backend/pixi.toml`, not pnpm workspace.

**Tech Stack:** Node.js ≥22, pnpm ≥10, Python 3.11+ (Pixi), Next.js 16, Express, FastAPI, SQLAlchemy, Pydantic, Tailwind CSS, Radix UI, Vitest, Playwright, pytest, ESLint, Prettier, Black, Flake8, Husky, GitHub Actions.

**Pre-existing environment (verified):**
- Node v24.13.0 ✅
- pnpm 10.28.1 ✅
- Pixi 0.63.0 ✅
- Python 3.12.3 ✅
- Claude Code CLI 2.1.45 ✅
- Gemini CLI 0.28.2 ✅
- Aider ❌ (to install)
- Git repo ❌ (not initialized)

---

## Task 0: Git Initialization

**Files:**
- Create: `.gitignore`
- Create: `README.md`

**Step 1: Initialize git repo**

```bash
cd /home/ollie/Development/Tools/viflo
git init
```

Expected: `Initialized empty Git repository`

**Step 2: Create `.gitignore`**

```gitignore
# Dependencies
node_modules/
.pnpm-store/

# Build
.next/
dist/
build/
*.egg-info/

# Python
__pycache__/
*.pyc
*.pyo
.venv/
.pixi/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test
coverage/
.pytest_cache/
htmlcov/

# Misc
*.log
```

**Step 3: Create minimal `README.md`**

```markdown
# GeriApp

Stage-adaptive dementia care platform.

## Quick Start

```bash
./scripts/bootstrap.sh
```

See `docs/` for architecture and planning documentation.
```

**Step 4: Initial commit**

```bash
git add .
git commit -m "chore: initialize repository"
```

Expected: commit succeeds with files tracked.

---

## Task 1: Monorepo Scaffold (pnpm + Pixi)

**Files:**
- Create: `package.json` (root)
- Create: `pnpm-workspace.yaml`
- Create: `web/package.json`
- Create: `web/src/app/page.tsx`
- Create: `web/src/app/layout.tsx`
- Create: `web/next.config.ts`
- Create: `web/tsconfig.json`
- Create: `backend/user-service/package.json`
- Create: `backend/user-service/src/index.ts`
- Create: `backend/user-service/tsconfig.json`
- Create: `backend/shared/database/__init__.py`
- Create: `backend/shared/schemas/__init__.py`
- Create: `backend/pixi.toml`
- Create: `backend/care-service/src/__init__.py`
- Create: `backend/care-service/src/main.py`
- Create: `backend/ai-service/src/__init__.py`
- Create: `backend/ai-service/src/main.py`

### Step 1: Create root `package.json`

```json
{
  "name": "geriapp",
  "private": true,
  "engines": {
    "node": ">=22.0.0",
    "pnpm": ">=10.0.0"
  },
  "scripts": {
    "dev": "echo 'Use pnpm --filter <app> dev'",
    "lint": "pnpm -r run lint",
    "format": "pnpm -r run format",
    "check": "make check"
  }
}
```

### Step 2: Create `pnpm-workspace.yaml`

```yaml
packages:
  - "web"
  - "mobile"
  - "backend/user-service"
  - "backend/shared"
  - "packages/*"
```

### Step 3: Scaffold the web portal (`web/`)

Create `web/package.json`:

```json
{
  "name": "@geriapp/web",
  "version": "0.0.1",
  "private": true,
  "scripts": {
    "dev": "next dev --port 4100 --turbopack",
    "build": "next build",
    "start": "next start --port 4100",
    "lint": "next lint",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^16.0.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "typescript": "^5.7.0"
  }
}
```

Create `web/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

Create `web/next.config.ts`:

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {};

export default nextConfig;
```

Create `web/src/app/layout.tsx`:

```tsx
export const metadata = {
  title: 'GeriApp',
  description: 'Stage-adaptive dementia care platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

Create `web/src/app/page.tsx`:

```tsx
export default function Home() {
  return (
    <main>
      <h1>GeriApp</h1>
      <p>Stage-adaptive dementia care platform.</p>
    </main>
  );
}
```

### Step 4: Scaffold the user service (`backend/user-service/`)

Create `backend/user-service/package.json`:

```json
{
  "name": "@geriapp/user-service",
  "version": "0.0.1",
  "private": true,
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "start": "node dist/index.js",
    "build": "tsc",
    "lint": "eslint src/",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "express": "^5.1.0",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "@types/express": "^5.0.0",
    "@types/cors": "^2.8.17",
    "@types/node": "^22.0.0",
    "tsx": "^4.19.0",
    "typescript": "^5.7.0"
  }
}
```

Create `backend/user-service/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

Create `backend/user-service/src/index.ts`:

```typescript
import express from 'express';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 8100;

app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'user-service' });
});

app.listen(PORT, () => {
  console.log(`User service running on port ${PORT}`);
});
```

### Step 5: Scaffold Python shared module and services

Create `backend/shared/database/__init__.py` — empty file.

Create `backend/shared/schemas/__init__.py` — empty file.

Create `backend/care-service/src/__init__.py` — empty file.

Create `backend/care-service/src/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="GeriApp Care Service", version="0.1.0")


@app.get("/api/v1/health")
async def health() -> dict:
    return {"status": "ok", "service": "care-service"}
```

Create `backend/ai-service/src/__init__.py` — empty file.

Create `backend/ai-service/src/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="GeriApp AI Service", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "ai-service"}
```

### Step 6: Create `backend/pixi.toml`

```toml
[project]
name = "geriapp-backend"
version = "0.1.0"
description = "GeriApp Python backend services"
channels = ["conda-forge"]
platforms = ["linux-64"]

[environments]
care-service = ["care-service"]
ai-service = ["ai-service"]
dev = ["dev"]

[feature.care-service.dependencies]
python = ">=3.11,<3.13"
pip = "*"

[feature.care-service.pypi-dependencies]
fastapi = ">=0.115.0"
uvicorn = { version = ">=0.34.0", extras = ["standard"] }
sqlalchemy = { version = ">=2.0.0", extras = ["asyncio"] }
alembic = ">=1.14.0"
pydantic = ">=2.10.0"
pydantic-settings = ">=2.6.0"

[feature.care-service.tasks]
care-dev = "cd care-service && uvicorn src.main:app --host 0.0.0.0 --port 8101 --reload"
care-test = "cd care-service && pytest tests/ -v"
care-migrate = "cd care-service && alembic upgrade head"

[feature.ai-service.dependencies]
python = ">=3.11,<3.13"
pip = "*"

[feature.ai-service.pypi-dependencies]
fastapi = ">=0.115.0"
uvicorn = { version = ">=0.34.0", extras = ["standard"] }

[feature.ai-service.tasks]
ai-dev = { cmd = "cd ai-service && uvicorn src.main:app --host 0.0.0.0 --port 8102 --reload", env = { PYTHONNOUSERSITE = "1" } }
ai-test = "cd ai-service && pytest tests/ -v"

[feature.dev.dependencies]
python = ">=3.11,<3.13"
pip = "*"

[feature.dev.pypi-dependencies]
black = ">=24.0.0"
flake8 = ">=7.0.0"
mypy = ">=1.11.0"
pytest = ">=8.0.0"
pytest-asyncio = ">=0.24.0"

[feature.dev.tasks]
lint = "flake8 ."
format = "black ."
format-check = "black --check ."
type-check = "mypy ."
```

### Step 7: Install dependencies

```bash
cd /home/ollie/Development/Tools/viflo && pnpm install
```

Expected: dependencies installed with no errors.

```bash
cd /home/ollie/Development/Tools/viflo/backend && pixi install -e care-service && pixi install -e ai-service && pixi install -e dev
```

Expected: pixi environments created.

### Step 8: Verify scaffolds

```bash
cd /home/ollie/Development/Tools/viflo/web && pnpm build
```

Expected: Next.js builds successfully.

```bash
cd /home/ollie/Development/Tools/viflo/backend && pixi run -e care-service -- python -c "from src.main import app; print('care-service OK')"
```

Expected: `care-service OK`

```bash
cd /home/ollie/Development/Tools/viflo/backend && pixi run -e ai-service -- python -c "from src.main import app; print('ai-service OK')"
```

Expected: `ai-service OK`

### Step 9: Commit

```bash
git add .
git commit -m "chore: scaffold monorepo with pnpm workspaces and pixi"
```

---

## Task 2: Code Quality Toolchain

**Files:**
- Create: `.prettierrc`
- Create: `.prettierignore`
- Create: `web/.eslintrc.json` (or use Next.js default)
- Create: `backend/.flake8`
- Create: `Makefile`
- Modify: `package.json` (add husky + lint-staged)
- Modify: `backend/pixi.toml` (already has black+flake8)

### Step 1: Create `.prettierrc`

```json
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

### Step 2: Create `.prettierignore`

```
node_modules
.next
dist
build
coverage
.pixi
__pycache__
```

### Step 3: Install JS quality deps

```bash
cd /home/ollie/Development/Tools/viflo && pnpm add -wD prettier eslint-config-prettier husky lint-staged
```

Expected: installed.

### Step 4: Configure lint-staged in root `package.json`

Add to root `package.json`:

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yaml,yml}": ["prettier --write"],
    "*.py": ["black"]
  }
}
```

### Step 5: Initialize Husky

```bash
cd /home/ollie/Development/Tools/viflo && npx husky init
```

Expected: `.husky/` directory created with a `pre-commit` hook.

Edit `.husky/pre-commit`:

```bash
pnpm exec lint-staged
```

### Step 6: Create `backend/.flake8`

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude =
    .pixi,
    __pycache__,
    .git
```

### Step 7: Create `Makefile`

```makefile
.PHONY: lint format check lint-js lint-py format-js format-py

# JavaScript/TypeScript
lint-js:
	pnpm -r run lint

format-js:
	pnpm exec prettier --write "**/*.{ts,tsx,js,jsx,json,md,yaml,yml}"

# Python (run from backend/)
lint-py:
	cd backend && pixi run -e dev lint

format-py:
	cd backend && pixi run -e dev format

# Combined
lint: lint-js lint-py

format: format-js format-py

check: lint
	cd backend && pixi run -e dev format-check
	pnpm exec prettier --check "**/*.{ts,tsx,js,jsx,json,md,yaml,yml}"
```

### Step 8: Verify quality gate

```bash
cd /home/ollie/Development/Tools/viflo && pnpm exec prettier --check .
```

Expected: exits 0 (all files formatted).

```bash
cd /home/ollie/Development/Tools/viflo/backend && pixi run -e dev format-check
```

Expected: exits 0.

### Step 9: Test pre-commit hook

```bash
cd /home/ollie/Development/Tools/viflo
echo "const   x=1;" > /tmp/test-lint.ts
cp /tmp/test-lint.ts web/src/test-lint.ts
git add web/src/test-lint.ts
git commit -m "test: verify pre-commit hook"
```

Expected: lint-staged runs, reformats the file, commit succeeds with formatted output.

```bash
rm web/src/test-lint.ts
git add web/src/test-lint.ts
git commit -m "chore: remove test file"
```

### Step 10: Commit quality toolchain

```bash
git add .
git commit -m "chore: add code quality toolchain (ESLint, Prettier, Black, Flake8, Husky)"
```

---

## Task 3: CLI Agent Installation (Aider)

**Files:**
- None (system-level install)

> Claude Code CLI and Gemini CLI are already installed and verified.

### Step 1: Install Aider

```bash
pip install aider-chat
```

Expected: installs successfully.

### Step 2: Verify Aider

```bash
aider --version
```

Expected: prints version number (e.g., `0.70.x`).

### Step 3: Verify all three agents

```bash
claude --version && gemini --version && aider --version
```

Expected: all three print version info.

> **No commit needed** — system-level tool, not repo-tracked.

---

## Task 4: Bootstrap Script

**Files:**
- Create: `scripts/bootstrap.sh`
- Create: `.env.example`

### Step 1: Create `.env.example`

```bash
# GeriApp Environment Variables

# Node.js services
NODE_ENV=development
PORT=8100

# Database
DATABASE_URL=postgresql://geriapp:dev_password@localhost:5435/geriapp

# Redis
REDIS_URL=redis://localhost:6479

# Auth (provider TBD in Task 7)
# JWT_SECRET=your-secret-here

# LLM API Keys (from Task 5)
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
# GOOGLE_AI_API_KEY=
```

### Step 2: Create `scripts/bootstrap.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "🏥 GeriApp Bootstrap"
echo "==================="

# 1. Check prerequisites
echo ""
echo "Checking prerequisites..."

check_cmd() {
  if ! command -v "$1" &>/dev/null; then
    echo "❌ $1 not found. $2"
    exit 1
  fi
  echo "✅ $1 found: $($1 --version 2>/dev/null | head -1)"
}

check_cmd node "Install via nvm: https://github.com/nvm-sh/nvm"
check_cmd pnpm "Install: npm install -g pnpm"
check_cmd pixi "Install: curl -fsSL https://pixi.sh/install.sh | bash"
check_cmd python3 "Install via pixi or system package manager"
check_cmd git "Install: sudo apt install git"

# 2. Check node version
NODE_MAJOR=$(node --version | sed 's/v//' | cut -d. -f1)
if [ "$NODE_MAJOR" -lt 22 ]; then
  echo "❌ Node.js >= 22 required (found: $(node --version))"
  exit 1
fi
echo "✅ Node.js version OK"

# 3. Install JS dependencies
echo ""
echo "Installing JavaScript dependencies..."
pnpm install

# 4. Install Python dependencies
echo ""
echo "Installing Python dependencies..."
cd backend
pixi install -e care-service
pixi install -e ai-service
pixi install -e dev
cd ..

# 5. Setup environment file
if [ ! -f .env ]; then
  echo ""
  echo "Creating .env from .env.example..."
  cp .env.example .env
  echo "⚠️  Edit .env with your API keys"
fi

# 6. Setup git hooks
echo ""
echo "Setting up git hooks..."
npx husky install 2>/dev/null || true

# 7. Verify
echo ""
echo "Verifying setup..."
echo "  Node.js:  $(node --version)"
echo "  pnpm:     $(pnpm --version)"
echo "  Pixi:     $(pixi --version)"
echo "  Python:   $(python3 --version)"

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Start infrastructure: docker compose up -d"
echo "  3. Start dev servers: pnpm dev"
```

### Step 3: Make executable

```bash
chmod +x scripts/bootstrap.sh
```

### Step 4: Verify bootstrap

```bash
cd /home/ollie/Development/Tools/viflo && ./scripts/bootstrap.sh
```

Expected: script runs end-to-end without errors, prints success message.

### Step 5: Commit

```bash
git add .
git commit -m "chore: add bootstrap script and .env.example"
```

---

## Task 5: LLM Selection Document

**Files:**
- Create: `llm_selection.md`

### Step 1: Create `llm_selection.md`

```markdown
# LLM Selection — GeriApp

## Model Picks

| Role | Model | Fallback | Cost (~$/1M tokens) | Context | Rationale |
|------|-------|----------|---------------------|---------|-----------|
| 🧠 Planning Brain | Claude Opus 4.5 | Gemini 3 Pro | ~$15 in / $75 out | 200K | Best structured architectural reasoning; excels at multi-step plan generation |
| ⚡ Coding Workhorse | Gemini 3 Pro | Claude Sonnet | ~$1.25 in / $10 out | 1M | Top coding benchmarks 2026, massive context for repo-wide refactors |
| 💰 Cheap Bulk | DeepSeek V3.x | Qwen (local) | ~$0.27 in / $1.10 out | 128K | Cost-efficient for repetitive edits, doc generation, boilerplate |

## Agent → Model Routing

| Agent | Model | Role |
|-------|-------|------|
| Claude Code CLI | Claude Opus 4.5 | Planning Brain |
| Aider | Gemini 3 Pro | Coding Workhorse |
| Gemini CLI | Gemini 3 Pro | Coding Workhorse |
| Local fallback | DeepSeek V3.x / Qwen | Cheap Bulk |

## Monthly Cost Estimate (Solo Dev)

| Category | Est. Monthly |
|----------|-------------|
| Planning Brain (light use) | ~$30–50 |
| Coding Workhorse (heavy use) | ~$50–100 |
| Cheap Bulk (moderate use) | ~$10–20 |
| **Total** | **~$90–170** |

## Reassessment

- Reassess quarterly or when costs spike >2x
- Track token usage per agent per week
- Switch models when quality/cost ratio degrades
```

### Step 2: Commit

```bash
git add llm_selection.md
git commit -m "docs: add LLM selection with routing table"
```

> [!IMPORTANT]
> **User review needed**: The model picks and cost estimates above are educated defaults. You should verify these match your actual API access and budget constraints before finalizing.

---

## Task 6: PLAN.md (Planning Infrastructure)

**Files:**
- Create: `PLAN.md`
- Create: `prompts/generate-system-design.md`
- Create: `prompts/generate-api-route.md`
- Create: `prompts/generate-db-migration.md`

### Step 1: Create `PLAN.md`

```markdown
# PLAN.md — GeriApp

## Overview

GeriApp is a stage-adaptive dementia care platform. The core differentiator is cognitive stage adaptation — every UI component adjusts complexity, touch targets, and guidance based on the user's dementia stage (early/moderate/advanced).

The platform supports three user personas:
1. **People with dementia** — simplified, accessible interface
2. **Caregivers** — care plan management, medication tracking, activity scheduling
3. **Healthcare providers** — clinical dashboards, patient monitoring, analytics

## Tech Stack

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Web Frontend | Next.js (App Router) | 16 | Port 4100 |
| Mobile Frontend | React Native + Expo | 0.73+ | Shared hooks with web |
| UI | Tailwind CSS + Radix UI | — | + class-variance-authority |
| User Service | Express + TypeScript | 5.x | Port 8100 |
| Care Service | FastAPI + SQLAlchemy | ≥0.115 | Port 8101, Python 3.11+ |
| AI Service | FastAPI + PyTorch + MediaPipe | ≥0.115 | Port 8102, Python 3.11+ |
| Database | PostgreSQL | 16+ | Port 5435 |
| Cache | Redis | 7+ | Port 6479 |
| Real-time | Socket.IO | — | JWT auth + Redis adapter |
| Package mgmt (JS) | pnpm | ≥10 | Workspaces |
| Package mgmt (Py) | Pixi | — | Per-service environments |

### Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend Shape | Next.js + Express API (separate) | Clear separation, independent scaling, complex domain |
| Python Integration | Separate FastAPI services | Direct sync REST calls for real-time interactions |
| ORM | SQLAlchemy 2.0 (async) | Shared models in backend/shared/ |
| Validation | Pydantic | Three-layer sync: SQLAlchemy → Pydantic → TypeScript |
| State (web) | React Context + React Query | Server state via TanStack Query |

## Infrastructure Constraints

- **Hosting**: TBD (Railway backend, Vercel frontend candidates)
- **Compute**: Standard tier — no GPU required except AI service
- **Networking**: All services on localhost for dev; reverse proxy for prod
- **Storage**: S3-compatible for media uploads (TBD)

## Budget & Latency

| Metric | Target |
|--------|--------|
| LLM monthly budget | $90–170/mo (solo dev) |
| Infra monthly budget | TBD — start with free tiers |
| API latency (p95) | < 200ms for CRUD, < 1s for AI endpoints |
| Page load (LCP) | < 2.5s |

## Auth & Security

| Aspect | Decision |
|--------|----------|
| Auth provider | TBD (Clerk or custom JWT) |
| Token format | JWT (httpOnly cookies) |
| Token expiry | 24h access, 7d refresh |
| Authorization | RBAC — patient, caregiver, provider, admin |
| Encryption | TLS in transit, AES-256 at rest |
| Compliance | HIPAA-compliant data handling |
| Rate limiting | slowapi on auth endpoints |
| Security headers | CSP, HSTS, X-Frame-Options, SameSite |
```

### Step 2: Create `prompts/generate-system-design.md`

```markdown
# System Design Generation Prompt

You are designing a system component for GeriApp, a stage-adaptive dementia care platform.

## Context
Read PLAN.md and ARCHITECTURE.md for full project context.

## Task
Design the [COMPONENT] subsystem. Include:

1. **Data flow diagram** (Mermaid)
2. **API endpoints** (method, path, request/response types)
3. **Database tables** (columns, types, constraints, relationships)
4. **Error handling** (error codes, retry strategy)
5. **Security considerations** (auth, validation, HIPAA)

## Constraints
- Must support cognitive stage adaptation
- Must maintain three-layer type sync (SQLAlchemy → Pydantic → TypeScript)
- API responses wrap errors as `{"error": {"message": "...", "code": "..."}}`
- All endpoints require JWT auth via middleware

## Output Format
Markdown with Mermaid diagrams and code blocks.
```

### Step 3: Create `prompts/generate-api-route.md`

```markdown
# API Route Generation Prompt

Generate a FastAPI route for GeriApp's Care Service.

## Context
- Framework: FastAPI with async SQLAlchemy
- Auth: `CurrentUser = Annotated[Dict[str, Any], Depends(verify_user_token)]`
- DB: `DbSession = Annotated[AsyncSession, Depends(get_db)]`
- Roles: `require_roles("admin", "provider")`

## Task
Create the [ENDPOINT] route. Include:

1. **Router file** at `backend/care-service/src/api/[resource].py`
2. **Pydantic schemas** at `backend/shared/schemas/[resource].py`
3. **Service layer** at `backend/care-service/src/services/[resource].py`

## Constraints
- Use `DbSession` and `CurrentUser` dependency types
- Return proper HTTP status codes (201 for creation, 204 for deletion)
- Wrap errors in standard format
- Soft delete with `is_active=False`

## Output
Complete Python code for all three files.
```

### Step 4: Create `prompts/generate-db-migration.md`

```markdown
# Database Migration Generation Prompt

Generate an Alembic migration for GeriApp.

## Context
- ORM: SQLAlchemy 2.0 (async)
- Models: `backend/shared/database/models.py`
- Alembic config: `backend/care-service/alembic.ini`
- Database: PostgreSQL 16+

## Task
Create a migration for [CHANGE DESCRIPTION].

## Constraints
- Use `op.create_table()` / `op.add_column()` etc.
- Include both `upgrade()` and `downgrade()`
- Use UUID primary keys (`sa.dialects.postgresql.UUID`)
- Include `created_at` and `updated_at` timestamps
- Add appropriate indexes for query patterns
- Add foreign key constraints with `ondelete="CASCADE"` where appropriate

## Output
Complete Alembic migration file.
```

### Step 5: Commit

```bash
git add PLAN.md prompts/
git commit -m "docs: add PLAN.md and prompt templates"
```

---

## Task 7: System Architecture Document

**Files:**
- Create: `ARCHITECTURE.md`

### Step 1: Create `ARCHITECTURE.md`

This is a substantial document. Create it with these sections:

```markdown
# ARCHITECTURE.md — GeriApp

## 1. Service Map

```mermaid
graph LR
    Client[Web / Mobile] --> NextJS[Next.js :4100]
    NextJS --> UserService[User Service :8100]
    NextJS --> CareService[Care Service :8101]
    NextJS --> AIService[AI Service :8102]
    UserService --> PG[(PostgreSQL :5435)]
    CareService --> PG
    AIService --> PG
    UserService --> Redis[(Redis :6479)]
```

## 2. API Route Tree (First Vertical Slice)

### User Service (:8100)

| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | Health check |
| POST | /api/v1/auth/register | Register new user |
| POST | /api/v1/auth/login | Login, return JWT |
| POST | /api/v1/auth/refresh | Refresh JWT |
| GET | /api/v1/users/me | Get current user profile |
| PATCH | /api/v1/users/me | Update profile |

### Care Service (:8101)

| Method | Path | Purpose |
|--------|------|---------|
| GET | /api/v1/health | Health check |
| GET | /api/v1/patients | List patients (provider/caregiver) |
| GET | /api/v1/patients/:id | Get patient details |
| POST | /api/v1/care-plans | Create care plan |
| GET | /api/v1/care-plans/:id | Get care plan |
| POST | /api/v1/medications | Add medication |
| GET | /api/v1/medications | List medications |

### AI Service (:8102)

| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | Health check |
| POST | /api/v1/analyze/pose | Pose estimation |

## 3. Database Schema

```mermaid
erDiagram
    users {
        uuid id PK
        varchar email UK
        varchar hashed_password
        varchar role
        varchar first_name
        varchar last_name
        varchar cognitive_stage
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    care_plans {
        uuid id PK
        uuid patient_id FK
        uuid created_by FK
        varchar title
        text description
        varchar status
        date start_date
        date end_date
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    medications {
        uuid id PK
        uuid patient_id FK
        varchar name
        varchar dosage
        varchar frequency
        time scheduled_time
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    users ||--o{ care_plans : "patient_id"
    users ||--o{ care_plans : "created_by"
    users ||--o{ medications : "patient_id"
```

### ORM Notes
- Source of truth: `backend/shared/database/models.py` (SQLAlchemy)
- Validation: `backend/shared/schemas/` (Pydantic)
- Frontend types: `web/src/types/` (TypeScript)
- Soft delete: `is_active=False` pattern
- Association tables use `Table()`, models use `class Model(Base)`

## 4. Authentication Model

### Flow
1. User registers → password hashed (bcrypt) → stored in `users`
2. User logs in → credentials verified → JWT issued (access + refresh)
3. Access token: 24h expiry, stored in httpOnly cookie
4. Refresh token: 7d expiry, stored in httpOnly cookie
5. Protected routes: middleware extracts + verifies JWT

### Middleware/Guard Pattern
- **Express (user-service)**: `authMiddleware` extracts JWT, attaches `req.user`
- **FastAPI (care/ai)**: `verify_user_token` dependency, `CurrentUser` annotated type
- **Next.js**: Server-side JWT verification in API routes / middleware

### Roles
| Role | Access Level |
|------|-------------|
| patient | Own data only |
| caregiver | Assigned patients' data |
| provider | All patients in facility |
| admin | Full system access |

## 5. Backend Integration Pattern

**Selected:** Synchronous REST (Node.js → Python FastAPI)

- User Service validates JWT → calls Care/AI services with `Authorization: Bearer <token>`
- Contract: OpenAPI/Swagger auto-generated by FastAPI
- Shared models defined in `backend/shared/`
- Error format: `{"error": {"message": "...", "code": "VALIDATION_ERROR"}}`

## 6. Error Handling Strategy

### Standard Error Response
```json
{
  "error": {
    "message": "Human-readable description",
    "code": "MACHINE_READABLE_CODE",
    "details": {}
  }
}
```

### Error Codes
| Code | HTTP | Description |
|------|------|-------------|
| VALIDATION_ERROR | 422 | Request validation failed |
| NOT_FOUND | 404 | Resource not found |
| UNAUTHORIZED | 401 | Missing or invalid token |
| FORBIDDEN | 403 | Insufficient permissions |
| INTERNAL_ERROR | 500 | Server error |

### Logging
- Framework: Python `logging` (backend), `pino` (user-service)
- Levels: DEBUG (dev only), INFO, WARNING, ERROR
- Monitoring: TBD — revisit Phase 03

## 7. Testing Plan

| Type | Target | Tooling | Coverage |
|------|--------|---------|----------|
| Unit (JS) | Components, hooks, utils | Vitest + Testing Library | ≥80% |
| Unit (Python) | Services, models, schemas | pytest + pytest-asyncio | ≥80% |
| Integration | API endpoints | supertest / httpx | Key flows |
| E2E | Critical user journeys | Playwright | Login, care plan CRUD |
| A11y | All UI components | jest-axe | 100% |
| Performance | TBD | TBD | p95 < 200ms (target) |

Testing tooling setup deferred to Phase 02 when endpoints exist.
```

### Step 2: Commit

```bash
git add ARCHITECTURE.md
git commit -m "docs: add system architecture (MV)"
```

---

## Task 8: CI/CD Pipeline

**Files:**
- Create: `.github/workflows/ci.yml`

### Step 1: Create `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, development]
  pull_request:
    branches: [main, development]

jobs:
  javascript:
    name: JavaScript / TypeScript
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 10

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm -r run lint

      - name: Prettier check
        run: pnpm exec prettier --check .

      - name: Type check
        run: pnpm -r run type-check

      - name: Build
        run: pnpm -r run build

      - name: Test
        run: pnpm -r run test || true  # No tests yet

  python:
    name: Python
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: prefix-dev/setup-pixi@v0.8.1
        with:
          pixi-version: v0.63.0
          manifest-path: backend/pixi.toml

      - name: Lint (Flake8)
        run: cd backend && pixi run -e dev lint

      - name: Format check (Black)
        run: cd backend && pixi run -e dev format-check

      - name: Test
        run: cd backend && pixi run -e dev -- pytest || true  # No tests yet
```

### Step 2: Verify CI config locally

```bash
cat /home/ollie/Development/Tools/viflo/.github/workflows/ci.yml
```

Expected: valid YAML with both jobs.

### Step 3: Commit

```bash
git add .github/
git commit -m "ci: add GitHub Actions CI pipeline"
```

---

## Task 9: Final Verification & Commit

**Files:**
- None new

### Step 1: Run full quality check

```bash
cd /home/ollie/Development/Tools/viflo && make check
```

Expected: exits 0 — all lints + format checks pass.

### Step 2: Verify bootstrap script

```bash
cd /home/ollie/Development/Tools/viflo && ./scripts/bootstrap.sh
```

Expected: runs clean, all checks pass.

### Step 3: Verify directory structure

```bash
find /home/ollie/Development/Tools/viflo -name "*.py" -o -name "*.ts" -o -name "*.tsx" | grep -v node_modules | grep -v .pixi | sort
```

Expected: shows all scaffolded source files.

### Step 4: Verify all artifacts exist

```bash
ls -la /home/ollie/Development/Tools/viflo/{PLAN.md,ARCHITECTURE.md,llm_selection.md,Makefile,.env.example}
ls -la /home/ollie/Development/Tools/viflo/scripts/bootstrap.sh
ls -la /home/ollie/Development/Tools/viflo/.github/workflows/ci.yml
ls -la /home/ollie/Development/Tools/viflo/prompts/
```

Expected: all files exist.

### Step 5: Final commit (if any unstaged changes)

```bash
git status
# If anything uncommitted:
git add .
git commit -m "chore: phase 01 foundation complete"
```

### Step 6: Tag phase completion

```bash
git tag -a v0.1.0-phase01 -m "Phase 01: Foundation & Planning Infrastructure complete"
```

---

## Verification Plan

### Automated Checks

| Check | Command | Expected |
|-------|---------|----------|
| JS deps install | `pnpm install` | exits 0, no errors |
| Python deps install | `cd backend && pixi install -e care-service` | exits 0 |
| Next.js builds | `cd web && pnpm build` | exits 0 |
| Care service imports | `cd backend && pixi run -e care-service -- python -c "from src.main import app; print('OK')"` | prints `OK` |
| AI service imports | `cd backend && pixi run -e ai-service -- python -c "from src.main import app; print('OK')"` | prints `OK` |
| Prettier check | `pnpm exec prettier --check .` | exits 0 |
| Black check | `cd backend && pixi run -e dev format-check` | exits 0 |
| Flake8 check | `cd backend && pixi run -e dev lint` | exits 0 |
| Makefile check | `make check` | exits 0 |
| Bootstrap script | `./scripts/bootstrap.sh` | exits 0 |
| Pre-commit hook | Create bad JS file → `git add` → `git commit` | lint-staged runs |
| CLI agents | `claude --version && gemini --version && aider --version` | all print versions |

### Manual Verification

These require human confirmation:

1. **Review `PLAN.md`** — verify tech stack versions match your actual environment and decisions
2. **Review `ARCHITECTURE.md`** — verify API routes cover the intended first vertical slice
3. **Review `llm_selection.md`** — verify model picks, costs, and routing match your API access and budget
4. **Review CI workflow** — verify GitHub Actions YAML is valid for your remote (push + test)

> [!TIP]
> After execution, push to GitHub and verify CI runs green on the first push.
