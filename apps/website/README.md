# Blame Game — website

The marketing site. Next.js (App Router) + Tailwind v4, statically exported to
`out/`: a folder of HTML any host can serve, with no server behind it.

```sh
npm install                                       # from the repo root
npm run dev     --workspace @blame-game/website   # localhost:3000
npm run build   --workspace @blame-game/website   # -> apps/website/out
npm run preview --workspace @blame-game/website   # build, then serve on :4173
npm run lint    --workspace @blame-game/website
```

## What the page is

A dark room with a photo thrown on the wall. It is built as one story rather
than a list of features:

| Section | What it does |
| --- | --- |
| Hero | The wall of everyone's photos, on an angle, with the question over it |
| Numbers | The three limits the game actually enforces |
| The moment | Scrolling tips a screen flat: one round, on three phones |
| Three things happen | The rules, on a rail that fills in as you pass it |
| What is in it | Features, two of them holding a real screen |
| Questions | FAQ |
| Get everyone in a room | The name, drawn; then the button |

## Everything on it is real

- **`public/screenshots/`** are captures of the app running on a simulator, not
  mockups. `scripts/capture-app-screenshots.sh` drives it through a whole game
  and shoots with `simctl`; `scripts/prepare-screenshots.sh` sizes them.
- **`public/photos/`** are the photographs the app is holding in those
  screenshots — the same twelve files, written by
  `scripts/generate-demo-photos.sh` from `assets/demo-photos/`. They are real
  photographs under the Unsplash licence, credited in that folder's README and
  in the site footer. Do not edit `public/photos/` by hand; it is generated.
- **`public/favicon.png`, `apple-touch-icon.png`, `og-image.png`** come out of
  `scripts/generate-app-icons.sh`, from the same SVG as the launcher icon, so
  the site cannot drift from the app.

## Layout

```
src/app/[[...lang]]/   one route, two pages: / is English, /de/ is German
src/app/sitemap.ts     both derived from `locales`; adding a language edits
src/app/robots.ts      neither of them, nor any hreflang tag
src/components/ui/     vendored Aceternity UI — see below
src/components/site/   this site's own composition
src/i18n/              the copy
src/lib/               cn(), the SEO metadata, the photo list
```

### Aceternity UI is vendored, and some of it is edited

Every animated component comes from the [Aceternity UI](https://ui.aceternity.com)
registry and lives in `src/components/ui`. They are pulled as source, not
installed, which is how that registry is meant to be used — and it means the
page has one visual vocabulary rather than three.

Several of them needed edits to work here: React 19's ref types, this repo's
`strict` TypeScript, and the fact that they ship styled for a light page with
Aceternity's own demo copy inside them. **Every edited file says so at the top,
and re-fetching a component from the registry throws those edits away.** Read
the header before replacing one.

Two consequences worth knowing:

- `src/components/ui/**` is exempted from a few lint rules in
  `eslint.config.mjs`. It is upstream's code; holding it to our hook and ref
  rules would mean rewriting it, and every rewrite is lost on the next fetch.
  Everything else is linted normally.
- Tailwind's `dark:` variant is bound to a class (`globals.css`) and `dark` is
  on `<html>`. Those components style themselves almost entirely through
  `dark:`, and the default variant follows the operating system — so without
  this the page would render light for anyone whose machine is set to light.

## Translations cannot half-ship

`src/i18n/en.ts` and `de.ts` are both annotated `: Messages`. A key in one
language and not the other is a compile error, and `next build` runs `tsc`
before it renders anything.

## SEO

Per-locale title and description, canonical, hreflang for both plus
`x-default`, Open Graph (including `og:locale:alternate`), a Twitter summary
card, and JSON-LD for `SoftwareApplication` and `FAQPage` — all from Next's
metadata API, all derived from the `locales` array.

Deliberately absent: `aggregateRating` and `offers`. There are no ratings and
no price, and structured data that claims otherwise is how a site earns a manual
action instead of a rich result.

The page is prerendered, so the whole of it — every heading, answer and tag —
is in the HTML before a single script runs. The client bundle only adds motion,
and a `<noscript>` rule reveals the pieces that fade themselves in.

## Before this goes public

- The copy says the app is on the App Store. **It is not.** `stores.appStore`
  in `packages/brand` is an empty string, so the button renders but is not a
  link; fill it in and every one of them becomes real at once.
- `siteOrigin` is `https://blamegame.app`, which nobody owns yet. Every
  canonical, hreflang and sitemap URL is built from it.
- There is no Impressum and no Datenschutzerklärung. The site sets no cookies
  and runs no analytics, but a German-language site needs both.
