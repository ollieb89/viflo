# Next.js i18n Example

A minimal Next.js application demonstrating internationalization with `next-i18next`.

## Features

- English and Spanish translations
- Language switcher component in the navbar
- Locale-aware date, number, and currency formatting
- RTL detection in `_app.tsx`
- Accept-Language header middleware for automatic locale routing

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The app defaults to English.

Switch to Spanish by selecting "Espanol" in the language dropdown, or navigate directly to [http://localhost:3000/es](http://localhost:3000/es).

## Structure

```
.
|-- components/
|   |-- LanguageSwitcher.tsx   # Language dropdown
|   |-- LocaleDemo.tsx         # Intl API demo (dates, numbers, currency)
|   `-- Navbar.tsx             # Nav bar with switcher
|-- pages/
|   |-- _app.tsx               # App wrapper with RTL and appWithTranslation
|   `-- index.tsx              # Home page
|-- public/
|   `-- locales/
|       |-- en/
|       |   |-- common.json    # Shared strings in English
|       |   `-- home.json      # Home page strings in English
|       `-- es/
|           |-- common.json    # Shared strings in Spanish
|           `-- home.json      # Home page strings in Spanish
|-- middleware.ts              # Auto-redirect based on Accept-Language
|-- next-i18next.config.js     # i18n config (locales, defaultLocale)
`-- next.config.js             # Next.js config (loads i18n)
```

## Adding a New Language

1. Add the locale code to `next-i18next.config.js` → `locales` array
2. Create `public/locales/{code}/common.json` and `home.json`
3. Add `{ code, flag }` entry in `components/LanguageSwitcher.tsx`
4. If the language is RTL, add its code to `RTL_LOCALES` in `pages/_app.tsx`

## Adding a New Namespace

1. Create `public/locales/en/{namespace}.json`
2. Mirror the file for every other locale
3. Add the namespace to `serverSideTranslations` calls in the relevant page
4. Use `useTranslation('{namespace}')` in components

## Key Concepts

- **`appWithTranslation`** in `_app.tsx` provides the i18next context to every page
- **`serverSideTranslations`** in `getStaticProps`/`getServerSideProps` loads only the namespaces needed for that page
- **`useTranslation`** hook gives components access to the `t()` translation function
- **`Intl` API** is used directly (no extra library) for locale-aware formatting
