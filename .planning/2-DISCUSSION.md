# Phase 2 Discussion: Extended Skills & Examples

**Date**: 2026-02-23  
**Participants**: AI Assistant  
**Phase**: 2 - Extended Skills & Examples  
**Status**: discussing → ready for execution

---

## Context Review

Phase 1 has been successfully completed with:
- ✅ GSD Workflow skill (12 helper scripts)
- ✅ Frontend-dev-guidelines (component generator, Next.js template)
- ✅ Backend-dev-guidelines (endpoint generator, FastAPI template)

Now entering Phase 2 to address requirements R8, R9, R10:
- R8: Database design skill enhancement (PostgreSQL)
- R9: E2E testing skill enhancement (Playwright)
- R10: Example project templates

---

## Plans Overview

### Plan 2-1: Database Design Skill Enhancement
**Duration**: ~60 minutes

The existing `database-design` skill has:
- 52-line SKILL.md (basic, needs enhancement)
- 6 reference files (schema-design, indexing, migrations, etc.)
- 1 script (schema_validator.py)

**Proposed Additions:**
1. **Schema Generator**: `generate-schema.py User --fields "email:str,name:str"`
   - Generates SQLAlchemy 2.0 model
   - Creates Alembic migration stub
   - Creates Pydantic schemas
   
2. **PostgreSQL Patterns**: Document JSONB, arrays, RLS, partitioning

3. **Migration Helper**: Safety checks, rollback helper, status viewer

4. **Postgres Template**: Docker Compose + connection pooling config

5. **Index Optimization**: Guide for composite, partial indexes

**Key Decisions:**
- Focus on PostgreSQL only (not generic SQL)
- SQLAlchemy 2.0 patterns (consistent with backend skill)
- Generator follows Phase 1 style (Python CLI)

---

### Plan 2-2: E2E Testing Skill Enhancement
**Duration**: ~50 minutes

The existing `e2e-testing-patterns` skill has:
- 544-line SKILL.md (already comprehensive)
- No scripts or templates

**Proposed Additions:**
1. **Test Generator**: `generate-test.py Login --page --crud`
   - Page Object Model class
   - Playwright spec file
   - Data-testid reference
   
2. **Playwright Template**: Complete project setup
   - playwright.config.ts
   - fixtures for auth
   - Example page object
   - Sample tests

3. **Page Object Examples**: Forms, tables, modals

4. **Test Data Management**: API seeding, cleanup patterns

5. **CI/CD Integration**: GitHub Actions workflow

**Key Decisions:**
- Focus on Playwright (not Cypress, despite SKILL.md mentioning both)
- Use official Playwright template as base
- Generator creates TypeScript (consistent with frontend)

---

### Plan 2-3: Example Project Templates
**Duration**: ~100 minutes  
**Dependencies**: Plan 2-1, Plan 2-2

**Proposed Examples:**

1. **Task Management App** (Full-Stack CRUD)
   - Frontend: Next.js + MUI + TanStack Query
   - Backend: FastAPI + SQLAlchemy + PostgreSQL
   - Features: Auth, CRUD, filtering, pagination
   - Tests: Unit + E2E
   - DevOps: Docker Compose

2. **E-Commerce App** (Complex Patterns)
   - Products catalog, cart, checkout
   - Complex relationships (orders, items, products)
   - Transactions, search, responsive design

3. **Minimal Starter** (Quick Start)
   - Single page, single endpoint
   - No auth (simpler)
   - Basic tests

**Key Decisions:**
- Examples demonstrate ALL Phase 1 and 2 skills
- Each example must run with `docker-compose up`
- Comprehensive READMEs required
- Realistic but not over-engineered

---

## Execution Strategy

```
Wave 1 (Parallel)
=================
Plan 2-1: Database        Plan 2-2: E2E Testing
(60 min)                  (50 min)
     \                      /
      \                    /
       \                  /
        \                /
         ▼              ▼
      Wave 2 (Sequential)
      ==================
      Plan 2-3: Examples
      (100 min)
```

**Rationale:**
- Plans 2-1 and 2-2 are independent (different skills)
- Plan 2-3 depends on both (examples use generators)
- Parallel execution saves ~50 minutes

---

## Risk Discussion

| Risk | Mitigation | Status |
|------|------------|--------|
| Example apps too complex | Start minimal, add features if time | Accepted |
| Playwright template issues | Use official template base | Accepted |
| Database patterns scope creep | PostgreSQL only, not generic | Accepted |
| Time overrun | Can drop P3 tasks (minimal starter) | Contingency |

---

## Questions for Discussion

### 1. Scope Confirmation
Should we focus exclusively on PostgreSQL for database patterns, or include SQLite/MySQL considerations?

**Recommendation**: PostgreSQL only for Phase 2. Other databases can be added in Phase 4.

### 2. Example App Complexity
Should the task app include real-time features (WebSockets) or keep it simple REST?

**Recommendation**: Keep it simple REST. WebSockets can be a future enhancement.

### 3. E2E Framework Choice
The SKILL.md mentions both Playwright and Cypress. Should we support both or focus on Playwright only?

**Recommendation**: Playwright only for generators/templates. Cypress stays in SKILL.md as reference.

### 4. Documentation Language
Should example READMEs include setup for both Docker and local development?

**Recommendation**: Yes, both paths documented. Docker is primary, local is secondary.

---

## Pre-Execution Checklist

- [x] Phase 1 complete
- [x] All 3 plans created
- [x] Dependencies mapped
- [x] Risks assessed
- [x] Execution strategy defined
- [ ] Wave 1 execution approved
- [ ] Wave 2 execution approved

---

## Decision Record

| Decision | Rationale | Approved |
|----------|-----------|----------|
| PostgreSQL only | Consistent with Phase 1 backend skill | ⏳ |
| Playwright focus | Modern, faster, better DX | ⏳ |
| Simple REST examples | Scope control | ⏳ |
| Parallel execution | Efficiency | ⏳ |

---

## Next Actions

1. Approve decisions above
2. Transition to executing state
3. Start Wave 1 (Plans 2-1 and 2-2 in parallel)
4. After Wave 1 complete, start Wave 2 (Plan 2-3)

---

**Ready to proceed with execution?**

Options:
- **Approve & Start**: Begin Wave 1 execution
- **Modify Plans**: Adjust scope or approach
- **Add Questions**: Clarify requirements
