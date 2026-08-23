/**
 * Build step: renders every locale to static HTML.
 *
 * The markup is complete before any script runs — every animated component
 * renders its content server-side and only starts moving once hydrated — so a
 * crawler and a person with JavaScript off both get the whole page. The client
 * bundle is enhancement: motion, the cursor spotlight, the tilt.
 *
 * `<html class="no-js">` plus a one-line inline script is what keeps that
 * honest: if scripting never runs, the class stays and CSS forces anything
 * that would have animated in to be visible.
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

interface ClientAssets {
  readonly script: string;
  readonly styles: readonly string[];
}

/** Reads Vite's manifest to find the hashed client entry and its CSS. */
async function clientAssets(): Promise<ClientAssets> {
  const manifestPath = join(outDir, '.vite/manifest.json');
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8')) as Record<
    string,
    { file: string; css?: string[]; isEntry?: boolean }
  >;
  const entry = Object.values(manifest).find((chunk) => chunk.isEntry);
  if (!entry) throw new Error('no client entry in the Vite manifest');
  return { script: `/${entry.file}`, styles: (entry.css ?? []).map((f) => `/${f}`) };
}

function renderDocument(
  locale: Locale,
  css: string,
  logoSvg: string,
  assets: ClientAssets,
): string {
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

  const data = jsonLd({ locale, logoSvg });
  const stylesheets = assets.styles
    .map((href) => `    <link rel="stylesheet" href="${href}">`)
    .join('\n');

  return `<!doctype html>
<html lang="${m.htmlLang}" class="no-js">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${escapeHtml(head.title)}</title>
${metas}
${links}
    <script>document.documentElement.classList.remove('no-js')</script>
    <style>${css}</style>
${stylesheets}
    <script type="application/ld+json">${jsonLd(softwareApplicationSchema(locale, m))}</script>
    <script type="application/ld+json">${jsonLd(faqSchema(m))}</script>
  </head>
  <body>
    <div id="root">${body}</div>
    <script type="application/json" id="__APP_DATA__">${data}</script>
    <script type="module" src="${assets.script}"></script>
  </body>
</html>
`;
}

function escapeHtml(value: string): string {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function escapeAttr(value: string): string {
  return escapeHtml(value).replace(/"/g, '&quot;');
}

/** Copies public/ into dist/, one level of subdirectory deep (screenshots/). */
async function copyPublicAssets(): Promise<number> {
  const publicDir = join(projectRoot, 'public');
  let entries;
  try {
    entries = await readdir(publicDir, { withFileTypes: true });
  } catch {
    return 0;
  }
  let count = 0;
  for (const entry of entries) {
    const from = join(publicDir, entry.name);
    const to = join(outDir, entry.name);
    if (entry.isDirectory()) {
      await mkdir(to, { recursive: true });
      for (const child of await readdir(from)) {
        await copyFile(join(from, child), join(to, child));
        count += 1;
      }
    } else {
      await copyFile(from, to);
      count += 1;
    }
  }
  return count;
}

async function build(): Promise<void> {
  const [rawCss, animCss, logoSvg] = await Promise.all([
    readFile(join(projectRoot, 'src/styles.css'), 'utf8'),
    readFile(join(projectRoot, 'src/styles-animation.css'), 'utf8'),
    readFile(join(repoRoot, 'assets/branding/logo_mark.svg'), 'utf8'),
  ]);
  const css = cssVariables() + rawCss + animCss;

  await mkdir(outDir, { recursive: true });
  const client = await clientAssets();

  for (const locale of locales) {
    const path = pathFor(locale);
    const dir = path === '/' ? outDir : join(outDir, path);
    await mkdir(dir, { recursive: true });
    await writeFile(
      join(dir, 'index.html'),
      renderDocument(locale, css, logoSvg, client),
      'utf8',
    );
  }

  await writeFile(join(outDir, 'sitemap.xml'), sitemapXml(), 'utf8');
  await writeFile(join(outDir, 'robots.txt'), robotsTxt(), 'utf8');
  const assets = await copyPublicAssets();

  console.log(
    `built ${locales.length} locales (${locales.join(', ')}), sitemap.xml, robots.txt, ${assets} assets -> dist/`,
  );
}

await build();
