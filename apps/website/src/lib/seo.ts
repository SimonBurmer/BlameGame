import type { Metadata } from 'next';

import { app, siteOrigin } from '@blame-game/brand';

import { locales, pathFor, type Locale } from '@/i18n';
import { messages } from '@/i18n';

const OG_IMAGE = '/og-image.png';

export function absoluteUrl(path: string): string {
  return new URL(path, siteOrigin).href;
}

/**
 * `alternates.languages` is derived from `locales`, so adding a language adds
 * its hreflang, its canonical and its sitemap entry with no further edits.
 * `x-default` points at English, which is what a crawler with no better idea
 * should be shown.
 */
function languageAlternates(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const l of locales) out[l] = pathFor(l);
  out['x-default'] = pathFor('en');
  return out;
}

export function metadataFor(locale: Locale): Metadata {
  const m = messages[locale];
  return {
    metadataBase: new URL(siteOrigin),
    title: m.meta.title,
    description: m.meta.description,
    keywords: [...m.meta.keywords],
    applicationName: app.name,
    alternates: {
      canonical: pathFor(locale),
      languages: languageAlternates(),
    },
    openGraph: {
      type: 'website',
      siteName: app.name,
      title: m.meta.title,
      description: m.meta.description,
      url: absoluteUrl(pathFor(locale)),
      locale: m.ogLocale,
      alternateLocale: locales.filter((l) => l !== locale).map((l) => messages[l].ogLocale),
      images: [{ url: OG_IMAGE, width: 1200, height: 630, alt: m.meta.ogImageAlt }],
    },
    twitter: {
      card: 'summary_large_image',
      title: m.meta.title,
      description: m.meta.description,
      images: [{ url: OG_IMAGE, alt: m.meta.ogImageAlt }],
    },
    icons: {
      icon: [{ url: '/favicon.png', type: 'image/png' }],
      apple: [{ url: '/apple-touch-icon.png', sizes: '180x180' }],
    },
  };
}

/**
 * Structured data. Deliberately no `aggregateRating` and no `offers`: the app
 * has no ratings and no price yet, and inventing either is how a site earns a
 * manual action rather than a rich result.
 */
export function schemasFor(locale: Locale): unknown[] {
  const m = messages[locale];
  return [
    {
      '@context': 'https://schema.org',
      '@type': 'SoftwareApplication',
      name: app.name,
      description: m.meta.description,
      applicationCategory: 'GameApplication',
      operatingSystem: 'iOS',
      inLanguage: m.htmlLang,
      url: absoluteUrl(pathFor(locale)),
      image: absoluteUrl(OG_IMAGE),
    },
    {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      inLanguage: m.htmlLang,
      mainEntity: m.faq.items.map((item) => ({
        '@type': 'Question',
        name: item.question,
        acceptedAnswer: { '@type': 'Answer', text: item.answer },
      })),
    },
  ];
}

/**
 * JSON.stringify can emit `</script>`, which would close the tag the payload is
 * sitting inside. Escaping `<` keeps it valid JSON and inert as markup.
 */
export function jsonLd(value: unknown): string {
  return JSON.stringify(value).replace(/</g, '\\u003c');
}
