---
id: TASK-50
title: 'Website: rebuild on Next.js + Aceternity, with real photos in the screenshots'
status: Done
assignee: []
created_date: '2026-08-23 02:30'
updated_date: '2026-08-23 02:31'
labels: []
dependencies: []
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The site looked generic and its screenshots showed drawn placeholder images. Rebuild it as a clean Next.js + Tailwind install using only Aceternity UI components, so it has one visual vocabulary, and stage it as a cinematic story rather than a feature list. Load real photographs into the app for the capture run so the screenshots show a real camera roll.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 apps/website is a clean Next.js (App Router) + Tailwind v4 install, statically exported
- [x] #2 Every animated component comes from the Aceternity UI registry; no second component library
- [x] #3 The screenshots are captures of the app on a simulator, with real photographs in it
- [x] #4 The photographs on the page are the same ones the app is holding in the screenshots
- [x] #5 The page is a scroll-driven narrative, not a list of sections
- [x] #6 EN and DE both build; canonical, hreflang, Open Graph and JSON-LD survive the build
- [x] #7 lint, typecheck and build are clean, and the page hydrates with no console errors
<!-- AC:END -->
