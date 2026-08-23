---
id: TASK-6
title: Late-join and mid-round state reconstruction from room snapshot
status: In Progress
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-23 10:15'
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
- [x] #1 Room snapshot includes enough state to reconstruct phase, round index, and current photo
- [x] #2 Client seeds GameController state from the snapshot on join/reconnect
- [x] #3 A player joining or reconnecting mid-game lands in the correct phase
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Done. `GET /rooms/{code}` now carries the in-flight round whenever the room is not in the lobby, and `GameController._applySnapshot` seeds phase, round index, current photo, deadline and hasGuessedThisRound from it — on both join and reconnect(). A player who joins or drops mid-game lands in the phase the room is actually in instead of sitting in the lobby until the next socket event.

The round block reports `index`, `photo`, `ends_at` and `has_guessed`:
- The photo's `owner_id` is withheld while the round is live and only included once revealed. The owner is the answer players are guessing, so leaking it in the snapshot would hand a reconnecting client a free correct guess. `round_revealed` remains the first thing that discloses it.
- `ends_at` is epoch-ms, the same units and the same server authority as `round_started`; the client derives remaining time as `ends_at - now()` rather than being handed a tamperable countdown.
- `has_guessed` is scoped to the optional `?player_id=` query param, so a reconnector is not offered a guess they already spent. The param grants nothing — an absent or bogus id just means no per-player detail.
- `PhotoInfo.ownerId` is nullable for the same reason. Nothing in the UI read it (the reveal comes from `revealedOwnerId`), so no placeholder was needed.
- The `finished` phase reconstructs the leaderboard by sorting the roster the snapshot already carries; there is no separate results payload to wait for.

The earlier session left the backend half of this as WIP commit 156c94c, which was missing the `RoomState` import; that is fixed here.

Also fixed by the earlier half of this ticket: the join race — the socket connects before the roster snapshot is fetched, and the snapshot is merged into (not assigned over) the live list, so a player joining in that window is no longer lost.

Known gap, out of scope: the `round_started` WebSocket event still includes `owner_id`, which is a separate pre-existing leak with its own blast radius (it would need a client that reads the raw frame). Worth its own ticket.
<!-- SECTION:NOTES:END -->
