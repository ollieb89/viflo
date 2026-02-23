---
name: i18n-implementation
description: Internationalization (i18n) and localization (l10n) patterns for web applications. Covers next-i18next setup, translation file structure, language switching, RTL support, date/number formatting, pluralization, and translation workflow. Use when adding multi-language support to Next.js apps or managing translations.
---

# i18n Implementation

## Purpose

Practical guide for adding internationalization to web applications, with a focus on Next.js using next-i18next. Covers setup, translation management, language switching, and advanced formatting patterns.

## When to Use This Skill

- Adding multi-language support to a Next.js application
- Setting up translation file structure and naming conventions
- Implementing a language switcher UI component
- Supporting right-to-left (RTL) languages
- Formatting dates, numbers, and currencies per locale
- Managing translations with a team or translation service

---

## Quick Start

### New i18n Project Checklist

- [ ] Install `next-i18next` and `react-i18next`
- [ ] Create `next-i18next.config.js` at project root
- [ ] Update `next.config.js` to load i18n config
- [ ] Create `public/locales/{locale}/{namespace}.json` files
- [ ] Wrap `_app.tsx` with `appWithTranslation`
- [ ] Use `serverSideTranslations` in `getStaticProps` / `getServerSideProps`
- [ ] Import `useTranslation` hook in components
- [ ] Add language switcher to layout

### Minimal Setup

```bash
npm install next-i18next react-i18next i18next
```

```js
// next-i18next.config.js
module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es'],
  },
};
```

```js
// next.config.js
const { i18n } = require('./next-i18next.config');
module.exports = { i18n };
```

---

## Translation File Structure

```
public/
  locales/
    en/
      common.json       # Shared across pages (nav, buttons, errors)
      home.json         # Home page strings
      auth.json         # Login, register
    es/
      common.json
      home.json
      auth.json
```

### Namespace Strategy

| Namespace  | Contents                          |
| ---------- | --------------------------------- |
| `common`   | Navigation, buttons, global errors|
| `home`     | Landing page, hero section        |
| `auth`     | Login, register, forgot password  |
| `dashboard`| Dashboard-specific strings        |
| `errors`   | Error page messages               |

### Translation Key Naming

Use dot notation for grouping; keep flat within namespace files.

```json
// en/common.json
{
  "nav": {
    "home": "Home",
    "about": "About",
    "contact": "Contact"
  },
  "button": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete"
  },
  "error": {
    "required": "This field is required",
    "notFound": "Page not found"
  }
}
```

**Naming rules:**
- Use camelCase for keys: `firstName`, not `first_name`
- Group by UI area, not by component: `nav.home`, not `Navbar.homeLink`
- Keep key names semantic: `button.save`, not `button.green`

---

## Using Translations in Components

### Basic Usage

```tsx
import { useTranslation } from 'next-i18next';

export const Navbar: React.FC = () => {
  const { t } = useTranslation('common');

  return (
    <nav>
      <a href="/">{t('nav.home')}</a>
      <a href="/about">{t('nav.about')}</a>
    </nav>
  );
};
```

### Multiple Namespaces

```tsx
const { t: tCommon } = useTranslation('common');
const { t: tDashboard } = useTranslation('dashboard');
```

### Server-Side Translation Loading

```tsx
// pages/index.tsx
import { GetStaticProps } from 'next';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';

export const getStaticProps: GetStaticProps = async ({ locale }) => ({
  props: {
    ...(await serverSideTranslations(locale ?? 'en', ['common', 'home'])),
  },
});
```

---

## Language Switcher Component

```tsx
// components/LanguageSwitcher.tsx
import { useRouter } from 'next/router';

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'es', label: 'Español' },
];

export const LanguageSwitcher: React.FC = () => {
  const router = useRouter();
  const { pathname, asPath, query, locale } = router;

  const switchLanguage = (lang: string) => {
    router.push({ pathname, query }, asPath, { locale: lang });
  };

  return (
    <select
      value={locale}
      onChange={(e) => switchLanguage(e.target.value)}
      aria-label="Select language"
    >
      {LANGUAGES.map(({ code, label }) => (
        <option key={code} value={code}>
          {label}
        </option>
      ))}
    </select>
  );
};
```

---

## RTL Support

Right-to-left languages (Arabic, Hebrew, Persian) require document direction changes.

### Detecting RTL

```tsx
// lib/rtl.ts
const RTL_LOCALES = ['ar', 'he', 'fa', 'ur'];

export const isRTL = (locale: string): boolean =>
  RTL_LOCALES.includes(locale);
```

### Applying Direction in _app.tsx

```tsx
import { isRTL } from '../lib/rtl';

function MyApp({ Component, pageProps, router }: AppProps) {
  const dir = isRTL(router.locale ?? 'en') ? 'rtl' : 'ltr';

  return (
    <div dir={dir} lang={router.locale}>
      <Component {...pageProps} />
    </div>
  );
}
```

### CSS Logical Properties (RTL-safe)

Use logical properties instead of `left`/`right` for automatic RTL support:

```css
/* Instead of: margin-left, padding-right */
margin-inline-start: 1rem;   /* left in LTR, right in RTL */
padding-inline-end: 0.5rem;  /* right in LTR, left in RTL */
```

---

## Date, Number, and Currency Formatting

Use the browser's built-in `Intl` API for locale-aware formatting.

### Dates

```tsx
const formatDate = (date: Date, locale: string): string =>
  new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);

// Usage
formatDate(new Date(), 'en');  // "February 23, 2026"
formatDate(new Date(), 'es');  // "23 de febrero de 2026"
```

### Numbers

```tsx
const formatNumber = (value: number, locale: string): string =>
  new Intl.NumberFormat(locale).format(value);

formatNumber(1234567.89, 'en');  // "1,234,567.89"
formatNumber(1234567.89, 'es');  // "1.234.567,89"
```

### Currency

```tsx
const formatCurrency = (amount: number, locale: string, currency = 'USD'): string =>
  new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount);

formatCurrency(9.99, 'en', 'USD');  // "$9.99"
formatCurrency(9.99, 'es', 'EUR');  // "9,99 €"
```

---

## Middleware for Locale Routing

Next.js middleware can detect and redirect to the correct locale.

```ts
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';

const SUPPORTED_LOCALES = ['en', 'es'];
const DEFAULT_LOCALE = 'en';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip if already has locale prefix
  const hasLocale = SUPPORTED_LOCALES.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );
  if (hasLocale) return NextResponse.next();

  // Detect from Accept-Language header
  const acceptLang = request.headers.get('Accept-Language') ?? '';
  const preferred = acceptLang.split(',')[0]?.split('-')[0] ?? DEFAULT_LOCALE;
  const locale = SUPPORTED_LOCALES.includes(preferred) ? preferred : DEFAULT_LOCALE;

  request.nextUrl.pathname = `/${locale}${pathname}`;
  return NextResponse.redirect(request.nextUrl);
}

export const config = {
  matcher: ['/((?!_next|api|favicon.ico).*)'],
};
```

---

## Topic Guides

### Advanced Translation Patterns

- Pluralization rules
- Interpolation with variables
- Context-based translations
- Lazy loading namespaces

_(See inline content above for patterns)_

### Translation Workflow

- Managing translation files across locales
- Key extraction tools
- Translation services (Crowdin, Phrase)
- QA and testing

**[Complete Guide: references/translation-workflow.md](references/translation-workflow.md)**

### Working Example

- Full Next.js app with EN and ES translations
- Language switcher
- Middleware routing

**[Example: assets/examples/nextjs-i18n/](assets/examples/nextjs-i18n/)**

---

## Navigation Guide

| Need to...                        | Read this                                                             |
| --------------------------------- | --------------------------------------------------------------------- |
| Set up next-i18next               | Quick Start section above                                             |
| Structure translation files       | Translation File Structure section above                              |
| Add a language switcher           | Language Switcher Component section above                             |
| Support Arabic/Hebrew/RTL         | RTL Support section above                                             |
| Format dates or currencies        | Date, Number, and Currency Formatting above                           |
| Pluralization and interpolation   | Advanced Translation Patterns section above                           |
| Manage translations with a team   | [translation-workflow.md](references/translation-workflow.md)         |
| See a working Next.js example     | [assets/examples/nextjs-i18n/](assets/examples/nextjs-i18n/)         |

---

## Core Principles

1. **Namespaces by domain**: Split translations into focused namespaces to control load size
2. **Keys are semantic**: Name keys by meaning, not by position or style
3. **Never hardcode text**: Every user-visible string lives in a translation file
4. **Intl API for formatting**: Use browser-native `Intl` for dates, numbers, and currency
5. **Logical CSS properties**: Use `margin-inline-start` over `margin-left` for RTL safety
6. **Load only what you need**: Pass only required namespaces to `serverSideTranslations`

---

## Related Skills

- **frontend-dev-guidelines**: React/Next.js component patterns that consume translations
- **app-builder**: Full-stack app scaffolding that can integrate i18n from the start
