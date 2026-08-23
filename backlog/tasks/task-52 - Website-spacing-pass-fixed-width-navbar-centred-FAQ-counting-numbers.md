---
id: TASK-52
title: 'Website: spacing pass, fixed-width navbar, centred FAQ, counting numbers'
status: Done
assignee: []
created_date: '2026-08-23 10:46'
updated_date: '2026-08-23 10:46'
labels: []
dependencies: []
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Polish pass on TASK-51. Section spacing was inconsistent and the timeline's heading landed hard against the band above it. The navbar shrank to 40% of the page on scroll, which fought the full-width layout. The FAQ sat off to one side. And the three figures under the hero were wrapped in a hover-drawn rectangle rather than counting up.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every section uses one vertical rhythm, and no heading sits against the section above it
- [x] #2 The navbar keeps the same width at every scroll position
- [x] #3 The FAQ is centred on the page
- [x] #4 The three figures count up when scrolled into view, with no rectangle or pointer
- [x] #5 The figures are server-rendered, so they are in the HTML with scripting off
- [x] #6 lint, typecheck, both locale builds, Flutter and backend tests all pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The count-up is written in src/components/site/, not vendored: Aceternity's number ticker is one of the paid blocks and ships no source. It animates with motion, the same library every vendored component here uses.

It writes digits straight to the text node rather than through React state — sixty renders a second to change one string is work for nothing, and the react-hooks/set-state-in-effect rule rejects the state version anyway. The server renders the finished number, so the figure is in the HTML for a crawler and for a reader with scripting off; the client blanks it to zero on mount, long before the band can be scrolled to.

pointer-highlight.tsx is deleted — the stats band was its only use.

Two 'broken' images on a 390px viewport are the bento phones inside 'hidden sm:flex'. The browser correctly never fetches them at that width. Not a defect: mobile is deliberately not downloading two screenshots it will not show.
<!-- SECTION:NOTES:END -->
