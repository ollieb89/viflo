<plan phase="1" plan="2">
  <overview>
    <phase_name>Backend Development Skill</phase_name>
    <goal>Create comprehensive backend development skill for FastAPI with SQLAlchemy 2.0</goal>
  </overview>
  
  <dependencies>
    <complete>Plan 1: Frontend Development Skill</complete>
  </dependencies>
  
  <context>
    <scope>FastAPI, SQLAlchemy 2.0, Pydantic v2, PostgreSQL</scope>
    <approach>API-first design, repository pattern, test-driven</approach>
    <integration>Should align with frontend skill patterns</integration>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create skill directory structure</name>
      <files>.agent/skills/backend-dev-guidelines/</files>
      <action>
Create directory structure:
- .agent/skills/backend-dev-guidelines/
  - SKILL.md
  - scripts/
  - references/
  - assets/
    - templates/
    - examples/
      </action>
      <verify>Directory exists with all subdirectories</verify>
      <done>Directory structure created</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Write SKILL.md frontmatter and overview</name>
      <files>.agent/skills/backend-dev-guidelines/SKILL.md</files>
      <action>
Write SKILL.md with:
- name: backend-dev-guidelines
- description: Comprehensive guide for FastAPI backend development. Use when creating APIs, database models, authentication, or business logic.
- Overview section with tech stack
- Core principles (API design, data modeling, testing)
      </action>
      <verify>SKILL.md exists with proper frontmatter</verify>
      <done>SKILL.md structure complete</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create API design patterns reference</name>
      <files>.agent/skills/backend-dev-guidelines/references/api-patterns.md</files>
      <action>
Document API patterns:
- RESTful resource naming
- CRUD endpoint patterns
- Request/response schemas with Pydantic
- Error handling and HTTP status codes
- Pagination strategies
- Authentication with JWT
- Dependency injection patterns
      </action>
      <verify>API patterns documented with examples</verify>
      <done>API patterns reference complete</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create database modeling reference</name>
      <files>.agent/skills/backend-dev-guidelines/references/database-models.md</files>
      <action>
Document database patterns:
- SQLAlchemy 2.0 declarative models
- Relationship patterns (one-to-many, many-to-many)
- Repository pattern implementation
- Unit of work pattern
- Migration best practices (Alembic)
- Soft delete implementation
      </action>
      <verify>Database patterns documented</verify>
      <done>Database modeling guide complete</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create API endpoint generator script</name>
      <files>.agent/skills/backend-dev-guidelines/scripts/generate-endpoint.py</files>
      <action>
Create script that generates:
- Pydantic schemas (Create, Update, Response)
- SQLAlchemy model
- Repository class
- FastAPI router with CRUD endpoints
- pytest test file
      </action>
      <verify>Script runs and generates working endpoint</verify>
      <done>Endpoint generator working</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Add example project template</name>
      <files>.agent/skills/backend-dev-guidelines/assets/templates/fastapi-app/</files>
      <action>
Create minimal FastAPI template:
- app/ directory structure
- Database configuration
- Sample models and schemas
- Sample router with endpoints
- Test setup with pytest
- Docker compose for Postgres
      </action>
      <verify>Template can be copied and runs with docker-compose up</verify>
      <done>Example template ready</done>
    </task>
  </tasks>
  
  <verification>
    <check>Skill directory structure complete</check>
    <check>SKILL.md under 500 lines</check>
    <check>Endpoint generator tested</check>
    <check>Example template runs with Docker</check>
  </verification>
</plan>
