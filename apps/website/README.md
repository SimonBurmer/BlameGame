# Website

The marketing site for Blame Game. English and German, prerendered to static
HTML, **no client JavaScript**.

```sh
npm install                 # from the repo root — this is a workspace
npm run build -w @blame-game/website
npm run preview -w @blame-game/website   # builds, then serves dist/ on :4173
```

## Why there is no client bundle

Everything on the page that looks interactive is a native element: the language
switch is two links, the section jumps are anchors, the FAQ is `<details>`.
Nothing needs hydrating, so nothing ships. React and TypeScript are the
authoring layer, not the runtime — `src/entry-static.tsx` renders each locale
with `renderToStaticMarkup` and writes the HTML.

That makes the page a crawler sees byte-identical to the page a person sees,
which is the whole SEO argument.

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

`public/` is generated, not hand-made — `scripts/generate-app-icons.sh` renders
the favicon, the Apple touch icon and the Open Graph card from the same vectors
as the app icon, so the site cannot drift from the app. Do not edit the PNGs.

## Not here yet

No imprint, privacy policy or cookie banner. The site sets no cookies and runs
no analytics, so there is nothing to consent to today — but a German-language
site will need an Impressum and a Datenschutzerklärung before it is public.
