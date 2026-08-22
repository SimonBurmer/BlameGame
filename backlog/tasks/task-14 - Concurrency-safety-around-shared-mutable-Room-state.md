---
id: TASK-14
title: Concurrency safety around shared mutable Room state
status: Done
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 17:56'
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
No lock added - a lock would be ceremony here. game.py is fully synchronous (submit_guess, add_player, add_photo, start_game, reset_room never await), so under asyncio each runs to completion and cannot interleave. The only real interleaving windows are the RoundDriver's awaits.

Four real bugs found and fixed, all in timer.py:
1. advance_round() after the reveal hold was unguarded (the pre-reveal re-check existed, the post-hold one did not) - a room reset+restarted during the 3s hold got advanced by the previous game's driver.
2. /reset + /start spawned a second driver while the first was still sleeping: double-advance and duplicate round_started.
3. A stale driver emitted game_finished for a freshly-restarted game, dropping every client to the results screen.
4. A stale driver polled out the full remaining round of a game it no longer owned.

Fix is one monotonic Room.epoch bumped by start_game/reset_room; the driver captures it at construction and re-checks via _still_ours() after every await. A state/round comparison alone is insufficient because a reset-then-restart looks identical to the round the driver was already on.

Claimed races that are NOT real, deliberately left unguarded: concurrent /guess vs /guess, /start vs /start (both synchronous, second caller loses cleanly), and /photos (add_photo re-validates state synchronously after the body read). everyone_has_guessed already guards empty rounds, so the IndexError it was supposed to have is unreachable.

Backend suite 73 -> 77. Red-green verified independently by the orchestrator: reverting models.py/game.py/timer.py to main fails exactly the 4 new tests. PR: https://github.com/SimonBurmer/BlameGame/pull/28
<!-- SECTION:NOTES:END -->
