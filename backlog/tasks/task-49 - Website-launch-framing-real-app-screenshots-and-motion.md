---
id: TASK-49
title: 'Website: launch framing, real app screenshots, and motion'
status: Done
assignee: []
created_date: '2026-08-23 01:07'
updated_date: '2026-08-23 01:07'
labels: []
dependencies: []
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The site reads as pre-launch and is entirely static. Reframe the copy as if the app is on the App Store, add a store button, put real captures of the app on the page, and make it move.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Copy and CTA present the app as available, with an App Store button whose link is empty until there is a listing
- [x] #2 Real screenshots captured from the app running on a simulator are shown on the page
- [x] #3 The page is animated using React Bits components, and the registry is configured for future use
- [x] #4 Prerendered HTML still carries the full content and all SEO tags; the page works with JavaScript disabled
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Launch framing: hero badge, CTA and the download FAQ now read as shipped. The App Store button is real markup with an empty href - stores.appStore in packages/brand is '' so filling it in is one edit. No Play Store button: there is no Android listing and a dead second button is worse than one.

Screenshots are genuine captures of the app on a booted simulator, not mockups. scripts/capture-app-screenshots.sh starts the backend, populates a room with four players and photos over HTTP, drives one client through the game with integration_test, and shoots with simctl on markers the test prints. Doing the capture host-side avoids the platform screenshot APIs entirely. scripts/prepare-screenshots.sh resizes to 540px JPEGs (~20 KB each). The five shots are taken in different rounds so they do not all show the same photo.

The camera-roll photos in those shots are drawn, not real (assets/demo-photos/, regenerated into a Dart fixture by scripts/generate-demo-photos.sh). A screenshot of a game about people's private photos should not contain anybody's private photos.

This surfaced TASK-46 independently: driving lobby -> game reproduces the crash every time. Root cause is written up on that ticket - Navigator.pushReplacement completes the replaced route's future, which is the future HomeScreen awaits before disposing the controller. Not fixed here; the in-game screenshots are taken by mounting the game flow directly, which is the same screen and the same data on the same device, just reached by a different route.

Motion: five React Bits components vendored as TS + plain CSS (BlurText, SpotlightCard, CountUp, TiltedCard, Magnet) with one animation dependency, motion. components.json points at the registry so the shadcn MCP server can add more later - note the MCP server itself needs a Claude Code restart before it is usable, so these were pulled straight from the registry JSON instead.

The site now hydrates, where before it shipped no client JavaScript at all. Prerendering is unchanged, so the HTML still carries the whole page and every SEO tag; the bundle only adds movement. html.no-js plus an inline unsetter and CSS fallbacks mean a visitor without JavaScript still sees the headline and the counters rather than blank space. Cost: about 110 KB gzipped.

Vendored React Bits files were edited for this repo's strict + noUncheckedIndexedAccess tsconfig. Re-fetching a component from the registry overwrites those edits; noted in the README and in the file headers.

Verified: both locales build; all SEO assertions re-checked against the generated HTML plus new checks for the hydration root, the client script, the no-js guard, the screenshots and the empty store href; rendered in headless Chrome with no hydration warnings.
<!-- SECTION:NOTES:END -->
