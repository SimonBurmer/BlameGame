---
id: TASK-6
title: Late-join and mid-round state reconstruction from room snapshot
status: In Progress
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-22 10:42'
labels:
  - frontend
  - backend
  - realtime
milestone: m-0
dependencies:
  - TASK-5
priority: medium
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
getRoom returns a 'state' field the controller ignores; it only reads the players list. A player joining an already-started game does not sync into the correct phase, current photo, or round index — it relies purely on subsequent socket events. Seed full game state from the snapshot on join/reconnect.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Room snapshot includes enough state to reconstruct phase, round index, and current photo
- [ ] #2 Client seeds GameController state from the snapshot on join/reconnect
- [ ] #3 A player joining or reconnecting mid-game lands in the correct phase
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Half done. The join race is fixed: the socket now connects before the roster snapshot is fetched and the snapshot is merged into (not assigned over) the live list, so a player who joins during that window is no longer lost permanently. reconnect() re-seeds the roster the same way. Still open: mid-round reconstruction proper - a client that joins or reconnects mid-game gets the roster but not the current photo, round index or deadline, because GET /rooms/{code} does not report them. That needs the snapshot to carry the in-flight round.
<!-- SECTION:NOTES:END -->
