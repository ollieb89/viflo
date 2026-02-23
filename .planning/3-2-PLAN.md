<plan phase="3" plan="2">
  <overview>
    <phase_name>CI/CD Pipeline Templates</phase_name>
    <goal>Create reusable CI/CD pipeline templates and documentation for common workflows</goal>
  </overview>
  
  <dependencies>
    <complete>Containerization skill</complete>
    <complete>E2E testing CI/CD reference</complete>
  </dependencies>
  
  <context>
    <scope>GitHub Actions, lint/test/build/deploy workflows</scope>
    <approach>Template files + workflow generator</approach>
    <current_state>Basic CI/CD in E2E skill, no comprehensive templates</current_state>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create CI/CD skill structure</name>
      <files>.agent/skills/ci-cd-pipelines/</files>
      <action>
Create directory:
- .agent/skills/ci-cd-pipelines/
  - SKILL.md
  - workflows/
  - scripts/
  - references/
      </action>
      <verify>Directory structure complete</verify>
      <done>Structure created</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Write SKILL.md</name>
      <files>.agent/skills/ci-cd-pipelines/SKILL.md</files>
      <action>
Write SKILL.md with:
- CI/CD fundamentals
- GitHub Actions overview
- Workflow triggers and events
- Secret management
- Matrix builds
- Caching strategies
- Under 500 lines
      </action>
      <verify>SKILL.md comprehensive</verify>
      <done>SKILL.md written</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create workflow generator</name>
      <files>.agent/skills/ci-cd-pipelines/scripts/generate-workflow.py</files>
      <action>
Create script that generates:
- GitHub Actions workflow files
- For different project types (Python, Node, full-stack)
- With lint, test, build, deploy stages
- Customizable via arguments

Usage: python generate-workflow.py --type fullstack --deploy vercel
      </action>
      <verify>Script generates valid workflow files</verify>
      <done>Workflow generator working</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create Python project workflow</name>
      <files>.agent/skills/ci-cd-pipelines/workflows/python.yml</files>
      <action>
Create workflow template for Python projects:
- Lint (ruff, black, mypy)
- Test (pytest with coverage)
- Build Docker image
- Push to registry
- Deploy to staging/production
      </action>
      <verify>Workflow covers Python project lifecycle</verify>
      <done>Python workflow template created</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create Node.js project workflow</name>
      <files>.agent/skills/ci-cd-pipelines/workflows/nodejs.yml</files>
      <action>
Create workflow template for Node.js projects:
- Lint (ESLint, Prettier)
- Test (Jest/Vitest)
- Type check (TypeScript)
- Build
- Deploy (Vercel/Netlify)
      </action>
      <verify>Workflow covers Node.js project lifecycle</verify>
      <done>Node.js workflow template created</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create full-stack workflow</name>
      <files>.agent/skills/ci-cd-pipelines/workflows/fullstack.yml</files>
      <action>
Create workflow for full-stack projects:
- Backend tests and build
- Frontend tests and build
- E2E tests
- Build and push Docker images
- Deploy backend (ECS/Railway)
- Deploy frontend (Vercel)
      </action>
      <verify>Workflow handles multi-service deployment</verify>
      <done>Full-stack workflow template created</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create secret management guide</name>
      <files>.agent/skills/ci-cd-pipelines/references/secret-management.md</files>
      <action>
Document secret management:
- GitHub Secrets
- Environment variables
- Doppler/1Password integration
- Best practices (no hardcoded secrets)
- Rotation strategies
      </action>
      <verify>Guide security-focused and practical</verify>
      <done>Secret management guide complete</done>
    </task>
  </tasks>
  
  <verification>
    <check>SKILL.md under 500 lines</check>
    <check>Workflow generator creates valid files</check>
    <check>3 workflow templates provided</check>
    <check>Secret management documented</check>
  </verification>
</plan>
