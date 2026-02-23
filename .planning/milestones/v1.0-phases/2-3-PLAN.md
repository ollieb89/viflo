<plan phase="2" plan="3">
  <overview>
    <phase_name>Example Project Templates</phase_name>
    <goal>Create complete, working example projects demonstrating Viflo methodology</goal>
  </overview>
  
  <dependencies>
    <plan>Plan 2-1: Database Design Skill</plan>
    <plan>Plan 2-2: E2E Testing Skill</plan>
    <complete>Phase 1 frontend and backend skills</complete>
  </dependencies>
  
  <context>
    <scope>Full-stack applications with frontend, backend, database, tests</scope>
    <approach>Realistic examples demonstrating all skills</approach>
    <current_state>No example projects exist</current_state>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create task management app example</name>
      <files>.agent/skills/app-builder/assets/templates/task-app/</files>
      <action>
Create full-stack task management app:
- Frontend: Next.js + MUI + TanStack Query
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL with migrations
- Features: CRUD tasks, filtering, pagination
- Auth: JWT authentication
- Tests: Unit + E2E (Playwright)
- DevOps: Docker Compose setup

Structure:
task-app/
├── frontend/ (Next.js)
├── backend/ (FastAPI)
├── e2e/ (Playwright)
├── docker-compose.yml
└── README.md
</action>
<verify>App runs with docker-compose up and all features work</verify>
<done>Task app example complete</done>
</task>

    <task type="auto" priority="1">
      <name>Create e-commerce app example</name>
      <files>.agent/skills/app-builder/assets/templates/ecommerce-app/</files>
      <action>

Create simplified e-commerce example:

- Frontend: Product catalog, cart, checkout UI
- Backend: Products API, orders API
- Database: Products, orders, customers tables
- Features: Product listing, cart, order placement
- Tests: API tests + E2E tests
- DevOps: Docker Compose

Focus on demonstrating:

- Complex relationships (orders, items, products)
- Transaction handling
- Search/filter functionality
- Responsive design
  </action>
  <verify>App demonstrates e-commerce patterns</verify>
  <done>E-commerce example complete</done>
  </task>
  <task type="auto" priority="2">
  <name>Create README template for examples</name>
  <files>.agent/skills/app-builder/assets/templates/README-template.md</files>
  <action>
  Create standardized README template for all examples:
- Overview and features
- Tech stack
- Quick start (docker-compose)
- Project structure
- Testing instructions
- Development guide
- Deployment notes
  </action>
  <verify>Template is comprehensive and reusable</verify>
  <done>README template created</done>
  </task>
  <task type="auto" priority="2">
  <name>Create example documentation guide</name>
  <files>.agent/skills/app-builder/references/example-patterns.md</files>
  <action>
  Document patterns for creating examples:
- Project structure conventions
- Tech stack choices
- What makes a good example
- Testing requirements
- Documentation standards
- Maintenance guidelines
  </action>
  <verify>Guide helps create consistent examples</verify>
  <done>Example patterns documented</done>
  </task>
  <task type="auto" priority="2">
  <name>Create app-builder skill enhancement</name>
  <files>.agent/skills/app-builder/SKILL.md</files>
  <action>
  Enhance app-builder skill:
- Reference example templates
- Add quick start for scaffolding
- Document customization steps
- Add troubleshooting guide
- Keep under 500 lines
  </action>
  <verify>SKILL.md references examples and provides guidance</verify>
  <done>App-builder skill enhanced</done>
  </task>
  <task type="auto" priority="3">
  <name>Create minimal starter template</name>
  <files>.agent/skills/app-builder/assets/templates/minimal-app/</files>
  <action>
  Create minimal full-stack starter:
- Frontend: Single page with data fetching
- Backend: Single CRUD endpoint
- Database: Single table
- Tests: Basic API + E2E tests
- No auth (simpler)

Purpose: Quick start for new projects
</action>
<verify>Template is minimal but functional</verify>
<done>Minimal starter created</done>
</task>
</tasks>

  <verification>
    <check>Task app example runs and tests pass</check>
    <check>E-commerce example demonstrates complex patterns</check>
    <check>All examples have comprehensive READMEs</check>
    <check>Docker Compose works for all examples</check>
    <check>Examples follow Viflo methodology</check>
  </verification>
</plan>
