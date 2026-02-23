# GSD Quick Reference

## One-Liners

```bash
# Start new project
gsd init

# Full phase cycle
gsd discuss 1 && gsd plan 1 && gsd execute 1 && gsd verify 1

# Quick task (no planning)
gsd quick "Fix login button color"

# Check status
gsd status
```

## File Locations

```
.planning/
├── PROJECT.md           # Project vision
├── REQUIREMENTS.md      # v1/v2 requirements
├── ROADMAP.md           # Phases
├── STATE.md             # Decisions, blockers
├── config.json          # Settings
├── research/            # Research outputs
├── todos/               # Captured ideas
├── {phase}-CONTEXT.md   # Phase decisions
├── {phase}-{N}-PLAN.md  # Task plans
└── {phase}-{N}-SUMMARY.md # Execution results
```

## Task XML Template

```xml
<task type="auto" priority="1">
  <name>{Name}</name>
  <files>{files}</files>
  <action>{instructions}</action>
  <verify>{verification}</verify>
  <done>{completion criteria}</done>
</task>
```

## Task Types

- `type="auto"` - Kimi executes
- `type="manual"` - User executes

## Priorities

- `1` - Blocking/other tasks depend
- `2` - Important but parallelizable
- `3` - Nice to have

## Size Limits

| Artifact | Max Lines |
|----------|-----------|
| PROJECT.md | 500 |
| REQUIREMENTS.md | 300 |
| ROADMAP.md | 200 |
| PLAN.md | 150 |
| Task | 50 |

## Wave Execution

```
Wave 1: Plans 01, 02 (independent)     → parallel
Wave 2: Plans 03, 04 (need 01, 02)     → parallel
Wave 3: Plan 05 (needs 03, 04)         → sequential
```

## Config Options

```json
{
  "mode": "interactive",     // or "yolo"
  "depth": "standard",       // or "quick", "comprehensive"
  "profile": "balanced",     // or "quality", "budget"
  "workflow": {
    "research": true,
    "plan_check": true,
    "verifier": true,
    "auto_advance": false
  }
}
```

## Common Patterns

### Vertical Slice (Preferred)
```
Plan 01: User feature end-to-end
Plan 02: Product feature end-to-end
```
→ Parallelizes well

### Horizontal Layers (Avoid)
```
Plan 01: All models
Plan 02: All APIs
Plan 03: All UI
```
→ Sequential, more conflicts
