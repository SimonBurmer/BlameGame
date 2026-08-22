---
id: TASK-29
title: Round reveal is never visible to players
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
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
RoundDriver emits round_revealed then immediately calls advance_round and emits round_started in the same tick - measured 0ms apart. The client sets phase=revealed then phase=inRound in one event batch, so the reveal banner ('It was Anna's photo') and the wrong-answer shake render for zero frames. Players never learn whose photo it was, which is the point of the game. Needs a reveal pause between the reveal event and advancing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 round_revealed is followed by a visible pause before the next round starts
- [x] #2 The reveal banner and shake animation are actually seen by players
- [x] #3 The final round's reveal is visible before navigating to results
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
RoundDriver now holds REVEAL_SECONDS (3s) between round_revealed and advance_round, and sets RoomState.REVEALING for that window so a late guess can't land in the next round. Verified end-to-end against the live server: reveal at t=3.02s, next round at t=6.03s (was 0ms apart). REVEALING was previously a dead enum member.
<!-- SECTION:NOTES:END -->
