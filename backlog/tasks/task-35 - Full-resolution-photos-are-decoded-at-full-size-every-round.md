---
id: TASK-35
title: Full-resolution photos are decoded at full size every round
status: Done
assignee: []
created_date: '2026-08-22 01:20'
updated_date: '2026-08-22 10:27'
labels:
  - bug
  - flutter
  - performance
milestone: m-3
dependencies: []
priority: high
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PhotoSampler uploads originBytes (full-resolution camera originals, e.g. 4032x3024) and game_screen renders them with Image.network into a ~350px box with no cacheWidth. Decoded RGBA is ~48MB per photo against a 100MB image cache, so two or three rounds thrash the cache and on lower-memory devices this is an OOM kill rather than jank.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Photos are decoded at display size, not source size
- [x] #2 Memory stays flat across a full game
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Image.network now passes cacheWidth derived from the display width and devicePixelRatio, so a ~4032px original decodes at ~350pt instead of ~48MB.
<!-- SECTION:NOTES:END -->
