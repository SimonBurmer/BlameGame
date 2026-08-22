---
id: TASK-14
title: Concurrency safety around shared mutable Room state
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 10:42'
labels:
  - backend
  - core
  - bug
milestone: m-2
dependencies: []
priority: medium
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The RoundDriver may advance/finish a round while late REST guesses arrive; there is no locking around the shared mutable Room object. Add proper synchronization (per-room lock/async lock) so concurrent guess/advance operations can't corrupt state.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Concurrent guess and round-advance operations on a room are serialized safely
- [ ] #2 No state corruption possible under concurrent access
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Still open, but the worst instance is fixed: RoundDriver re-reads room state and current_round after awaiting and returns rather than acting on a round that moved underneath it, and the REVEALING state closes the guess window during the reveal hold. The general problem (shared mutable Room under asyncio with no lock) stands.
<!-- SECTION:NOTES:END -->
