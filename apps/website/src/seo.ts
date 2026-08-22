import { app, palette, siteOrigin } from '@blame-game/brand';
import { locales, pathFor, type Locale, type Messages } from './i18n';

const OG_IMAGE = '/og-image.png';
const OG_IMAGE_WIDTH = 1200;
const OG_IMAGE_HEIGHT = 630;

export function absoluteUrl(path: string): string {
  return new URL(path, siteOrigin).href;
}

/**
 * JSON.stringify can emit `</script>`, which would close the tag it is sitting
 * inside. Escaping `<` keeps the payload valid JSON and inert as markup.
 */
export function jsonLd(value: unknown): string {
  return JSON.stringify(value).replace(/</g, '\\u003c');
}

/**
 * Structured data. Deliberately no `aggregateRating` and no `offers`: the app
 * has no ratings and no price yet, and inventing either is how a site earns a
 * manual action rather than a rich result.
 */
export function softwareApplicationSchema(locale: Locale, m: Messages): unknown {
  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: app.name,
    description: m.meta.description,
    applicationCategory: 'GameApplication',
    operatingSystem: 'iOS, Android',
    inLanguage: m.htmlLang,
    url: absoluteUrl(pathFor(locale)),
    image: absoluteUrl(OG_IMAGE),
  };
}

export function faqSchema(m: Messages): unknown {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: m.faq.items.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: { '@type': 'Answer', text: item.answer },
    })),
  };
}

export interface MetaTag {
  readonly kind: 'name' | 'property';
  readonly key: string;
  readonly value: string;
}

export interface LinkTag {
  readonly rel: string;
  readonly href: string;
  readonly hreflang?: string;
  readonly type?: string;
  readonly sizes?: string;
}

export interface HeadData {
  readonly title: string;
  readonly metas: readonly MetaTag[];
  readonly links: readonly LinkTag[];
}

export function buildHead(locale: Locale, m: Messages): HeadData {
  const canonical = absoluteUrl(pathFor(locale));
  const ogImage = absoluteUrl(OG_IMAGE);

  const metas: MetaTag[] = [
    { kind: 'name', key: 'description', value: m.meta.description },
    { kind: 'name', key: 'keywords', value: m.meta.keywords.join(', ') },
    { kind: 'name', key: 'theme-color', value: palette.bgTop },
    { kind: 'name', key: 'robots', value: 'index, follow' },

    { kind: 'property', key: 'og:type', value: 'website' },
    { kind: 'property', key: 'og:site_name', value: app.name },
    { kind: 'property', key: 'og:title', value: m.meta.title },
    { kind: 'property', key: 'og:description', value: m.meta.description },
    { kind: 'property', key: 'og:url', value: canonical },
    { kind: 'property', key: 'og:image', value: ogImage },
    { kind: 'property', key: 'og:image:width', value: String(OG_IMAGE_WIDTH) },
    { kind: 'property', key: 'og:image:height', value: String(OG_IMAGE_HEIGHT) },
    { kind: 'property', key: 'og:image:alt', value: m.meta.ogImageAlt },
    { kind: 'property', key: 'og:locale', value: m.ogLocale },

    { kind: 'name', key: 'twitter:card', value: 'summary_large_image' },
    { kind: 'name', key: 'twitter:title', value: m.meta.title },
    { kind: 'name', key: 'twitter:description', value: m.meta.description },
    { kind: 'name', key: 'twitter:image', value: ogImage },
    { kind: 'name', key: 'twitter:image:alt', value: m.meta.ogImageAlt },
  ];

  // Every locale advertises every other one, plus x-default for crawlers that
  // cannot infer a language from the request.
  for (const other of locales) {
    if (other === locale) continue;
    metas.push({
      kind: 'property',
      key: 'og:locale:alternate',
      value: other === 'de' ? 'de_DE' : 'en_US',
    });
  }

  const links: LinkTag[] = [
    { rel: 'canonical', href: canonical },
    { rel: 'icon', href: '/favicon.png', type: 'image/png' },
    { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' },
    ...locales.map((other) => ({
      rel: 'alternate',
      hreflang: other,
      href: absoluteUrl(pathFor(other)),
    })),
    { rel: 'alternate', hreflang: 'x-default', href: absoluteUrl(pathFor('en')) },
  ];

  return { title: m.meta.title, metas, links };
}

export function sitemapXml(): string {
  const urls = locales
    .map((locale) => {
      const alternates = [...locales, 'x-default' as const]
        .map((other) => {
          const href = absoluteUrl(pathFor(other === 'x-default' ? 'en' : other));
          return `    <xhtml:link rel="alternate" hreflang="${other}" href="${href}"/>`;
        })
        .join('\n');
      return [
        '  <url>',
        `    <loc>${absoluteUrl(pathFor(locale))}</loc>`,
        alternates,
        '    <changefreq>monthly</changefreq>',
        `    <priority>${locale === 'en' ? '1.0' : '0.9'}</priority>`,
        '  </url>',
      ].join('\n');
    })
    .join('\n');

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
    '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    urls,
    '</urlset>',
    '',
  ].join('\n');
}

export function robotsTxt(): string {
  return ['User-agent: *', 'Allow: /', '', `Sitemap: ${absoluteUrl('/sitemap.xml')}`, ''].join('\n');
}
