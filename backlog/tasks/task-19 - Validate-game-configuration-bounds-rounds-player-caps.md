---
id: TASK-19
title: 'Validate game configuration bounds (rounds, player caps)'
status: Done
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 10:42'
labels:
  - backend
  - gameplay
  - validation
milestone: m-3
dependencies: []
priority: low
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
StartBody.total_rounds has no bounds check (could be 0 or huge). There is no min/max player cap beyond the >=2 start rule. Add sane validation for round count and player limits.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 total_rounds is validated within sane min/max bounds
- [ ] #2 A maximum player cap is enforced on join
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
total_rounds bounded 1-50 and round_seconds 1-120 via Pydantic Field on StartBody, so out-of-range values are a 422 at the boundary rather than a game rule. Room capacity capped at 12 players and photos at 10 per player in game.py. Previously total_rounds=0 was accepted and produced an in_round room with zero rounds, which then 500'd on the first guess (IndexError) and left the room permanently stuck.
<!-- SECTION:NOTES:END -->
