---
id: TASK-38
title: Add Flutter test coverage for GameController
status: Done
assignee: []
created_date: '2026-08-22 01:21'
updated_date: '2026-08-22 10:29'
labels:
  - testing
  - flutter
milestone: m-4
dependencies:
  - TASK-21
priority: medium
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GameController is the heart of the client and has zero direct tests, because GameSocket.connect is a hard-coded factory with no seam. Add a socket-factory injection point and a fake, then cover the event-driven state transitions: per-round state reset, room_reset play-again, score accumulation, join wiring, duplicate player_joined, and the guess lock-and-rollback path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A fake socket can drive controller state in tests without a network
- [x] #2 Each GameEvent branch has a test
- [x] #3 The guess failure rollback is covered
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added a GameSocketFactory seam (4 lines) plus test/support/fakes.dart and pump.dart. Flutter suite went 15 -> 57 tests: 21 controller tests covering every GameEvent branch, connection loss/reconnect, the guess lock-and-rollback, and the late-joiner merge; plus widget tests for lobby, game and results screens.
<!-- SECTION:NOTES:END -->
