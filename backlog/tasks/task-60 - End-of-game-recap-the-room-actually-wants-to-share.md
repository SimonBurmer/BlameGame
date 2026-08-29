---
id: TASK-60
title: End-of-game recap the room actually wants to share
status: To Do
assignee: []
created_date: '2026-08-23 11:58'
labels: []
milestone: m-3
dependencies: []
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The leaderboard lands and the whole evening evaporates. There is no recap, and the most repeatable moment of the night - the photo nobody guessed, the person who fooled four people, the one everybody blamed for everything - is sitting on the server as data that is then deleted with the room.

Compute the superlatives that are already implied by the guesses and show them after the leaderboard, then let the room save or share the card. That is the only part of this game that markets itself, and it costs one pass over data that already exists.

It runs straight into the deletion promise, so it has to be built to keep it: the card is generated while the room is alive, it belongs to the players and not to us, and nothing survives the room in order to produce it later.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Superlatives are derived from guesses already recorded, with no new tracking
- [ ] #2 The recap appears after the leaderboard and names specific rounds and people
- [ ] #3 A superlative with no honest winner is omitted rather than awarded to nobody
- [ ] #4 The card can be saved or shared from the device
- [ ] #5 Nothing is retained past room deletion in order to build it
<!-- AC:END -->
