import type { AppProps } from 'next/app';
import { appWithTranslation } from 'next-i18next';
import { useRouter } from 'next/router';
import { Navbar } from '../components/Navbar';

// RTL locale codes
const RTL_LOCALES = ['ar', 'he', 'fa', 'ur'];

function MyApp({ Component, pageProps }: AppProps) {
  const { locale } = useRouter();
  const dir = RTL_LOCALES.includes(locale ?? '') ? 'rtl' : 'ltr';

  return (
    <div dir={dir} lang={locale} style={{ minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      <Navbar />
      <main style={{ maxWidth: '960px', margin: '0 auto', padding: '2rem' }}>
        <Component {...pageProps} />
      </main>
    </div>
  );
}

// Wraps the app with i18next context provider
export default appWithTranslation(MyApp);
