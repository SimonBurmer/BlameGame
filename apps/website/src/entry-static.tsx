/**
 * Build step: renders every locale to static HTML.
 *
 * The site ships no client JavaScript. Everything interactive on the page —
 * the language switch, the anchors, the FAQ accordion — is a link or a
 * <details>, so there is nothing to hydrate. That keeps the HTML a crawler
 * sees identical to the page a person sees.
 */
import { mkdir, copyFile, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { renderToStaticMarkup } from 'react-dom/server';
import { palette } from '@blame-game/brand';

import { App } from './App';
import { locales, messages, pathFor, type Locale } from './i18n';
import { buildHead, faqSchema, jsonLd, robotsTxt, sitemapXml, softwareApplicationSchema } from './seo';

const here = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(here, '..');
const repoRoot = resolve(projectRoot, '../..');
const outDir = join(projectRoot, 'dist');

/** CSS custom properties, generated so the stylesheet never repeats a hex. */
function cssVariables(): string {
  const vars: Record<string, string> = {
    '--bg-top': palette.bgTop,
    '--bg-mid': palette.bgMid,
    '--bg-bottom': palette.bgBottom,
    '--brand': palette.brand,
    '--accent': palette.accent,
    '--fg': palette.onSurfaceStrong,
    '--fg-muted': palette.onSurfaceMuted,
    '--fg-faint': palette.onSurfaceFaint,
    '--tint': palette.surfaceTint,
    '--tint-strong': palette.surfaceTintStrong,
  };
  const body = Object.entries(vars)
    .map(([k, v]) => `  ${k}: ${v};`)
    .join('\n');
  return `:root {\n${body}\n}\n`;
}

function renderDocument(locale: Locale, css: string, logoSvg: string): string {
  const m = messages[locale];
  const head = buildHead(locale, m);

  const body = renderToStaticMarkup(<App locale={locale} m={m} logoSvg={logoSvg} />);

  const metas = head.metas
    .map((t) => `    <meta ${t.kind}="${t.key}" content="${escapeAttr(t.value)}">`)
    .join('\n');

  const links = head.links
    .map((l) => {
      const attrs = [`rel="${l.rel}"`, `href="${escapeAttr(l.href)}"`];
      if (l.hreflang) attrs.push(`hreflang="${l.hreflang}"`);
      if (l.type) attrs.push(`type="${l.type}"`);
      if (l.sizes) attrs.push(`sizes="${l.sizes}"`);
      return `    <link ${attrs.join(' ')}>`;
    })
    .join('\n');

  return `<!doctype html>
<html lang="${m.htmlLang}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${escapeHtml(head.title)}</title>
${metas}
${links}
    <style>${css}</style>
    <script type="application/ld+json">${jsonLd(softwareApplicationSchema(locale, m))}</script>
    <script type="application/ld+json">${jsonLd(faqSchema(m))}</script>
  </head>
  <body>${body}</body>
</html>
`;
}

function escapeHtml(value: string): string {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function escapeAttr(value: string): string {
  return escapeHtml(value).replace(/"/g, '&quot;');
}

async function copyPublicAssets(): Promise<number> {
  const publicDir = join(projectRoot, 'public');
  let entries: string[];
  try {
    entries = await readdir(publicDir);
  } catch {
    return 0;
  }
  await Promise.all(entries.map((name) => copyFile(join(publicDir, name), join(outDir, name))));
  return entries.length;
}

async function build(): Promise<void> {
  const [rawCss, logoSvg] = await Promise.all([
    readFile(join(projectRoot, 'src/styles.css'), 'utf8'),
    readFile(join(repoRoot, 'assets/branding/logo_mark.svg'), 'utf8'),
  ]);
  const css = cssVariables() + rawCss;

  await mkdir(outDir, { recursive: true });

  for (const locale of locales) {
    const path = pathFor(locale);
    const dir = path === '/' ? outDir : join(outDir, path);
    await mkdir(dir, { recursive: true });
    await writeFile(join(dir, 'index.html'), renderDocument(locale, css, logoSvg), 'utf8');
  }

  await writeFile(join(outDir, 'sitemap.xml'), sitemapXml(), 'utf8');
  await writeFile(join(outDir, 'robots.txt'), robotsTxt(), 'utf8');
  const assets = await copyPublicAssets();

  console.log(
    `built ${locales.length} locales (${locales.join(', ')}), sitemap.xml, robots.txt, ${assets} assets -> dist/`,
  );
}

await build();
