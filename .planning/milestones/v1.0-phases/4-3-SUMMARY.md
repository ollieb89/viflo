---
phase: 04-polish-community
plan: 3
subsystem: ui
tags:
  [
    i18n,
    l10n,
    next-i18next,
    react-i18next,
    next.js,
    translations,
    rtl,
    intl-api,
    crowdin,
    pluralization,
  ]

# Dependency graph
requires:
  - phase: 01-core-skills
    provides: frontend-dev-guidelines skill (Next.js/React patterns this skill extends)
provides:
  - i18n-implementation skill with SKILL.md, working Next.js example, translation workflow guide, and i18n patterns reference
affects:
  - app-builder (can now scaffold i18n into new projects)
  - frontend-dev-guidelines (complementary skill for i18n in React/Next.js apps)

# Tech tracking
tech-stack:
  added:
    - next-i18next v15 (Next.js Pages Router i18n)
    - react-i18next v14 (React hook bindings)
    - i18next v23 (core i18n library)
    - i18next-scanner (key extraction tool)
  patterns:
    - Namespace-per-domain translation file organization
    - appWithTranslation + serverSideTranslations for SSR/SSG
    - Trans component for HTML-embedded translations
    - Intl API for date/number/currency formatting (no third-party library)
    - RTL direction via document dir attribute driven by locale
    - Accept-Language middleware for automatic locale routing

key-files:
  created:
    - .agent/skills/i18n-implementation/SKILL.md
    - .agent/skills/i18n-implementation/references/translation-workflow.md
    - .agent/skills/i18n-implementation/references/i18n-patterns.md
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/next-i18next.config.js
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/next.config.js
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/middleware.ts
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/pages/_app.tsx
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/pages/index.tsx
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/components/LanguageSwitcher.tsx
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/components/Navbar.tsx
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/components/LocaleDemo.tsx
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/public/locales/en/common.json
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/public/locales/en/home.json
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/public/locales/es/common.json
    - .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/public/locales/es/home.json
  modified: []

key-decisions:
  - "Use next-i18next (not next-intl) as it pairs directly with existing next.config.js i18n routing"
  - "Use native Intl API for date/number/currency formatting - zero extra dependencies"
  - "Namespace by domain (auth, dashboard, common) not by component for maintainability"
  - "Trans component pattern for inline HTML translations to keep markup out of JSON files"

patterns-established:
  - "Namespace strategy: common for shared UI, one namespace per major domain"
  - "camelCase keys grouped by UI area, not by component name"
  - "serverSideTranslations loads only needed namespaces per page to minimize bundle"
  - "Intl API over third-party libraries for date/number formatting"
  - "RTL detection via locale lookup table, applied as dir attribute on root element"

requirements-completed: []

# Metrics
duration: 18min
completed: 2026-02-23
---

# Phase 4 Plan 3: i18n Implementation Examples Summary

**next-i18next skill with EN/ES Next.js example, translation workflow guide, pluralization/interpolation patterns, and Intl API formatting reference**

## Performance

- **Duration:** 18 min
- **Started:** 2026-02-23T19:00:05Z
- **Completed:** 2026-02-23T19:18:00Z
- **Tasks:** 5
- **Files modified:** 17 created, 0 modified

## Accomplishments

- Created complete i18n-implementation skill with 376-line SKILL.md covering setup, RTL, middleware, and Intl API
- Built working Next.js example with EN/ES translations, language switcher, locale demo, and middleware routing
- Wrote translation workflow guide covering key naming conventions, extraction tools, Crowdin/Phrase/Lokalise integration, and QA process
- Wrote i18n patterns reference covering pluralization, interpolation, context-based translations, dynamic keys, lazy loading, and testing

## Task Commits

Each task was committed atomically:

1. **Tasks 1+2: i18n skill structure and SKILL.md** - `f9a8eb5` (feat) - directory structure + 376-line SKILL.md
2. **Task 3: Next.js i18n working example** - `e8dda8c` (feat) - full Next.js app with EN/ES translations, language switcher, middleware
3. **Task 4: Translation workflow guide** - `57b4d40` (feat) - key naming, extraction, TMS services, QA process
4. **Task 5: i18n patterns reference** - `c5b0210` (feat) - pluralization, interpolation, dynamic keys, lazy loading, testing

Note: Tasks 1 and 2 were committed together because git does not track empty directories; the SKILL.md file was the first trackable artifact.

## Files Created/Modified

- `.agent/skills/i18n-implementation/SKILL.md` - 376-line comprehensive i18n skill index
- `.agent/skills/i18n-implementation/references/translation-workflow.md` - Team workflow, TMS services, QA process
- `.agent/skills/i18n-implementation/references/i18n-patterns.md` - Pluralization, interpolation, context, lazy loading, Intl API
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/next-i18next.config.js` - i18n config (EN, ES locales)
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/next.config.js` - Next.js config with i18n
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/middleware.ts` - Accept-Language locale routing
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/pages/_app.tsx` - appWithTranslation, RTL detection
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/pages/index.tsx` - Home page with getStaticProps
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/components/LanguageSwitcher.tsx` - Language dropdown
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/components/Navbar.tsx` - Translated nav + switcher
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/components/LocaleDemo.tsx` - Intl API demo
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/public/locales/en/{common,home}.json` - English strings
- `.agent/skills/i18n-implementation/assets/examples/nextjs-i18n/public/locales/es/{common,home}.json` - Spanish strings

## Decisions Made

- **next-i18next over next-intl**: next-i18next integrates directly with Next.js Pages Router's built-in i18n routing via `next.config.js`, making it lower friction for the majority of Next.js projects still on Pages Router.
- **Intl API (native) over date-fns/dayjs**: Zero dependency overhead; Intl API is built into every modern browser and Node.js, handles locale-aware formatting for dates, numbers, currencies, lists, and relative time.
- **Namespace by domain**: Grouping by UI domain (`auth`, `dashboard`, `common`) rather than by component makes namespaces stable as component names change during refactoring.
- **Trans component for HTML translations**: Keeps the markup definition in TypeScript (where it belongs) while the text content lives in JSON translation files, preventing broken HTML tags in translation files.

## Deviations from Plan

None - plan executed exactly as written. Tasks 1 and 2 were committed in a single commit due to git not tracking empty directories, but both tasks were completed as specified.

## Issues Encountered

None - execution was straightforward. The only minor note is that git requires at least one file in a directory to track it, so the directory creation (Task 1) and SKILL.md writing (Task 2) were committed as one atomic unit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- i18n-implementation skill is complete and ready for use by any agent working on multi-language features
- The Next.js example can be run with `npm install && npm run dev` as a reference or starting point
- Translation workflow guide is suitable for sharing with translators and translation services

---

_Phase: 04-polish-community_
_Completed: 2026-02-23_

## Self-Check: PASSED

All files verified present on disk:

- FOUND: .agent/skills/i18n-implementation/SKILL.md
- FOUND: .agent/skills/i18n-implementation/references/translation-workflow.md
- FOUND: .agent/skills/i18n-implementation/references/i18n-patterns.md
- FOUND: .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/pages/index.tsx
- FOUND: .agent/skills/i18n-implementation/assets/examples/nextjs-i18n/components/LanguageSwitcher.tsx
- FOUND: .planning/4-3-SUMMARY.md

All commits verified present:

- FOUND: f9a8eb5 (skill structure + SKILL.md)
- FOUND: e8dda8c (Next.js i18n example)
- FOUND: 57b4d40 (translation workflow guide)
- FOUND: c5b0210 (i18n patterns reference)
