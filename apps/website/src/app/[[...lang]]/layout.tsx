import type { Metadata, Viewport } from 'next';
import { Archivo_Black, Inter, JetBrains_Mono } from 'next/font/google';

import { palette } from '@blame-game/brand';

import { locales, type Locale } from '@/i18n';
import { metadataFor } from '@/lib/seo';

import '../globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' });

/**
 * The app's wordmark is a very heavy, very tight sans. Archivo Black is the
 * closest thing on Google Fonts, and it keeps the page and the launcher icon
 * looking like one product rather than two.
 */
const display = Archivo_Black({
  subsets: ['latin'],
  weight: '400',
  variable: '--font-display',
  display: 'swap',
});

/** Room codes are monospaced in the app; they are monospaced here too. */
const mono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono-code',
  display: 'swap',
});

/** `/` is English, `/de/` is German — see `pathFor`. */
export function generateStaticParams(): { lang: string[] }[] {
  return locales.map((l) => ({ lang: l === 'en' ? [] : [l] }));
}

function localeOf(segments: string[] | undefined): Locale {
  const first = segments?.[0];
  return locales.includes(first as Locale) ? (first as Locale) : 'en';
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ lang?: string[] }>;
}): Promise<Metadata> {
  return metadataFor(localeOf((await params).lang));
}

export const viewport: Viewport = {
  themeColor: palette.bgTop,
  colorScheme: 'dark',
};

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ lang?: string[] }>;
}) {
  const locale = localeOf((await params).lang);
  return (
    <html lang={locale} className={`dark ${inter.variable} ${display.variable} ${mono.variable}`}>
      <head>
        {/* Several of the animated components ship their first frame as
            inline `opacity: 0` and fade it in from JavaScript. With scripting
            off that frame is the last one, and the copy never appears — so
            with scripting off, it is simply shown. */}
        <noscript>
          <style>{'[style*="opacity:0"],[style*="opacity: 0"]{opacity:1!important;filter:none!important}'}</style>
        </noscript>
      </head>
      <body className="grain bg-ink text-white antialiased">{children}</body>
    </html>
  );
}
