---
id: TASK-48
title: 'Marketing website for the app (React + TypeScript, EN/DE)'
status: Done
assignee: []
created_date: '2026-08-22 21:36'
updated_date: '2026-08-22 21:50'
labels: []
dependencies: []
ordinal: 48000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The app has no web presence. Build a static marketing landing page that promotes it, in English and German, and restructure the repo as a monorepo so the site can share brand tokens with the app instead of copying hex codes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Repo is an npm workspaces monorepo; the site lives in apps/website and shares brand tokens from packages/brand
- [x] #2 Landing page is React + TypeScript and ships as prerendered static HTML
- [x] #3 Full English and German versions, each on its own URL, with a language switch
- [x] #4 SEO: per-locale title/description/canonical, hreflang alternates, Open Graph and Twitter cards, JSON-LD, sitemap.xml and robots.txt
- [x] #5 Copy describes what the app actually does; no invented store links
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Monorepo: npm workspaces at the root, apps/website and packages/brand. The Flutter app and the FastAPI backend stay where they are - moving them would break the Xcode project, the icon scripts and the CI paths for no benefit, and a workspace root does not require it.

The site ships zero client JavaScript. React and TypeScript are the authoring layer only: src/entry-static.tsx renders each locale with renderToStaticMarkup and writes the HTML. Everything that looks interactive is native - the language switch is two links, the section jumps are anchors, the FAQ is <details>. So the markup a crawler sees is byte-identical to the page a person sees, which is the whole SEO argument, and there is no hydration to get wrong.

Copy lives in src/i18n/{en,de}.ts, both annotated ': Messages'. A key present in one language and missing in the other fails tsc, and typecheck runs as part of build, so a half-translated page cannot ship. Both files came out at 118 lines, which is the parity showing.

SEO, all asserted against the built HTML for both locales: per-locale title/description, canonical, hreflang for en/de plus x-default, Open Graph (incl. og:locale and og:locale:alternate), Twitter summary_large_image, theme-color, favicon and apple-touch-icon, and JSON-LD for SoftwareApplication and FAQPage. sitemap.xml and robots.txt are generated from the same locales array, so adding a language needs no edits to any of them.

Deliberately no aggregateRating and no offers in the structured data, and no store buttons: the app has no ratings, no price and no listing. stores.appStore/playStore in packages/brand are null until there is something real to point at.

packages/brand also carries the game limits (12 players, 10 photos, 5-char code) sourced from backend/app/game.py and store.py, so the copy quotes the rules rather than retyping them.

scripts/rasterize-svg.swift now accepts 'out.png:WxH' as well as 'out.png:N', and generate-app-icons.sh renders the site's favicon, apple-touch-icon and the 1200x630 Open Graph card from assets/branding - the site cannot drift from the app icon. Re-running the generator produced a zero-line diff against the committed icons.

Added a 'Website build' CI job that typechecks, builds, and then greps the output for canonical, hreflang, og:image and JSON-LD in both locales. It is not in the branch-protection ruleset, so it reports without blocking.

Verified: clean build of both locales; every SEO assertion checked against the generated HTML; rendered in headless Chrome at 1280px and at a true 390px viewport (Chrome clamps headless windows to 500px, so the narrow check needs --force-device-scale-factor=2 - the first 'mobile overflow' I saw was a cropped screenshot, not a layout bug, and a scrollWidth probe confirmed nothing overflows). flutter analyze clean, 83 Flutter tests pass, 125 backend tests pass.

Not included, as asked: imprint, privacy policy, cookie banner. Worth flagging that a German-language site needs an Impressum and a Datenschutzerklaerung before it is publicly reachable.
<!-- SECTION:NOTES:END -->
