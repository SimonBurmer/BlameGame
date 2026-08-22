---
id: TASK-14
title: Concurrency safety around shared mutable Room state
status: Done
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 13:44'
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
- [x] #1 Concurrent guess and round-advance operations on a room are serialized safely
- [x] #2 No state corruption possible under concurrent access
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Fixed with a `Room.epoch` counter rather than locks. This is asyncio: `game.py` is entirely synchronous, so `submit_guess`, `add_player`, `add_photo`, `start_game` and `reset_room` each run to completion without interleaving. A lock around them would be pure ceremony. The only real windows are where the RoundDriver awaits.

Real races found and fixed (all in `timer.py`):
1. `advance_round()` after the reveal hold was unguarded. The pre-reveal re-check existed; the post-hold one did not. A room that finished and was reset+restarted during the 3s hold got advanced by the previous game`s driver — skipping the new game`s first round, or raising GameError on a FINISHED room and killing the task into the logger.
2. Two drivers on one room. `/reset` + `/start` spawns a second RoundDriver while the first may still be sleeping; both then drove the same room, double-advancing rounds and emitting duplicate `round_started`.
3. Stale driver emitting `game_finished` for a room that had just restarted, dropping every client to the results screen.
4. Stale driver polling out the full remaining round of a game it no longer owns.

`epoch` is bumped by `start_game` and `reset_room`; the driver captures it at construction and re-checks via `_still_ours()` after every await. State/round comparison alone is insufficient — a reset-then-restart looks identical to the round the driver was already on.

Claimed races that are NOT real (no guard added):
- Concurrent `/guess` vs `/guess`: `submit_guess` is sync, so the duplicate-guess check and the `guesses[...]` write cannot interleave.
- Concurrent `/start` vs `/start`: `start_game` is sync and rejects a non-LOBBY room, so the second caller always loses cleanly.
- `/photos` upload: the handler awaits while reading the body, but `add_photo` re-validates room state synchronously afterwards, so the await cannot corrupt anything.
- `everyone_has_guessed` on an emptied `rounds` list: verified it already guards with `if not room.rounds`, so the IndexError I initially guarded against is unreachable. Kept the bail there for the early-exit benefit only, not as a crash fix.

Tests: 4 new in `tests/test_timer.py` that mutate the room inside the injected `sleep` — the injected sleep IS the await point, so this reproduces exactly what a REST handler does mid-drive. Verified red-green: all 4 fail against the unpatched `app/`. Suite 73 -> 77 passing, ruff clean.
<!-- SECTION:NOTES:END -->
