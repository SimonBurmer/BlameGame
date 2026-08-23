import type { MetadataRoute } from 'next';

import { locales, pathFor } from '@/i18n';
import { absoluteUrl } from '@/lib/seo';

/** Derived from `locales`, so a new language needs no edit here. */
/** `output: export` needs route handlers pinned to build time. */
export const dynamic = 'force-static';

export default function sitemap(): MetadataRoute.Sitemap {
  return locales.map((locale) => ({
    url: absoluteUrl(pathFor(locale)),
    changeFrequency: 'monthly',
    priority: locale === 'en' ? 1 : 0.9,
    alternates: {
      languages: Object.fromEntries(locales.map((l) => [l, absoluteUrl(pathFor(l))])),
    },
  }));
}
