---
id: TASK-43
title: 'Hardcore mode: upload the sampled photos blind, no preview'
status: To Do
assignee: []
created_date: '2026-08-22 13:37'
updated_date: '2026-08-22 13:37'
labels:
  - frontend
  - backend
  - gameplay
dependencies:
  - TASK-42
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Hardcore mode is the opt-in high-stakes variant: the player does not get to see which photos were randomly pre-selected from their library before they are shared. It is the current blind behaviour, kept deliberately, while TASK-42 makes preview+reshuffle the default for normal mode.

The host picks the mode in the lobby alongside the other game settings, and it applies to the whole room (a room where some players preview and some do not is not a mode, it is a bug). So the flag has to live on the room, not on each client: add it to the start/create payload and surface it in the room snapshot and the socket events, so every client knows which mode it is in before it samples.

The lobby must show clearly which mode is active before anyone uploads - a player who did not notice they are in hardcore mode and shares something private is exactly the failure this feature must not cause.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Room carries a hardcore flag set by the host when configuring the game,In hardcore mode photos are sampled and uploaded without a preview or reshuffle,In normal mode the TASK-42 preview and reshuffle flow runs,Every client learns the mode from the room snapshot, not from local state,The lobby clearly shows which mode is active before any photo is uploaded
<!-- AC:END -->
