# Website

The marketing site for Blame Game. English and German, prerendered to static
HTML, **no client JavaScript**.

```sh
npm install                 # from the repo root — this is a workspace
npm run build -w @blame-game/website
npm run preview -w @blame-game/website   # builds, then serves dist/ on :4173
```

## Prerendered, then hydrated

`src/entry-static.tsx` renders every locale with `renderToStaticMarkup` and
writes the HTML; `src/entry-client.tsx` hydrates it. The markup is complete
before any script runs — the animated components render their content
server-side and only start moving once mounted — so a crawler, and anybody with
JavaScript off, still gets the entire page.

`<html class="no-js">` plus a one-line inline script keeps that honest: the
script removes the class immediately, and if scripting never runs the class
stays and CSS in `styles-animation.css` forces anything that would have
animated in to be visible. Without it, a no-JS visitor would get an invisible
headline.

The trade is weight: hydration plus `motion` is roughly 110 kB gzipped. That is
the price of the animation, and it is worth re-checking if the page ever needs
to be fast on a bad connection more than it needs to move.

## React Bits

`src/components/reactbits/` is vendored from the React Bits registry (the
TypeScript + plain-CSS variants; this site has no Tailwind). `components.json`
points at the registry so `shadcn` and its MCP server can add more.

Those files have been edited to satisfy this project's `strict` +
`noUncheckedIndexedAccess` tsconfig. **Re-fetching a component from the
registry will overwrite those edits** — expect to redo them.

## Adding or changing copy

All copy lives in `src/i18n/en.ts` and `src/i18n/de.ts`. Both are annotated
`: Messages`, so adding a key to one language and forgetting the other is a
compile error rather than a blank space on the page. `npm run typecheck` is
part of `build`, so this cannot ship broken.

## Adding a locale

1. Add the code to `Locale` and `locales` in `src/i18n/types.ts`.
2. Add `src/i18n/<code>.ts` — TypeScript will list what is missing.
3. Register it in `src/i18n/index.ts`.

`hreflang`, `og:locale:alternate`, the sitemap and the language switch are all
derived from `locales`, so they pick it up without further edits. English is
served from `/`; every other locale gets a path prefix.

## SEO

`src/seo.ts` owns it: per-locale title and description, canonical, `hreflang`
alternates including `x-default`, Open Graph and Twitter cards, and JSON-LD for
`SoftwareApplication` and `FAQPage`. `sitemap.xml` and `robots.txt` are
generated from the same locale list.

There is deliberately no `aggregateRating` and no `offers` in the structured
data. The app has no ratings and no price, and inventing either is how a site
earns a manual action instead of a rich result.

## Assets

`public/` is generated, not hand-made. Do not edit it by hand.

- `scripts/generate-app-icons.sh` renders the favicon, the Apple touch icon and
  the Open Graph card from the same vectors as the app icon, so the site cannot
  drift from the app.
- `public/screenshots/` are real captures of the app running on a simulator.
  `scripts/capture-app-screenshots.sh` drives it through the game and shoots;
  `scripts/prepare-screenshots.sh` resizes them for the web. Nothing here is a
  mockup.

## Not here yet

No imprint, privacy policy or cookie banner. The site sets no cookies and runs
no analytics, so there is nothing to consent to today — but a German-language
site will need an Impressum and a Datenschutzerklärung before it is public.
