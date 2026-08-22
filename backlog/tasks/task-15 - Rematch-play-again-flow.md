---
id: TASK-15
title: Rematch / play-again flow
status: Done
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 18:04'
labels:
  - frontend
  - backend
  - gameplay
milestone: m-3
dependencies: []
priority: high
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
ResultsScreen only offers 'BACK TO HOME'. The real game lets the same group play another round without recreating the room. Add a rematch that keeps players together and starts a new game.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Results screen has a 'Play Again' / rematch action
- [x] #2 Rematch keeps the existing players and starts a fresh game
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented by TASK-24's reset flow: POST /rooms/{code}/reset (host-only) -> reset_room() -> room_reset broadcast, ApiClient.resetRoom / GameController.resetRoom, and the results screen's 'START NEW ROUND' button. Every client (not just the host) navigates to the lobby off the room_reset event, so nobody is stranded on the leaderboard.

Photos: a rematch KEEPS the existing photo pool (reset_room clears only rounds), so no re-upload is needed and the lobby's 'photos from 2+ distinct players' rule still holds automatically. Scores carry over as a running total.

Epoch: reset_room bumps room.epoch, so a RoundDriver left over from the finished game bows out instead of driving the rematch. Only gap found was test coverage for that bump; added test_reset_bumps_the_epoch (the stale-driver-after-restart paths were already covered in tests/test_timer.py).
<!-- SECTION:NOTES:END -->
