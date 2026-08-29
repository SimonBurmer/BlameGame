---
id: TASK-58
title: 'Round type: guess the room, not the truth'
status: To Do
assignee: []
created_date: '2026-08-23 11:58'
labels: []
milestone: m-0
dependencies:
  - TASK-53
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Same photo, same list of people, one word changed in the question: not whose photo is this, but who will everybody else say.

Points for matching the majority rather than for being right. It inverts the whole game - the player who knows the group best beats the player who knows the truth - and it costs almost nothing to build on top of the existing round, because the submission is identical and only the scoring changes.

Worth being careful about the reveal: it has to show the split, because the split is the joke. Seeing that four people blamed the same person and were all wrong is the moment worth staying for.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Scoring rewards agreement with the majority answer rather than the true owner
- [ ] #2 The true owner is still revealed, so the round has both an answer and a verdict
- [ ] #3 The reveal shows how the room split, not just who was right
- [ ] #4 A tie for the majority answer resolves deterministically and is explained on screen
<!-- AC:END -->
