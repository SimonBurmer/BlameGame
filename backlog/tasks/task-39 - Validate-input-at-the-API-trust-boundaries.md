---
id: TASK-39
title: Validate input at the API trust boundaries
status: Done
assignee: []
created_date: '2026-08-22 01:21'
updated_date: '2026-08-22 10:29'
labels:
  - backend
  - security
  - validation
milestone: m-2
dependencies:
  - TASK-19
priority: medium
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Confirmed live against the running backend: an empty player name and a 500-character name are both accepted with 200. Photo upload reads the whole body into memory with no size cap and trusts the client-supplied content type while always saving as .jpg. start_game bounds for total_rounds and round_seconds are unchecked.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Player names are length-and-content validated
- [x] #2 Photo uploads are size-capped
- [x] #3 Round configuration bounds are enforced
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Names are 1-24 chars (empty and 500-char names were both accepted with 200, confirmed live). Uploads capped at 8MB streamed with a 413, JPEG/PNG magic bytes checked rather than trusting content-type, 10 photos per player, lobby-state only, and the file is written only after validation so a rejected upload leaves no orphan. total_rounds and round_seconds bounded at the boundary (422). Room capacity 12. CORS allow_credentials turned off - with allow_origins='*' Starlette was reflecting any origin.
<!-- SECTION:NOTES:END -->
