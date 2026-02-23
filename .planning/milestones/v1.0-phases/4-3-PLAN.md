<plan phase="4" plan="3">
  <overview>
    <phase_name>i18n Implementation Examples</phase_name>
    <goal>Create multi-language support examples for applications</goal>
  </overview>
  
  <dependencies>
    <complete>Frontend skill with Next.js</complete>
  </dependencies>
  
  <context>
    <scope>Internationalization examples</scope>
    <approach>Create working example with translations</approach>
    <current_state>No i18n examples exist</current_state>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create i18n skill structure</name>
      <files>.agent/skills/i18n-implementation/</files>
      <action>
Create skill directory:
- .agent/skills/i18n-implementation/
  - SKILL.md
  - references/
  - assets/examples/
      </action>
      <verify>Directory structure complete</verify>
      <done>Structure created</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Write i18n SKILL.md</name>
      <files>.agent/skills/i18n-implementation/SKILL.md</files>
      <action>
Write SKILL.md covering:
- i18n fundamentals
- Next.js i18n setup
- Translation files structure
- Language switching
- RTL support
- Date/number formatting
- Under 500 lines
      </action>
      <verify>SKILL.md comprehensive</verify>
      <done>SKILL.md written</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create Next.js i18n example</name>
      <files>.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/</files>
      <action>
Create working example:
- next-i18next setup
- English translations
- Spanish translations
- Language switcher component
- Middleware for routing
- RTL support demo
      </action>
      <verify>Example runs and switches languages</verify>
      <done>Next.js example created</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create translation workflow guide</name>
      <files>.agent/skills/i18n-implementation/references/translation-workflow.md</files>
      <action>
Document translation workflow:
- Managing translation files
- Translation keys naming
- Extracting translations
- Translation services (Crowdin, etc.)
- QA process
      </action>
      <verify>Guide practical for teams</verify>
      <done>Translation workflow documented</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create i18n patterns reference</name>
      <files>.agent/skills/i18n-implementation/references/i18n-patterns.md</files>
      <action>
Document common patterns:
- Dynamic translations
- Pluralization
- Interpolation
- Context-specific translations
- Lazy loading translations
      </action>
      <verify>Patterns cover common scenarios</verify>
      <done>i18n patterns documented</done>
    </task>
  </tasks>
  
  <verification>
    <check>SKILL.md under 500 lines</check>
    <check>Next.js example working</check>
    <check>Translation workflow documented</check>
    <check>i18n patterns comprehensive</check>
  </verification>
</plan>
