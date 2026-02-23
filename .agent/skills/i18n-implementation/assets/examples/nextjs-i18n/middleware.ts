import { NextRequest, NextResponse } from 'next/server';

const SUPPORTED_LOCALES = ['en', 'es'];
const DEFAULT_LOCALE = 'en';

/**
 * Locale detection middleware.
 *
 * Reads the Accept-Language header and redirects to the appropriate
 * locale-prefixed path if one is not already present.
 *
 * Examples:
 *   /         → /en  (or /es based on browser language)
 *   /about    → /en/about
 *   /en/about → unchanged (already has locale)
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip if the path already contains a supported locale prefix
  const hasLocale = SUPPORTED_LOCALES.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );
  if (hasLocale) return NextResponse.next();

  // Parse browser's preferred language from Accept-Language header
  const acceptLanguage = request.headers.get('Accept-Language') ?? '';
  const preferredLang = acceptLanguage.split(',')[0]?.split('-')[0]?.toLowerCase() ?? '';

  // Map to supported locale or fall back to default
  const locale = SUPPORTED_LOCALES.includes(preferredLang) ? preferredLang : DEFAULT_LOCALE;

  // Redirect to locale-prefixed path
  request.nextUrl.pathname = `/${locale}${pathname}`;
  return NextResponse.redirect(request.nextUrl);
}

export const config = {
  // Match all routes except Next.js internals, API routes, and static files
  matcher: ['/((?!_next|api|favicon.ico|.*\\..*).*)'],
};
