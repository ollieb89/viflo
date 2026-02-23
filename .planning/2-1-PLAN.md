<plan phase="2" plan="1">
  <overview>
    <phase_name>Database Design Skill Enhancement</phase_name>
    <goal>Enhance database-design skill with PostgreSQL-specific patterns, schema generator, and migration tools</goal>
  </overview>
  
  <dependencies>
    <complete>Phase 1 skills (frontend, backend)</complete>
  </dependencies>
  
  <context>
    <scope>PostgreSQL, SQLAlchemy 2.0, Alembic migrations</scope>
    <approach>Generator scripts for common patterns, reference documentation</approach>
    <current_state>Basic SKILL.md (52 lines) with 6 reference files, 1 script</current_state>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Review and enhance SKILL.md</name>
      <files>.agent/skills/database-design/SKILL.md</files>
      <action>
Enhance SKILL.md:
- Keep frontmatter, expand triggers
- Add quick start section
- Add code generation instructions
- Reference existing files
- Keep under 500 lines (currently 52)
      </action>
      <verify>SKILL.md comprehensive but under 500 lines</verify>
      <done>SKILL.md enhanced</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create schema generator script</name>
      <files>.agent/skills/database-design/scripts/generate-schema.py</files>
      <action>
Create script that generates:
- SQLAlchemy 2.0 model from field definitions
- Alembic migration stub
- Pydantic schemas for the model
- Basic repository class

Usage: python generate-schema.py User --fields "email:str,name:str,active:bool"
      </action>
      <verify>Script runs and generates working code</verify>
      <done>Schema generator working</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create PostgreSQL patterns reference</name>
      <files>.agent/skills/database-design/references/postgresql-patterns.md</files>
      <action>
Document PostgreSQL-specific patterns:
- Data types (UUID, JSONB, Arrays)
- Constraints and indexes
- Full-text search
- Triggers and functions
- Partitioning strategies
- Row Level Security (RLS)
      </action>
      <verify>Reference covers common PostgreSQL patterns</verify>
      <done>PostgreSQL patterns documented</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create migration helper script</name>
      <files>.agent/skills/database-design/scripts/migration-helper.py</files>
      <action>
Create script for common migration tasks:
- Generate safe migration commands
- Check migration safety (destructive ops)
- Rollback helper
- Migration status viewer

Usage: python migration-helper.py check alembic/versions/xxx.py
      </action>
      <verify>Script provides useful migration utilities</verify>
      <done>Migration helper working</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Add database template</name>
      <files>.agent/skills/database-design/assets/templates/postgres-setup/</files>
      <action>
Create minimal PostgreSQL setup template:
- docker-compose.yml with Postgres
- init scripts for extensions
- sample SQLAlchemy config
- Connection pooling example
- Health check script
      </action>
      <verify>Template can be copied and runs with docker-compose up</verify>
      <done>Postgres template ready</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create index optimization guide</name>
      <files>.agent/skills/database-design/references/index-optimization.md</files>
      <action>
Document index optimization:
- When to add indexes
- Composite index ordering
- Partial indexes
- Index-only scans
- EXPLAIN ANALYZE usage
- Common indexing mistakes
      </action>
      <verify>Guide helps optimize query performance</verify>
      <done>Index optimization guide complete</done>
    </task>
  </tasks>
  
  <verification>
    <check>SKILL.md comprehensive and under 500 lines</check>
    <check>Schema generator tested and working</check>
    <check>PostgreSQL patterns documented</check>
    <check>Migration helper provides value</check>
    <check>Template runs with docker-compose</check>
  </verification>
</plan>
