# i18n Patterns Reference

Common internationalization patterns covering pluralization, interpolation, context-based translations, dynamic keys, and lazy loading.

---

## Interpolation (Variables in Strings)

### Basic Interpolation

Pass dynamic values into translation strings using double-brace syntax.

```json
// en/common.json
{
  "welcome": "Welcome, {{name}}!",
  "itemCount": "You have {{count}} items in your cart"
}
```

```tsx
const { t } = useTranslation('common');

t('welcome', { name: 'Alice' });        // "Welcome, Alice!"
t('itemCount', { count: 3 });           // "You have 3 items in your cart"
```

### HTML in Translations

Use `<Trans>` component when the translation contains HTML markup or React components.

```json
// en/home.json
{
  "termsNotice": "By signing up, you agree to our <terms>Terms</terms> and <privacy>Privacy Policy</privacy>."
}
```

```tsx
import { Trans, useTranslation } from 'next-i18next';

const { t } = useTranslation('home');

<Trans
  i18nKey="termsNotice"
  components={{
    terms: <a href="/terms" />,
    privacy: <a href="/privacy" />,
  }}
/>
```

This renders: "By signing up, you agree to our **Terms** and **Privacy Policy**." with real anchor links, while keeping all text in the translation file.

### Rich Text with Formatting

```json
{
  "highlight": "The total is <bold>{{amount}}</bold>"
}
```

```tsx
<Trans
  i18nKey="highlight"
  values={{ amount: '$49.99' }}
  components={{ bold: <strong /> }}
/>
```

---

## Pluralization

i18next follows CLDR plural rules for each language.

### English (two forms: `one` and `other`)

```json
// en/common.json
{
  "item": "{{count}} item",
  "item_one": "{{count}} item",
  "item_other": "{{count}} items"
}
```

```tsx
t('item', { count: 1 });   // "1 item"
t('item', { count: 5 });   // "5 items"
```

### Spanish (same two-form structure)

```json
// es/common.json
{
  "item_one": "{{count}} artículo",
  "item_other": "{{count}} artículos"
}
```

### Languages with More Plural Forms

Arabic has 6 plural forms. Russian has 3. i18next handles this automatically via CLDR rules — you only need to provide the correct keys:

```json
// ar/common.json
{
  "item_zero": "لا توجد عناصر",
  "item_one": "عنصر واحد",
  "item_two": "عنصران",
  "item_few": "{{count}} عناصر",
  "item_many": "{{count}} عنصرًا",
  "item_other": "{{count}} عنصر"
}
```

### Zero State Handling

```json
// en/common.json
{
  "result_zero": "No results found",
  "result_one": "{{count}} result",
  "result_other": "{{count}} results"
}
```

```tsx
t('result', { count: 0 });  // "No results found"
t('result', { count: 1 });  // "1 result"
t('result', { count: 42 }); // "42 results"
```

---

## Context-Based Translations

Use the `context` option when the same key needs different translations depending on a non-count variable (e.g., gender, role, state).

### Gender Context

```json
// en/common.json
{
  "invitedBy": "You were invited by {{name}}",
  "invitedBy_male": "He invited you",
  "invitedBy_female": "She invited you"
}
```

```tsx
t('invitedBy', { context: 'female', name: 'Alice' });
// "She invited you"

t('invitedBy', { context: 'male', name: 'Bob' });
// "He invited you"

t('invitedBy', { name: 'Alex' });
// "You were invited by Alex" (no context → fallback)
```

### Combining Context and Pluralization

```json
{
  "follower_male_one": "{{count}} male follower",
  "follower_male_other": "{{count}} male followers",
  "follower_female_one": "{{count}} female follower",
  "follower_female_other": "{{count}} female followers"
}
```

```tsx
t('follower', { context: 'female', count: 3 });
// "3 female followers"
```

---

## Dynamic Translation Keys

### When to Use Dynamic Keys

Use when you have a fixed set of values that map to translated labels, such as status codes, category names, or enum values.

```json
// en/common.json
{
  "status": {
    "pending": "Pending",
    "active": "Active",
    "suspended": "Suspended",
    "closed": "Closed"
  }
}
```

```tsx
type Status = 'pending' | 'active' | 'suspended' | 'closed';

const StatusBadge: React.FC<{ status: Status }> = ({ status }) => {
  const { t } = useTranslation('common');
  return <span>{t(`status.${status}`)}</span>;
};
```

### Type-Safe Dynamic Keys

Create a helper to get type safety on dynamic key segments:

```tsx
const STATUS_KEYS = ['pending', 'active', 'suspended', 'closed'] as const;
type StatusKey = typeof STATUS_KEYS[number];

const isValidStatusKey = (key: string): key is StatusKey =>
  STATUS_KEYS.includes(key as StatusKey);

const getStatusLabel = (t: TFunction, status: string): string => {
  if (isValidStatusKey(status)) return t(`status.${status}`);
  return status; // fallback to raw value
};
```

### Namespace-Based Feature Flags

```tsx
// Conditionally load a namespace based on feature availability
const namespaces = ['common', ...(featureEnabled ? ['premium'] : [])];

export const getStaticProps: GetStaticProps = async ({ locale }) => ({
  props: await serverSideTranslations(locale ?? 'en', namespaces),
});
```

---

## Lazy Loading Translation Namespaces

By default, `serverSideTranslations` loads specified namespaces at render time. For large apps, lazy-load namespaces client-side to reduce initial bundle size.

### Client-Side Lazy Load

```tsx
import i18next from 'i18next';

const loadNamespace = async (ns: string) => {
  if (!i18next.hasLoadedNamespace(ns)) {
    await i18next.loadNamespaces(ns);
  }
};

// In a component or route handler
await loadNamespace('reports');
const { t } = useTranslation('reports');
```

### Lazy Load on Demand (with React.lazy)

```tsx
// Combine code splitting with translation lazy loading
const ReportsPage = React.lazy(async () => {
  await loadNamespace('reports');
  return import('./ReportsPage');
});
```

### Preload Namespaces for Routes

```tsx
// In TanStack Router loader or Next.js loader
export const loader = async ({ locale }: { locale: string }) => {
  await i18next.loadNamespaces(['reports', 'exports']);
  return null;
};
```

---

## Date, Relative Time, and List Formatting

### Relative Time

```tsx
const formatRelativeTime = (date: Date, locale: string): string => {
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
  const diffMs = date.getTime() - Date.now();
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

  if (Math.abs(diffDays) < 1) {
    const diffHours = Math.round(diffMs / (1000 * 60 * 60));
    return rtf.format(diffHours, 'hour');
  }
  return rtf.format(diffDays, 'day');
};

formatRelativeTime(new Date(Date.now() - 3600000), 'en');  // "1 hour ago"
formatRelativeTime(new Date(Date.now() - 3600000), 'es');  // "hace 1 hora"
```

### List Formatting

```tsx
const formatList = (items: string[], locale: string): string =>
  new Intl.ListFormat(locale, { style: 'long', type: 'conjunction' }).format(items);

formatList(['apples', 'bananas', 'oranges'], 'en');
// "apples, bananas, and oranges"

formatList(['manzanas', 'plátanos', 'naranjas'], 'es');
// "manzanas, plátanos y naranjas"
```

---

## Fallback Chains

Configure i18next to fall back to a parent locale or default locale when a key is missing.

```js
// next-i18next.config.js
module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'en-GB', 'es', 'es-MX'],
  },
  fallbackLng: {
    'en-GB': ['en'],      // British English falls back to US English
    'es-MX': ['es'],      // Mexican Spanish falls back to Castilian Spanish
    default: ['en'],
  },
};
```

With this config:
- A missing `en-GB` key shows the `en` value
- A missing `es-MX` key shows the `es` value
- Any other missing key shows the `en` value

---

## Number Formatting Patterns

### Compact Numbers

```tsx
const formatCompact = (value: number, locale: string): string =>
  new Intl.NumberFormat(locale, {
    notation: 'compact',
    compactDisplay: 'short',
  }).format(value);

formatCompact(1200000, 'en');  // "1.2M"
formatCompact(1200000, 'es');  // "1,2 M"
```

### Percentages

```tsx
const formatPercent = (value: number, locale: string): string =>
  new Intl.NumberFormat(locale, {
    style: 'percent',
    maximumFractionDigits: 1,
  }).format(value);

formatPercent(0.756, 'en');  // "75.6%"
formatPercent(0.756, 'es');  // "75,6 %"
```

### Unit Formatting

```tsx
const formatBytes = (bytes: number, locale: string): string =>
  new Intl.NumberFormat(locale, {
    style: 'unit',
    unit: 'megabyte',
    maximumFractionDigits: 1,
  }).format(bytes / 1_000_000);

formatBytes(5242880, 'en');  // "5 MB"
formatBytes(5242880, 'es');  // "5 MB"
```

---

## Testing Translations

### Unit Test: Translation Keys Exist

```ts
// __tests__/translations.test.ts
import en from '../public/locales/en/common.json';
import es from '../public/locales/es/common.json';

const flattenKeys = (obj: object, prefix = ''): string[] =>
  Object.entries(obj).flatMap(([k, v]) =>
    typeof v === 'object'
      ? flattenKeys(v as object, `${prefix}${k}.`)
      : [`${prefix}${k}`]
  );

test('ES common.json has all keys from EN common.json', () => {
  const enKeys = flattenKeys(en).sort();
  const esKeys = flattenKeys(es).sort();
  expect(esKeys).toEqual(enKeys);
});
```

### Integration Test: Language Switching

```ts
// Using Playwright
test('language switcher changes page text', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Welcome');

  await page.selectOption('[aria-label="Select language"]', 'es');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Bienvenido');
});
```
