---
id: TASK-24
title: Reset room to lobby for a new round without recreating it
status: Done
assignee: []
created_date: '2026-08-18 16:23'
updated_date: '2026-08-21 23:04'
labels:
  - backend
  - frontend
  - gameplay
milestone: m-0
dependencies:
  - TASK-15
priority: medium
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
There is currently no way to start another round with the same room/players once a game reaches FINISHED (or mid-lobby) — the only path is to create a brand new room and re-share the code. Add a way to reset the current room back to LOBBY state (or directly into a fresh set of rounds) so the host can start a new round with the same group and same room code. This is the backend/state-machine mechanism that TASK-15's 'Play Again' button (and a lobby-side 'New Round' action) will call.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Backend supports resetting a room's state back to LOBBY (or starting a fresh round set) while keeping the same room code and player list
- [x] #2 Player scores are reset for the new round (or explicitly carried over — pick one and document it)
- [x] #3 Lobby screen shows a 'Start New Round' action (host-only) when the room is resettable, not just at first creation
- [x] #4 Existing players stay connected via their existing WebSocket without needing to rejoin
<!-- AC:END -->
