---
id: TASK-4
title: Resolve dual round-progression paths (RoundDriver vs POST /advance)
status: Done
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-22 10:42'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Resolved by deleting POST /rooms/{code}/advance and its _broadcast_round_started helper. The RoundDriver is now the only thing that advances a round. The endpoint was unauthenticated, had no caller in lib/, and racing it against the driver was reproducible: it either crashed the driver task (leaving clients hanging with no game_finished) or made the driver reveal round N's index with round N+1's photo and skip a round. The driver additionally re-checks room state and current_round after waiting, so it stops rather than acting on a round that moved underneath it.
<!-- SECTION:NOTES:END -->
