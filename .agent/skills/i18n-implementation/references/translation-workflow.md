# Translation Workflow Guide

Practical guide for managing translation files across a team, from development to production.

---

## Overview

A typical translation lifecycle:

```
Developer adds key → Source file updated → Extracted to TMS → Translated → Reviewed → Merged → Shipped
```

- **TMS**: Translation Management System (Crowdin, Phrase, Lokalise, etc.)
- **Source locale**: The language developers write first (usually English)
- **Target locales**: Languages that translations are produced for

---

## Managing Translation Files

### File Ownership

| File              | Owner                        |
| ----------------- | ---------------------------- |
| `en/*.json`       | Developers (source of truth) |
| `es/*.json`, etc. | Translators (via TMS or PR)  |

**Rule:** Developers own the source locale. Translators own target locales. Never manually edit a target locale in code unless it is a hotfix.

### Adding New Keys

1. Add the key and English value to the appropriate `en/*.json` namespace file
2. Add a placeholder in each target locale file with the English value as a fallback:

```json
// es/home.json — placeholder while translation is pending
{
  "newFeature": {
    "title": "New Feature Title"
  }
}
```

3. Mark the key as needing translation (via TMS upload or a comment)
4. Remove the placeholder once translated content arrives

### Removing Keys

1. Remove the key from the source (`en/`) file first
2. Remove matching keys from all target locale files
3. Search codebase for any `t('key.path')` usages: `grep -r "t('key.path'" src/`
4. Delete any dead `useTranslation` namespace imports if the namespace is now empty

### Handling Missing Translations

Configure i18next to log missing keys in development:

```js
// next-i18next.config.js
module.exports = {
  i18n: { defaultLocale: "en", locales: ["en", "es"] },
  saveMissing: process.env.NODE_ENV === "development",
  missingKeyHandler: (lng, ns, key) => {
    console.warn(`Missing translation: [${lng}] ${ns}:${key}`);
  },
};
```

---

## Translation Keys Naming Conventions

### Rules

1. **camelCase** for all key names: `firstName`, `submitButton`
2. **Group by UI area**, not by component: `nav.home`, not `Navbar.homeLink`
3. **Semantic names**: `button.save`, not `button.greenButton`
4. **Namespace by domain**: `auth.login.title`, `dashboard.stats.total`
5. **No abbreviations**: `errorMessage`, not `errMsg`

### Good vs Bad Examples

```json
// Good
{
  "auth": {
    "login": {
      "title": "Sign in",
      "emailLabel": "Email address",
      "passwordLabel": "Password",
      "submitButton": "Sign in",
      "forgotPassword": "Forgot your password?"
    }
  }
}

// Bad
{
  "LoginForm_title": "Sign in",
  "email_lbl": "Email address",
  "pwd": "Password",
  "btn1": "Sign in",
  "link_forgot": "Forgot your password?"
}
```

### Namespace Conventions

| Namespace   | Use for                                     |
| ----------- | ------------------------------------------- |
| `common`    | Nav, buttons, generic errors, status labels |
| `auth`      | Login, register, forgot password, 2FA       |
| `dashboard` | Dashboard-specific content                  |
| `[feature]` | One namespace per major feature             |
| `errors`    | Error pages (404, 500), form error messages |

---

## Extracting Translations

### Manual Extraction

Review component files and ensure every hardcoded string is moved to a translation file.

Useful grep pattern to find potentially missed strings:

```bash
# Find JSX text content that is not a translation call
grep -rn ">[A-Z][a-z]" src/ --include="*.tsx" | grep -v "{t(" | grep -v "//\|*"
```

### Automated Extraction with i18next-scanner

Install and configure:

```bash
npm install --save-dev i18next-scanner
```

```js
// i18next-scanner.config.js
module.exports = {
  input: ["src/**/*.{ts,tsx}"],
  output: "./",
  options: {
    debug: false,
    defaultLng: "en",
    lngs: ["en", "es"],
    ns: ["common", "home", "auth", "dashboard"],
    defaultNs: "common",
    resource: {
      loadPath: "public/locales/{{lng}}/{{ns}}.json",
      savePath: "public/locales/{{lng}}/{{ns}}.json",
    },
  },
};
```

```json
// package.json
{
  "scripts": {
    "i18n:extract": "i18next-scanner"
  }
}
```

Running `npm run i18n:extract` will:

- Scan all `.ts`/`.tsx` files for `t('key')` calls
- Add missing keys to source locale files with empty values
- Leave existing translated values untouched

---

## Translation Services

### Crowdin

Best for large teams with dedicated translators.

**Workflow:**

1. Connect GitHub repository to Crowdin project
2. Crowdin automatically opens PRs when translations are ready
3. Set source files to `public/locales/en/*.json`
4. Configure target languages in Crowdin dashboard
5. Translators work inside Crowdin's UI
6. Crowdin opens a PR with translated files → review → merge

**Key settings:**

- Enable "Auto-approve" for machine translations to speed up new keys
- Enable "Screenshots" so translators see context
- Set "Export only approved" to prevent unreviewed strings shipping

### Phrase (formerly Phrase Strings)

Good for developer-friendly workflows with a CLI tool.

```bash
npm install --save-dev phrase-cli
phrase pull          # Download latest translations
phrase push          # Upload source locale
```

### Lokalise

Supports key extraction from code, in-context editing, and Figma integration. Good for design-to-dev translation handoff.

### Self-hosted with LibreTranslate

For projects that cannot use SaaS translation services:

```bash
docker run -p 5000:5000 libretranslate/libretranslate
```

Use the REST API to bootstrap translations, then human-review all output.

---

## QA Process

### Pre-release Checklist

- [ ] Run `npm run i18n:extract` — no new missing keys
- [ ] Check all target locale files have no placeholder English values
- [ ] Test the app with each supported locale active
- [ ] Check for text overflow (translated text is often longer than English)
- [ ] Check RTL layout if Arabic/Hebrew/Persian is supported
- [ ] Verify date/number/currency formatting looks correct per locale
- [ ] Check `<html lang>` attribute matches active locale

### Automated Checks

Add a CI step to verify translation files are complete:

```bash
# scripts/check-translations.sh
#!/usr/bin/env bash
set -e

SOURCE_DIR="public/locales/en"
LOCALES=("es")

for locale in "${LOCALES[@]}"; do
  for file in "$SOURCE_DIR"/*.json; do
    ns=$(basename "$file")
    target="public/locales/$locale/$ns"

    if [ ! -f "$target" ]; then
      echo "MISSING: $target"
      exit 1
    fi

    # Count keys in source vs target
    source_keys=$(python3 -c "import json,sys; d=json.load(open('$file')); print(len(d))")
    target_keys=$(python3 -c "import json,sys; d=json.load(open('$target')); print(len(d))")

    if [ "$source_keys" != "$target_keys" ]; then
      echo "KEY COUNT MISMATCH: $target (expected $source_keys, got $target_keys)"
      exit 1
    fi
  done
done

echo "All translations OK"
```

### Visual QA: Pseudo-localization

Replace characters with visually similar extended characters to catch hardcoded strings and layout issues without needing real translations:

```ts
// scripts/pseudo-localize.ts
// Replaces English strings with visually decorated versions
// e.g., "Hello World" → "[Héllö Wörld!!!]"
const CHAR_MAP: Record<string, string> = {
  a: "à",
  e: "é",
  i: "í",
  o: "ö",
  u: "ü",
  A: "À",
  E: "É",
  I: "Í",
  O: "Ö",
  U: "Ü",
};

export const pseudoLocalize = (str: string): string => {
  const replaced = str
    .split("")
    .map((c) => CHAR_MAP[c] ?? c)
    .join("");
  return `[${replaced}!!!]`;
};
```

Run pseudo-localization on English strings to:

1. Find hardcoded UI strings (they won't be decorated)
2. Find layout issues (the `!!!` suffix adds ~30% string length)

---

## Team Conventions

### Git Workflow

- Translation files are committed directly to the main branch (no separate translation branch)
- Machine-translated drafts are committed with a `[machine-translation]` prefix in the commit message for easy revert
- All human-reviewed translations require a second pair of eyes before merging

### Translator Onboarding

1. Share a copy of the English source files as reference
2. Provide the app URL with a staging environment for context
3. Share the style guide: tone, formality level, terminology glossary
4. Set up TMS access with only the target locale they are responsible for

### Glossary

Maintain a `GLOSSARY.md` in the translations directory for domain-specific terms:

```markdown
| English   | Spanish | Notes                          |
| --------- | ------- | ------------------------------ |
| Dashboard | Panel   | Do not translate as "Tablero"  |
| Workflow  | Flujo   | Consistent across the product  |
| Submit    | Enviar  | Use for forms, not "Confirmar" |
```
