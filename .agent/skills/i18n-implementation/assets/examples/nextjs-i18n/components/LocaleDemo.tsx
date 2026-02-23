import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';

/**
 * Demonstrates locale-aware formatting using the Intl API.
 * Shows how dates, numbers, and currencies change per locale.
 */
export const LocaleDemo: React.FC = () => {
  const { t } = useTranslation('home');
  const { locale } = useRouter();
  const activeLocale = locale ?? 'en';

  const demoDate = new Date('2026-02-23T12:00:00Z');
  const demoNumber = 1234567.89;
  const demoPrice = 49.99;

  const formatDate = (date: Date) =>
    new Intl.DateTimeFormat(activeLocale, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(date);

  const formatNumber = (value: number) =>
    new Intl.NumberFormat(activeLocale).format(value);

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat(activeLocale, {
      style: 'currency',
      currency: 'USD',
    }).format(amount);

  const rows = [
    { label: t('demo.date'), value: formatDate(demoDate) },
    { label: t('demo.number'), value: formatNumber(demoNumber) },
    { label: t('demo.currency'), value: formatCurrency(demoPrice) },
  ];

  return (
    <section style={{ padding: '2rem', backgroundColor: '#f9f9f9', borderRadius: '8px' }}>
      <h2 style={{ marginTop: 0 }}>{t('demo.title')}</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <tbody>
          {rows.map(({ label, value }) => (
            <tr key={label} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '0.75rem 0', fontWeight: 500, color: '#666', width: '40%' }}>
                {label}
              </td>
              <td style={{ padding: '0.75rem 0', fontFamily: 'monospace' }}>
                {value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p style={{ marginBottom: 0, fontSize: '0.875rem', color: '#888' }}>
        Active locale: <code>{activeLocale}</code>
      </p>
    </section>
  );
};

export default LocaleDemo;
