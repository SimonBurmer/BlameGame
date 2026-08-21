---
id: TASK-26
title: Allow self-voting and improve guess-selection color feedback
status: To Do
assignee: []
created_date: '2026-08-21 23:17'
labels:
  - frontend
  - gameplay
  - ux
milestone: m-0
dependencies: []
priority: medium
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two related UI/UX gaps in the guess screen: (1) the local player is always excluded from the guess candidates (lib/screens/game_screen.dart:318 filters out c.myPlayerId client-side; the backend has no such restriction), so when it's your OWN photo on screen you have no correct option to pick. Allow guessing yourself. (2) Once a guess is made, the selected chip's highlight (added for TASK-1) is a subtle opacity/border change — make the color distinction clearer so it's obvious at a glance who you picked.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Player list includes the local player as a guessable option
- [ ] #2 Guessing yourself is submitted and scored the same way as any other guess (correct if it is genuinely your own photo)
- [ ] #3 The selected player's chip is visually distinct with a clearer color treatment than the current subtle opacity/border change (e.g. filled background in the player's color, not just a thin border)
- [ ] #4 Non-selected chips remain visually de-emphasized as they are today
<!-- AC:END -->
