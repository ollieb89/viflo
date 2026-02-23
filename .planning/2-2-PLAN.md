<plan phase="2" plan="2">
  <overview>
    <phase_name>E2E Testing Skill Enhancement</phase_name>
    <goal>Enhance e2e-testing-patterns with test generator and Playwright project template</goal>
  </overview>
  
  <dependencies>
    <complete>Phase 1 frontend skill</complete>
  </dependencies>
  
  <context>
    <scope>Playwright, Page Object Model, critical user journeys</scope>
    <approach>Generator for test scaffolding, reusable patterns</approach>
    <current_state>Comprehensive SKILL.md (544 lines), no scripts or templates</current_state>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Review existing SKILL.md</name>
      <files>.agent/skills/e2e-testing-patterns/SKILL.md</files>
      <action>
Review existing SKILL.md:
- Already 544 lines, comprehensive
- Check if any updates needed for consistency
- Ensure frontmatter is complete
- Add section on code generation if missing
      </action>
      <verify>SKILL.md up to date and complete</verify>
      <done>SKILL.md reviewed</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create test generator script</name>
      <files>.agent/skills/e2e-testing-patterns/scripts/generate-test.py</files>
      <action>
Create script that generates:
- Playwright spec file with Page Object Model
- Page class for the feature
- Test cases for CRUD operations
- Data test IDs reference

Usage: python generate-test.py Login --page --crud
      </action>
      <verify>Script generates working Playwright tests</verify>
      <done>Test generator working</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create Playwright project template</name>
      <files>.agent/skills/e2e-testing-patterns/assets/templates/playwright-project/</files>
      <action>
Create minimal Playwright setup:
- playwright.config.ts with best practices
- e2e/ directory structure
- fixtures for auth state
- utils for common operations
- Example page object (LoginPage)
- Sample test spec
- README with setup instructions
      </action>
      <verify>Template runs with npm install && npx playwright test</verify>
      <done>Playwright template ready</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create Page Object Model examples</name>
      <files>.agent/skills/e2e-testing-patterns/references/page-object-examples.md</files>
      <action>
Document Page Object Model patterns:
- Base page class
- Common page methods (waitForLoad, isVisible)
- Form handling patterns
- Table/list interactions
- Modal/dialog handling
- File upload patterns
      </action>
      <verify>Examples cover common UI patterns</verify>
      <done>Page Object examples documented</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create test data management guide</name>
      <files>.agent/skills/e2e-testing-patterns/references/test-data-management.md</files>
      <action>
Document test data strategies:
- API seeding vs UI setup
- Test isolation techniques
- Data cleanup patterns
- Environment-specific data
- Factory patterns for test data
      </action>
      <verify>Guide helps manage test data effectively</verify>
      <done>Test data guide complete</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create CI/CD integration guide</name>
      <files>.agent/skills/e2e-testing-patterns/references/ci-cd-integration.md</files>
      <action>
Document CI/CD patterns:
- GitHub Actions workflow
- Parallel test execution
- Artifact collection (screenshots, videos)
- Retry strategies
- Sharding for large suites
- Preview environment testing
      </action>
      <verify>Guide enables CI/CD integration</verify>
      <done>CI/CD guide complete</done>
    </task>
  </tasks>
  
  <verification>
    <check>SKILL.md up to date</check>
    <check>Test generator creates working tests</check>
    <check>Playwright template runs successfully</check>
    <check>Page Object examples comprehensive</check>
    <check>CI/CD integration documented</check>
  </verification>
</plan>
