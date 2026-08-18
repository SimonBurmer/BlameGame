---
id: TASK-4
title: Resolve dual round-progression paths (RoundDriver vs POST /advance)
status: To Do
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-18 14:43'
labels:
  - backend
  - core
  - bug
milestone: m-0
dependencies: []
priority: high
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two competing mechanisms advance rounds: the automatic RoundDriver spawned by /start AND the manual POST /rooms/{code}/advance endpoint. Both advance and broadcast; using both on one room double-advances/desyncs. Pick one authoritative path and remove/guard the other.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 There is a single authoritative round-progression mechanism
- [ ] #2 The redundant path is removed or explicitly guarded against concurrent use
- [ ] #3 No double-advance or desync possible on a running room
<!-- AC:END -->
