<plan phase="1" plan="1">
  <overview>
    <phase_name>Frontend Development Skill</phase_name>
    <goal>Create comprehensive frontend development skill for React/Next.js with TypeScript</goal>
  </overview>
  
  <dependencies>
    <complete>Phase 0: Foundation</complete>
  </dependencies>
  
  <context>
    <scope>React 19, Next.js 16, TypeScript 5.7+, Tailwind CSS v4</scope>
    <approach>Practical patterns with examples, progressive disclosure</approach>
    <size_limit>SKILL.md under 500 lines</size_limit>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create skill directory structure</name>
      <files>.agent/skills/frontend-dev-guidelines/</files>
      <action>
Create directory structure:
- .agent/skills/frontend-dev-guidelines/
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
      <files>.agent/skills/frontend-dev-guidelines/SKILL.md</files>
      <action>
Write SKILL.md with:
- name: frontend-dev-guidelines
- description: Comprehensive guide for React/Next.js frontend development. Use when working with React components, Next.js pages, TypeScript types, or Tailwind CSS styling.
- Overview section with tech stack
- Core principles (component design, state management, styling)
      </action>
      <verify>SKILL.md exists with proper frontmatter</verify>
      <done>SKILL.md structure complete</done>
    </task>
    
    <task type="auto" priority="1">
      <name>Create component patterns reference</name>
      <files>.agent/skills/frontend-dev-guidelines/references/component-patterns.md</files>
      <action>
Document component patterns:
- Functional components with hooks
- Props interface design
- Composition patterns
- Compound components
- Render props vs hooks
- Error boundaries
      </action>
      <verify>File exists with pattern examples</verify>
      <done>Component patterns documented</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create state management reference</name>
      <files>.agent/skills/frontend-dev-guidelines/references/state-management.md</files>
      <action>
Document state management:
- useState vs useReducer
- Context API patterns
- Zustand for global state
- Server state with React Query
- Form state with React Hook Form
- When to use each approach
      </action>
      <verify>State management patterns documented</verify>
      <done>State management guide complete</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Create component generator script</name>
      <files>.agent/skills/frontend-dev-guidelines/scripts/generate-component.py</files>
      <action>
Create script that generates:
- Component file (.tsx)
- Props interface
- Storybook story (optional)
- Test file (.test.tsx)
- CSS module or Tailwind classes
      </action>
      <verify>Script runs and generates component files</verify>
      <done>Component generator working</done>
    </task>
    
    <task type="auto" priority="2">
      <name>Add example project template</name>
      <files>.agent/skills/frontend-dev-guidelines/assets/templates/nextjs-app/</files>
      <action>
Create minimal Next.js template:
- app/ directory structure
- Layout with providers
- Sample page with components
- Tailwind config
- TypeScript config
      </action>
      <verify>Template can be copied and runs</verify>
      <done>Example template ready</done>
    </task>
  </tasks>
  
  <verification>
    <check>Skill directory structure complete</check>
    <check>SKILL.md under 500 lines</check>
    <check>Component generator tested</check>
    <check>Example template runs</check>
  </verification>
</plan>
