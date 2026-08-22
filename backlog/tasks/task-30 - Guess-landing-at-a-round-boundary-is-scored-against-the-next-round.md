---
id: TASK-30
title: Guess landing at a round boundary is scored against the next round
status: Done
assignee: []
created_date: '2026-08-22 01:20'
updated_date: '2026-08-22 10:27'
labels:
  - bug
  - backend
  - gameplay
milestone: m-0
dependencies: []
priority: high
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GuessBody carries no round index, and submit_guess writes into room.rounds[room.current_round]. RoundDriver reveals and advances back-to-back, so a POST /guess in flight across the rollover is recorded against the round the player has not seen. Verified by repro: the guess scores 0 against the next round's photo AND consumes that player's guess slot, so their real guess for the new round is rejected with 'already guessed'. The early-end check then fires one guess early, ending the next round prematurely too.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Guesses carry the round they were made for
- [x] #2 A guess for a stale round is rejected rather than mis-recorded
- [x] #3 The player is not locked out of the new round
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
GuessBody carries an optional round_index; submit_guess rejects a mismatch with 'that round has already ended'. The REVEALING window from TASK-29 closes the same race from the other side.
<!-- SECTION:NOTES:END -->
