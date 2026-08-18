---
id: TASK-6
title: Late-join and mid-round state reconstruction from room snapshot
status: To Do
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-18 14:43'
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
