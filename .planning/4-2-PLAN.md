<plan phase="4" plan="2">
  <overview>
    <phase_name>Contributing Guide</phase_name>
    <goal>Create comprehensive guide for community contributors</goal>
  </overview>
  
  <dependencies>
    <complete>All skills created</complete>
  </dependencies>
  
  <context>
    <scope>Community contribution guidelines</scope>
    <approach>Create templates and guides</approach>
    <current_state>No contributing guide exists</current_state>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create CONTRIBUTING.md</name>
      <files>CONTRIBUTING.md</files>
      <action>
Create contributing guide:
- Welcome message
- Code of conduct reference
- How to report bugs
- How to suggest features
- How to submit PRs
- Development setup
- Testing requirements
      </action>
      <verify>Guide comprehensive and friendly</verify>
      <done>CONTRIBUTING.md created</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create issue templates</name>
      <files>.github/ISSUE_TEMPLATE/</files>
      <action>
Create issue templates:
- Bug report template
- Feature request template
- Skill suggestion template
- Documentation issue template
      </action>
      <verify>Templates helpful and complete</verify>
      <done>Issue templates created</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create PR template</name>
      <files>.github/PULL_REQUEST_TEMPLATE.md</files>
      <action>
Create PR template:
- Description section
- Type of change (feat/fix/docs)
- Testing checklist
- Related issues
- Screenshots (if applicable)
      </action>
      <verify>Template helpful for reviewers</verify>
      <done>PR template created</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create skill creation guide</name>
      <files>docs/CREATING_SKILLS.md</files>
      <action>
Document how to create skills:
- Directory structure
- SKILL.md format
- Frontmatter requirements
- Adding scripts
- Adding references
- Testing skills
      </action>
      <verify>Guide enables skill creation</verify>
      <done>Skill creation guide created</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create code of conduct</name>
      <files>CODE_OF_CONDUCT.md</files>
      <action>
Create code of conduct:
- Pledge
- Standards
- Responsibilities
- Enforcement
- Contact information
      </action>
      <verify>Code of conduct professional</verify>
      <done>Code of conduct created</done>
    </task>
  </tasks>
  
  <verification>
    <check>CONTRIBUTING.md comprehensive</check>
    <check>Issue templates work</check>
    <check>PR template helpful</check>
    <check>Skill creation documented</check>
  </verification>
</plan>
