---
id: TASK-16
title: Leave-room and host kick-player support
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 15:33'
labels:
  - frontend
  - backend
  - gameplay
milestone: m-3
dependencies: []
priority: low
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
There is no leave-room or delete-room endpoint and no kick. Players can't cleanly exit and hosts can't remove someone. Add leave (client + server) and host-only kick.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A player can leave a room and is removed for everyone
- [x] #2 The host can kick a player
- [x] #3 Host leaving is handled (reassign host or end room)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
One remove_player in game.py serves both leave and kick, so the edge cases live in one place rather than in two callers. Two endpoints (POST /rooms/{code}/leave, host-only POST /rooms/{code}/kick) and one player_left broadcast carrying a kicked flag plus the refreshed roster, reusing the existing sealed GameEvent pattern.

Edges handled: a departing player's photos leave with them and not-yet-played rounds are re-pointed at a surviving photo (already-played rounds keep theirs - rewriting those would rewrite history players already saw and scored); a room that drops below two players or runs out of photos goes FINISHED rather than running the clock on unwinnable rounds; the host role hands to the next player; stale guesses from a departed player are cleared, or they would block the round from ever closing early.

Also fixed a real bug found via a failing test: the kicked player's explanation snackbar was posted on the lobby's messenger and then the lobby popped, taking the message with it, so they were ejected with no idea why.

Backend 73 -> 100, Flutter 57 -> 71. Verified independently by the orchestrator: pytest 100 passed, ruff clean, flutter test 71 passed, flutter analyze clean.

Known gap, deliberately not fixed here and tracked as TASK-45: a kicked player's already-open WebSocket stays connected until they next interact. PR: https://github.com/SimonBurmer/BlameGame/pull/29
<!-- SECTION:NOTES:END -->
