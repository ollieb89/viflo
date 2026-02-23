<plan phase="3" plan="1">
  <overview>
    <phase_name>Containerization Skill</phase_name>
    <goal>Create comprehensive Docker/containerization skill with best practices and production patterns</goal>
  </overview>
  
  <dependencies>
    <complete>Phase 2 templates with Dockerfiles</complete>
  </dependencies>
  
  <context>
    <scope>Docker, Docker Compose, container best practices</scope>
    <approach>Reference documentation + helper scripts</approach>
    <current_state>Dockerfiles exist but scattered, no unified skill</current_state>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create skill directory structure</name>
      <files>.agent/skills/containerization/</files>
      <action>
Create directory structure:
- .agent/skills/containerization/
  - SKILL.md
  - scripts/
  - references/
  - assets/templates/
      </action>
      <verify>Directory exists with all subdirectories</verify>
      <done>Directory structure created</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Write SKILL.md</name>
      <files>.agent/skills/containerization/SKILL.md</files>
      <action>
Write SKILL.md with:
- Docker best practices
- Multi-stage builds
- Docker Compose patterns
- Security guidelines
- Production optimization
- Under 500 lines
      </action>
      <verify>SKILL.md complete with frontmatter</verify>
      <done>SKILL.md written</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create Dockerfile generator</name>
      <files>.agent/skills/containerization/scripts/generate-dockerfile.py</files>
      <action>
Create script that generates:
- Multi-stage Dockerfile for various stacks
- Optimized for production
- Security best practices
- Health checks included

Usage: python generate-dockerfile.py --type python --output .
Types: python, node, nextjs, go, rust
      </action>
      <verify>Script generates working Dockerfiles</verify>
      <done>Dockerfile generator working</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create Docker best practices reference</name>
      <files>.agent/skills/containerization/references/docker-best-practices.md</files>
      <action>
Document best practices:
- Layer caching optimization
- Image size reduction
- Security (non-root user, minimal base images)
- Health checks
- Environment variables
- Build context optimization
      </action>
      <verify>Reference comprehensive and actionable</verify>
      <done>Docker best practices documented</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create multi-stage build examples</name>
      <files>.agent/skills/containerization/references/multi-stage-builds.md</files>
      <action>
Document multi-stage build patterns:
- Python (build deps vs runtime)
- Node.js (build vs production)
- Next.js (static export vs server)
- Go (compile vs scratch)
- Benefits and trade-offs
      </action>
      <verify>Examples cover common scenarios</verify>
      <done>Multi-stage examples complete</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create Docker Compose patterns</name>
      <files>.agent/skills/containerization/references/docker-compose-patterns.md</files>
      <action>
Document Compose patterns:
- Development vs production configs
- Environment variable handling
- Volume management
- Network configuration
- Health checks and dependencies
- Scaling services
      </action>
      <verify>Patterns practical and tested</verify>
      <done>Docker Compose patterns documented</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create production checklist</name>
      <files>.agent/skills/containerization/references/production-checklist.md</files>
      <action>
Create deployment checklist:
- Pre-deployment checks
- Security scanning
- Resource limits
- Logging configuration
- Monitoring setup
- Rollback procedures
      </action>
      <verify>Checklist comprehensive for production</verify>
      <done>Production checklist complete</done>
    </task>
  </tasks>
  
  <verification>
    <check>SKILL.md under 500 lines</check>
    <check>Dockerfile generator creates working files</check>
    <check>Best practices documented with examples</check>
    <check>Multi-stage builds explained</check>
    <check>Production checklist actionable</check>
  </verification>
</plan>
