import Link from 'next/link';
import { useTranslation } from 'next-i18next';
import { LanguageSwitcher } from './LanguageSwitcher';

const navStyles = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 2rem',
    borderBottom: '1px solid #eee',
    backgroundColor: '#fff',
  } as React.CSSProperties,
  links: {
    display: 'flex',
    gap: '1.5rem',
    listStyle: 'none',
    margin: 0,
    padding: 0,
  } as React.CSSProperties,
  link: {
    textDecoration: 'none',
    color: '#333',
    fontWeight: 500,
  } as React.CSSProperties,
};

/**
 * Site navigation bar with translated links and language switcher.
 */
export const Navbar: React.FC = () => {
  const { t } = useTranslation('common');

  return (
    <nav style={navStyles.nav}>
      <Link href="/" style={{ fontWeight: 700, fontSize: '1.25rem', textDecoration: 'none', color: '#000' }}>
        i18n Demo
      </Link>
      <ul style={navStyles.links}>
        <li><Link href="/" style={navStyles.link}>{t('nav.home')}</Link></li>
        <li><Link href="/about" style={navStyles.link}>{t('nav.about')}</Link></li>
        <li><Link href="/contact" style={navStyles.link}>{t('nav.contact')}</Link></li>
      </ul>
      <LanguageSwitcher />
    </nav>
  );
};

export default Navbar;
