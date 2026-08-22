---
id: TASK-21
title: Add Flutter widget/unit test coverage
status: Done
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 10:42'
labels:
  - frontend
  - testing
milestone: m-4
dependencies: []
priority: medium
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Flutter app has essentially no test coverage of screens, GameController state transitions, ApiClient, or GameSocket event mapping. Add widget tests for the four screens and unit tests for the controller/services (ApiClient already accepts an injectable http.Client for this).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 GameController state transitions are unit-tested
- [ ] #2 ApiClient and GameSocket are unit-tested with mocked transport
- [ ] #3 Each screen has at least a basic widget test
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Flutter suite went 15 -> 57 tests. Added test/support/{fakes,pump}.dart (fake socket, role-based HTTP fake, player builder, phone-sized pump helper), 21 GameController tests covering every GameEvent branch plus connection loss, reconnect, the guess lock-and-rollback and the late-joiner merge, and widget tests for the lobby, game and results screens. Needed one 4-line production seam: a GameSocketFactory injected into the controller.
<!-- SECTION:NOTES:END -->
