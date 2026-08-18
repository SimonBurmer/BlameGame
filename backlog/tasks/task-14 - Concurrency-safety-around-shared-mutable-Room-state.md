---
id: TASK-14
title: Concurrency safety around shared mutable Room state
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-18 14:43'
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
