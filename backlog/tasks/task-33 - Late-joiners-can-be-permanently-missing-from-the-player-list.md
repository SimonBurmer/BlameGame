---
id: TASK-33
title: Late joiners can be permanently missing from the player list
status: Done
assignee: []
created_date: '2026-08-22 01:20'
updated_date: '2026-08-22 10:29'
labels:
  - bug
  - flutter
milestone: m-0
dependencies: []
priority: high
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GameController._join fetches the roster snapshot and only then opens the socket. A player joining inside that window is in nobody's snapshot and their player_joined broadcast goes to a socket list that does not yet include the new client. Two friends tapping JOIN in the same second can each miss the other for the whole game - their guess buttons never contain that player, so every round showing that person's photo is an automatic zero. Nothing re-syncs the roster during a game.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Connecting and snapshotting cannot interleave to drop a player
- [x] #2 The roster converges even if events and snapshot race
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The socket now connects before the roster snapshot is fetched, and the snapshot is merged into (not assigned over) the live list: the snapshot wins for players in both, and anyone learned only from an event that raced it is kept. A failed snapshot tears the socket down and clears the session so no half-joined controller survives. Covered by a regression test that emits player_joined while the snapshot request is in flight.
<!-- SECTION:NOTES:END -->
