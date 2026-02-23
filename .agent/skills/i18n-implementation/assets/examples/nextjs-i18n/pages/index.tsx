import type { GetStaticProps, NextPage } from 'next';
import { useTranslation } from 'next-i18next';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import { LocaleDemo } from '../components/LocaleDemo';

const HomePage: NextPage = () => {
  const { t } = useTranslation('home');

  return (
    <div>
      {/* Hero */}
      <section style={{ textAlign: 'center', padding: '4rem 0 2rem' }}>
        <h1 style={{ fontSize: '2.5rem', margin: '0 0 1rem' }}>{t('hero.title')}</h1>
        <p style={{ fontSize: '1.25rem', color: '#555', margin: '0 0 2rem' }}>
          {t('hero.subtitle')}
        </p>
        <button
          style={{
            padding: '0.75rem 2rem',
            fontSize: '1rem',
            backgroundColor: '#0070f3',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          {t('hero.cta')}
        </button>
      </section>

      {/* Features */}
      <section style={{ padding: '2rem 0' }}>
        <h2>{t('features.title')}</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
          {(['i18n', 'rtl', 'formatting'] as const).map((key) => (
            <div
              key={key}
              style={{
                padding: '1.5rem',
                border: '1px solid #eee',
                borderRadius: '8px',
              }}
            >
              <h3 style={{ margin: '0 0 0.5rem' }}>{t(`features.${key}.title`)}</h3>
              <p style={{ margin: 0, color: '#666' }}>{t(`features.${key}.description`)}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Locale formatting demo */}
      <LocaleDemo />
    </div>
  );
};

export const getStaticProps: GetStaticProps = async ({ locale }) => ({
  props: {
    ...(await serverSideTranslations(locale ?? 'en', ['common', 'home'])),
  },
});

export default HomePage;
