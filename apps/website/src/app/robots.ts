import type { MetadataRoute } from 'next';

import { absoluteUrl } from '@/lib/seo';

/** `output: export` needs route handlers pinned to build time. */
export const dynamic = 'force-static';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/' },
    sitemap: absoluteUrl('/sitemap.xml'),
  };
}
