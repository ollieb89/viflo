import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';

const LANGUAGES = [
  { code: 'en', flag: '🇬🇧' },
  { code: 'es', flag: '🇪🇸' },
];

/**
 * Language switcher dropdown.
 * Uses Next.js router to navigate to the same page in the selected locale.
 */
export const LanguageSwitcher: React.FC = () => {
  const router = useRouter();
  const { t } = useTranslation('common');
  const { pathname, asPath, query, locale } = router;

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLocale = e.target.value;
    router.push({ pathname, query }, asPath, { locale: newLocale });
  };

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
      <label htmlFor="lang-select" style={{ fontSize: '0.875rem' }}>
        {t('language.select')}:
      </label>
      <select
        id="lang-select"
        value={locale}
        onChange={handleChange}
        style={{
          padding: '0.25rem 0.5rem',
          borderRadius: '4px',
          border: '1px solid #ccc',
          fontSize: '0.875rem',
          cursor: 'pointer',
        }}
        aria-label={t('language.select')}
      >
        {LANGUAGES.map(({ code, flag }) => (
          <option key={code} value={code}>
            {flag} {t(`language.${code}`)}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSwitcher;
