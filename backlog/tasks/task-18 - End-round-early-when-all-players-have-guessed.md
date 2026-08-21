---
id: TASK-18
title: End round early when all players have guessed
status: Done
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-21 23:47'
labels:
  - backend
  - gameplay
milestone: m-3
dependencies:
  - TASK-2
priority: low
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rounds always run the full timer even if everyone has already guessed. Add early round-end when all active players have submitted a guess, so the game feels responsive.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A round ends early once every active player has guessed
- [x] #2 Early end is broadcast and clients advance immediately
<!-- AC:END -->
