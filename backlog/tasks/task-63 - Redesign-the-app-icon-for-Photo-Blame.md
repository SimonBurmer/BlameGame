---
id: TASK-63
title: Redesign the app icon for Photo Blame
status: In Progress
assignee: []
created_date: '2026-08-31 00:16'
updated_date: '2026-08-31 00:16'
labels: []
dependencies: []
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The crosshair-over-a-photo-card mark shipped with task-40 and does not survive the rename: it reads as a camera utility, not a party game, and the crosshair was the strongest thing in it.

The new icon is three photo cards fanned like a hand of cards on a brand-red sunburst, under sixty pieces of confetti. It was picked from eight rounds of alternatives; the fan won because it is the only composition with a silhouette of its own (a single card on a dark ground describes half the category) and because it carries the multiplayer idea without spelling it out.

Two constraints the artwork encodes and future changes must keep. Red is not in the confetti palette - a red chip on a red sunburst is invisible. And logo_mark.svg keeps only the largest dozen confetti pieces, because sixty is texture at 1024px and mush at the 96px the home screen draws the mark at.

The marketing site on feature/task-48-marketing-website carries the same mark inline in logo.tsx plus its own og_image.svg, so it needs the same pass on that branch.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The four branding SVGs are the new artwork and every launcher icon is regenerated from them by scripts/generate-app-icons.sh
- [x] #2 The Android adaptive foreground survives a circular mask and the iOS icon reads at 40px
- [x] #3 The website's inline LogoMark and og_image.svg carry the same artwork, and the site typechecks and builds
- [x] #4 CLAUDE.md describes the new mark rather than the crosshair
<!-- AC:END -->
