---
id: TASK-59
title: 'Give a guess a cost: confidence and wagering'
status: To Do
assignee: []
created_date: '2026-08-23 11:58'
labels: []
milestone: m-3
dependencies: []
ordinal: 59000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
backend/app/scoring.py is the whole of it: seconds_left times 100 if right, 0 if wrong. There is no decision in that. A player who is certain and a player who is guessing at random play the round identically, and being confidently wrong costs nothing, so nobody is ever nervous.

Add something to decide. The cheapest version is a confidence the player sets with the guess - stake more, win more, lose some if wrong - so the interesting move is knowing when you do not know. It has to stay legible on a ten second timer, which rules out anything with more than about three settings.

The floor matters: a run of bad rounds should not put somebody so far behind that the rest of the game is dead to them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A guess carries a stake, and the stake is bounded and server-validated like every other input
- [ ] #2 A wrong guess at a high stake costs points; the cost is visible before committing
- [ ] #3 A player cannot be driven so far behind that the remaining rounds cannot matter
- [ ] #4 The default stake keeps the current game playable for anybody who ignores the mechanic
- [ ] #5 Scoring stays pure and unit-tested in scoring.py
<!-- AC:END -->
