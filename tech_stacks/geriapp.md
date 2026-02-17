# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GeriApp is a stage-adaptive dementia care platform. The core differentiator is **cognitive stage adaptation** — every UI component adjusts complexity, touch targets, and guidance based on the user's dementia stage (early/moderate/advanced). The platform includes web (Next.js 16), mobile (React Native/Expo), and microservice backends (Node.js + Python/FastAPI).

## Working with Claude Code

### Documentation Policy

**CRITICAL**: Do not create `.md` documentation files after completing tasks (e.g., `TASK_COMPLETE.md`, `SESSION_SUMMARY.md`, `*_REPORT.md`).

- ✅ **Do**: Respond in chat, use Serena MCP memory tools for archival
- ❌ **Don't**: Create summary/status/report markdown files
- **Exception**: Only create `.md` files when explicitly requested by the user or updating existing docs

This prevents workspace clutter and redundant documentation. See `.cursor/rules/00-no-documentation-files.mdc` for details.

## Commands

### Starting Services

```bash
# Smart dev (recommended for manual mode — auto-detects running services, starts infra if needed)
pnpm dev                                              # Runs scripts/dev/smart-dev.sh

# Individual services
cd web && pnpm dev                                    # Web portal → http://localhost:4100
cd backend/user-service && pnpm dev                   # User service → http://localhost:8100
cd backend && pixi run -e care-service care-dev       # Care service → http://localhost:8101
cd backend && pixi run -e ai-service ai-dev           # AI service → http://localhost:8102

# Infrastructure only (postgres + redis containers)
pnpm dev:infra                                        # Start postgres (5435) + redis (6479)
pnpm dev:infra:stop                                   # Stop infrastructure

# Docker (all services, one command)
./FIX-DOCKER-AND-START.sh
```

### Testing

```bash
# Web portal (vitest — NOT jest)
cd web && pnpm test                            # All tests
cd web && pnpm vitest run src/path/to/file.test.tsx  # Single test file
cd web && pnpm test:coverage                   # With coverage
cd web && pnpm test:e2e                        # Playwright E2E tests

# Care service (pytest via pixi)
cd backend && pixi run -e care-service care-test                    # All tests
cd backend && pixi run -e care-service -- pytest care-service/tests/test_specific.py -v  # Single file

# AI service
cd backend && pixi run -e ai-service ai-test

# Test database (separate from dev DB - port 5434)
docker-compose -f backend/care-service/docker-compose.test.yml up -d
```

### Type Checking & Linting

```bash
cd web && pnpm type-check      # TypeScript
cd web && pnpm lint             # ESLint
cd backend && pixi run -e dev type-check   # Python mypy
cd backend && pixi run -e dev lint         # Python flake8
cd backend && pixi run -e dev format       # Python black
```

### Database Migrations

```bash
cd backend && pixi run -e care-service care-migrate              # Apply migrations
cd backend && pixi run -e care-service care-migrate-revision "description"  # Generate migration
```

## Architecture

### Service Map

| Service | Tech | Port | Health Check |
|---------|------|:---:|---|
| Web Portal | Next.js 16, React 18, Tailwind, Radix UI | 4100 | `:4100` |
| User Service | Node.js, Express, TypeScript | 8100 | `:8100/health` |
| Care Service | Python 3.11, FastAPI, SQLAlchemy | 8101 | `:8101/api/v1/health` |
| AI Service | Python 3.11, FastAPI, PyTorch, MediaPipe | 8102 | `:8102/health` |
| PostgreSQL | - | 5435 | - |
| Redis | - | 6479 | - |

**Database**: `postgresql://geriapp:dev_password@localhost:5435/geriapp`

### Monorepo Structure

- **pnpm workspaces**: `web/`, `mobile/`, `backend/user-service/`, `backend/shared/`, `packages/*`
- **Pixi environments** (not in pnpm workspace): `backend/care-service/`, `backend/ai-service/` — managed via `backend/pixi.toml`
- Python services MUST use pixi or `run.py` to set PYTHONPATH for `backend/shared/` imports
- **Node**: >=22.0.0, **pnpm**: >=10.0.0

### Web Portal (`web/src/`)

- **Framework**: Next.js 16 App Router, React 18, TypeScript strict mode
- **Styling**: Tailwind CSS + Radix UI primitives + class-variance-authority
- **State**: React Context (auth, cognitive stage) + React Query (@tanstack/react-query) for server state
- **Testing**: Vitest + Testing Library + MSW (mock API) + Playwright (E2E) + jest-axe (a11y)
- **Path aliases**: `@/` → `./src/`; `@/components/dashboard` → `./src/components/dashboard-layout` (non-obvious remapping)

Key directories:
- `app/(dashboard)/` — App Router pages (dashboard, care-plans, medications, activities, patients, analytics)
- `components/ui/adaptive/` — Stage-adaptive wrappers
- `components/dashboard-layout/` — Shared layout components (PageShell, DetailPageShell, StatCard, CardGrid, TabBar)
- `lib/api/` — API client modules
- `hooks/` — Custom hooks (data fetching via React Query, UI state, realtime)
- `types/` — TypeScript types (must stay in sync with Python schemas)
- `mocks/` — MSW handlers for test API mocking

### Mobile App (`mobile/src/`)

- **Framework**: React Native 0.73+ with Expo
- **Navigation**: Expo Router (file-based routing)
- **State**: React Context + React Query (same pattern as web)
- **Styling**: NativeWind (Tailwind for React Native)
- **Stage adaptation**: Shared logic with web (`useCognitiveStage` hook)
- **Status**: Structure complete, implementation in progress

```bash
cd mobile && pnpm dev          # Start Expo dev server
cd mobile && pnpm ios          # Run iOS simulator
cd mobile && pnpm android      # Run Android emulator
```

### Dashboard Layout Components

All pages use shared layout components from `@/components/dashboard-layout`:
- **PageShell**: Standard page wrapper — title, description, breadcrumbs, actions, loading state. Renders `<section role="region">` with `<h1>`.
- **DetailPageShell**: Wraps PageShell for `[id]` detail pages — icon slot, status badge, TabBar integration.
- **StatCard**: Stat display card — colors: gray/blue/green/purple/orange/red/yellow. Props: icon, title, value, subtitle, color, isLoading.
- **CardGrid**: Responsive grid for stat cards. `columns` prop (2/3/4).
- **TabBar**: Standalone tab navigation — uses `border-primary text-primary` for active state.
- **Gold standard page**: `web/src/app/(dashboard)/medications/page.tsx`

### Backend

- `backend/shared/database/models.py` — SQLAlchemy models (**source of truth** for all data types)
- `backend/shared/schemas/` — Pydantic validation schemas
- `backend/care-service/src/api/` — FastAPI routers
- `backend/care-service/src/services/` — Business logic layer
- `backend/care-service/src/core/dependencies.py` — Reusable FastAPI dependencies (`CurrentUser`, `DbSession`, `require_roles()`)
- `backend/user-service/src/config/websocket.ts` — Socket.IO server with JWT auth + Redis adapter

### Git Workflow

- **Main branch**: `production` (PRs target this)
- **Development branch**: `development`
- Feature branches off `development`, merge to `development`, then to `production`

## Critical Patterns

### Stage-Adaptive UI

Every user-facing component must adapt to cognitive stage. This is the product's core value.

```typescript
import { useCognitiveStage } from '@/hooks/useCognitiveStage';

function MyComponent({ cognitiveStage }: { cognitiveStage: CognitiveStage }) {
  const { getTouchTargetClasses, getTextClasses } = useCognitiveStage(cognitiveStage);
  return (
    <Button className={cn(getTouchTargetClasses(), getTextClasses('base'))}>Save</Button>
  );
}
```

Stage specs (`web/src/utils/stage-helpers.ts`):
- **Early**: 44px touch targets, 16px text, full UI complexity, 3 nav levels
- **Moderate**: 58px touch targets, 18px text, simplified UI, 2 nav levels
- **Advanced**: 78px touch targets, 20px text, minimal UI, 1 nav level

### Type Synchronization (Three-Layer Sync)

When modifying data models, update all three layers in order:
1. **SQLAlchemy** (`backend/shared/database/models.py`) — source of truth
2. **Pydantic** (`backend/shared/schemas/`) — API validation
3. **TypeScript** (`web/src/types/`) — frontend types

### FastAPI Dependencies (care-service)

Reusable dependency types in `backend/care-service/src/core/dependencies.py`:

```python
from src.core.dependencies import DbSession, CurrentUser, require_roles

@router.get("/items")
async def get_items(db: DbSession, current_user: CurrentUser):
    ...

@router.delete("/items/{id}", dependencies=[Depends(require_roles("admin"))])
async def delete_item(item_id: UUID, db: DbSession, current_user: CurrentUser):
    ...
```

- `CurrentUser = Annotated[Dict[str, Any], Depends(verify_user_token)]` — NEVER add `= Depends(verify_user_token)` on top of `CurrentUser` (double Depends error)
- `require_roles()` inner function must use `CurrentUser` type, not plain `Dict[str, Any]` (FastAPI can't resolve sub-deps without Annotated)
- Role constants: `PROVIDER_ROLES`, `CLINICAL_ROLES`, `SYSTEM_TEMPLATE_ROLES`, `TEMPLATE_WRITE_ROLES`, `ADMIN_ONLY`

### SQLAlchemy: Tables vs Models

Not all database objects are ORM Models. Association tables (like `user_caregivers`) are `Table` objects.

```python
# Table objects → use insert()/update()
stmt = insert(user_caregivers).values(user_id=id, caregiver_id=cid, is_active=True)
await db.execute(stmt)

# Model classes → use db.add()
user = User(id=uuid(), email='user@example.com', role='patient')
db.add(user)
```

Soft delete pattern: set `is_active=False` instead of deleting rows.

### Real-time (WebSocket)

Socket.IO with JWT auth, Redis adapter. Client: `web/src/lib/socket.ts`, hook: `useRealtime()`. Events: `notification`, `emergency_alert`, `medication_reminder`, `activity_update`. Room patterns: `user:{userId}`, `patient:{patientId}`.

### RBAC (Care Plan Templates)

- Frontend permissions: `web/src/lib/auth/permissions.ts` — patient:read only, caregiver+clinical:CRUD
- Backend guards: `Depends(require_roles(...))` on create/update/delete endpoints
- Service layer accepts `user_role` param for admin privilege escalation on update/delete

## Security Best Practices

- **Input validation**: Validate all user inputs at API boundaries using Pydantic schemas
- **SQL injection**: Always use SQLAlchemy ORM or parameterized queries — never string concatenation
- **XSS prevention**: React auto-escapes, but sanitize HTML content with DOMPurify if accepting raw HTML
- **CSRF protection**: Enabled by default in FastAPI/Next.js — ensure tokens are properly validated
- **Authentication**: JWT tokens with short expiry (24h), stored in httpOnly cookies where possible
- **Secrets**: Never commit `.env`, `.pem`, `.key` files — use environment variables
- **Rate limiting**: Implement on auth endpoints (use slowapi for FastAPI)
- **Security headers**: CSP, HSTS, X-Frame-Options, SameSite cookies (configured in middleware)

Run security scans before commits:
```bash
cd web && pnpm lint              # ESLint with security plugins
cd backend && pixi run -e dev lint  # Includes bandit security checks
```

## Gotchas

- **Python imports fail**: Always use pixi (`pixi run -e care-service ...`) or `run.py` — they set `PYTHONPATH=.` for shared module imports. Never run `python -m uvicorn` directly.
- **AI service numpy conflict**: `PYTHONNOUSERSITE=1` is critical — user site-packages (`~/.local/lib/python3.11/`) has numpy 2.x which breaks tensorflow/mediapipe (need numpy <2). The `ai-dev` pixi task sets this automatically via environment variable.
- **pytest hangs**: Ensure `backend/care-service/pytest.ini` has `asyncio_mode = strict` and `asyncio_default_fixture_loop_scope = function`.
- **Backend test DB**: Uses port 5434 (`docker-compose -f backend/care-service/docker-compose.test.yml`). The `test_db_session` (sync) and `test_client` (async) use SEPARATE connections — data inserted in one isn't visible in the other.
- **`app.dependency_overrides`**: Global in FastAPI — test fixtures must save/restore, not just `.clear()`.
- **Backend error format**: Responses wrapped as `{"error": {"message": "...", "code": "..."}}` by middleware.
- **Redis SSL with `rediss://`**: SSL is auto-enabled by the protocol. Do NOT pass `ssl=True` explicitly — it causes errors.
- **Docker host binding**: Services must bind to `0.0.0.0`, not `127.0.0.1`, for healthchecks in containers.
- **Port conflicts**: Project uses custom high ports (4100/8100/8101/5435/6479). Kill with `lsof -ti:4100 | xargs kill -9`.
- **Frontend tests with PageShell**: Use `getByRole('heading', { name: '...' })` not `getByText('...')` for titles (title appears in both h1 and breadcrumb). Loading state renders `Loader2` spinner with "Loading..." text.
- **Do not create documentation .md files** after tasks. Only create .md files when explicitly requested.
