# Phase 1 Context: Core Skills Development

## Phase Goal

Create essential development skills for the Viflo ecosystem:
1. Frontend development guidelines (React/Next.js)
2. Backend development guidelines (FastAPI)

## Current State

- ✅ GSD Workflow skill: Complete with 12 scripts, 9 templates, 2 examples
- ⏳ Frontend skill: Needs to be created
- ⏳ Backend skill: Needs to be created

## Decisions to Make

### Frontend Skill

- [ ] **Scope**: What should the frontend skill cover?
  - React 19 + Next.js 16?
  - TypeScript patterns?
  - Tailwind CSS v4?
  - Component architecture?
  - State management (Zustand, Redux, Context)?
  
- [ ] **Approach**: How prescriptive should it be?
  - Strict conventions vs flexible guidelines?
  - Code examples or just patterns?
  
- [ ] **Scripts**: Any automation needed?
  - Component generator?
  - Page scaffold?
  - API route generator?

### Backend Skill

- [ ] **Scope**: What should the backend skill cover?
  - FastAPI patterns?
  - SQLAlchemy 2.0 models?
  - Pydantic schemas?
  - Authentication patterns?
  - API design (REST vs GraphQL)?
  
- [ ] **Database**: Which patterns to include?
  - Repository pattern?
  - Unit of work?
  - Migrations with Alembic?
  
- [ ] **Testing**: What testing approach?
  - pytest structure?
  - Test database setup?
  - Fixtures and factories?

## Resource Constraints

- **Time**: Each skill should take ~1-2 focused sessions
- **Size**: SKILL.md should be < 500 lines (follow progressive disclosure)
- **Quality**: Must include practical examples, not just theory

## Priorities

1. **Frontend skill first** - Most common need
2. **Backend skill second** - Depends on frontend patterns
3. **Both should work together** - Full-stack consistency

## Questions for Discussion

1. Should we create a "full-stack" skill that combines frontend + backend workflows?
2. Do we need database design skill before backend skill?
3. Should skills include example projects or just guidelines?
4. How do we keep skills updated with framework changes?

## Notes

- Follow existing skill structure (SKILL.md + scripts/ + references/ + assets/)
- Use GSD workflow itself to develop these skills (dogfooding)
- Consider what would help the GSD workflow skill development
