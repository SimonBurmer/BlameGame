import { Cta } from '@/components/site/cta';
import { Faq } from '@/components/site/faq';
import { Features } from '@/components/site/features';
import { Footer } from '@/components/site/footer';
import { Hero } from '@/components/site/hero';
import { Privacy } from '@/components/site/privacy';
import { SiteNav } from '@/components/site/site-nav';
import { Stats } from '@/components/site/stats';
import { Steps } from '@/components/site/steps';
import { locales, messages, type Locale } from '@/i18n';
import { jsonLd, schemasFor } from '@/lib/seo';

export function generateStaticParams(): { lang: string[] }[] {
  return locales.map((l) => ({ lang: l === 'en' ? [] : [l] }));
}

function localeOf(segments: string[] | undefined): Locale {
  const first = segments?.[0];
  return locales.includes(first as Locale) ? (first as Locale) : 'en';
}

export default async function Page({ params }: { params: Promise<{ lang?: string[] }> }) {
  const locale = localeOf((await params).lang);
  const m = messages[locale];

  return (
    <>
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:rounded-md focus:bg-brand focus:px-4 focus:py-2 focus:text-sm focus:font-semibold"
      >
        {m.nav.skipToContent}
      </a>

      <SiteNav locale={locale} m={m} />

      <main id="main">
        <Hero m={m} />
        <Stats m={m} />
        <Steps m={m} />
        <Features m={m} />
        <Privacy m={m} />
        <Faq m={m} />
        <Cta m={m} />
      </main>

      <Footer locale={locale} m={m} />

      {schemasFor(locale).map((schema, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: jsonLd(schema) }}
        />
      ))}
    </>
  );
}
