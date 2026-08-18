---
id: TASK-3
title: Validate guess timing server-side to prevent score cheating
status: To Do
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-18 14:43'
labels:
  - backend
  - security
  - core
milestone: m-0
dependencies:
  - TASK-2
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GuessBody.seconds_left is client-supplied and trusted by scoring (seconds_left * 100). A client can send seconds_left: 999 for an arbitrary score. Server must track each round's actual start time and compute/validate remaining seconds itself.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Server records authoritative round start time when a round begins
- [ ] #2 Score is computed from server-measured elapsed time, not the client-supplied value
- [ ] #3 Guesses arriving after the round window are rejected or scored zero
<!-- AC:END -->
