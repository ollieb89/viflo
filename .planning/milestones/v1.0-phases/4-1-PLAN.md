<plan phase="4" plan="1">
  <overview>
    <phase_name>Documentation Review</phase_name>
    <goal>Review and improve all documentation for consistency and completeness</goal>
  </overview>
  
  <dependencies>
    <complete>All previous phases complete</complete>
  </dependencies>
  
  <context>
    <scope>All project documentation</scope>
    <approach>Audit and fix issues</approach>
    <current_state>Documentation exists but needs consistency review</current_state>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Review SKILL.md files</name>
      <files>All .agent/skills/*/SKILL.md</files>
      <action>
Review all SKILL.md files for:
- Consistent frontmatter format
- Under 500 lines
- Complete triggers list
- Working cross-references
- Consistent style
      </action>
      <verify>All SKILL.md files follow conventions</verify>
      <done>SKILL.md files reviewed</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Update main README</name>
      <files>README.md</files>
      <action>
Update main README:
- List all available skills
- Quick start guide
- Link to AGENTS.md
- Project structure overview
- Contribution link
      </action>
      <verify>README comprehensive and up to date</verify>
      <done>README updated</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Check cross-references</name>
      <files>All markdown files</files>
      <action>
Check all internal links:
- Verify relative links work
- Fix broken references
- Standardize link format
- Update outdated references
      </action>
      <verify>All links functional</verify>
      <done>Cross-references checked</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create index of skills</name>
      <files>.agent/skills/INDEX.md</files>
      <action>
Create skill index:
- Table of all skills
- Brief description each
- Usage recommendations
- Difficulty level
      </action>
      <verify>Index complete and useful</verify>
      <done>Skill index created</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Review AGENTS.md</name>
      <files>AGENTS.md</files>
      <action>
Review and update AGENTS.md:
- Check all links work
- Update skill count
- Add new skills references
- Verify build commands
      </action>
      <verify>AGENTS.md current and accurate</verify>
      <done>AGENTS.md reviewed</done>
    </task>
  </tasks>
  
  <verification>
    <check>All SKILL.md files consistent</check>
    <check>README comprehensive</check>
    <check>No broken links</check>
    <check>AGENTS.md current</check>
  </verification>
</plan>
