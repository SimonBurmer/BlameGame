---
id: TASK-43
title: 'Hardcore mode: upload the sampled photos blind, no preview'
status: To Do
assignee: []
created_date: '2026-08-22 13:37'
updated_date: '2026-08-22 13:47'
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

The mode applies to the whole room - a room where some players preview and some do not is not a mode, it is a bug - so the flag lives on the Room, not on each client.

It must be set at ROOM CREATION, not on the start call. Photos are sampled and uploaded in the lobby, before the host presses start, so a flag riding along with StartBody arrives after the photos are already on disk. Set-at-creation also closes a hole by construction: if the mode were a mutable lobby setting, a host could flip to hardcore after players had already preview-approved their photos, retroactively breaking the promise that you saw what you shared. Making it mutable would additionally require a settings-changed event and a rule rejecting any toggle after the first upload.

Every client must learn the mode from the room snapshot before it samples; a client that joins before the mode is known must not sample. The lobby must show clearly which mode is active before anyone uploads - a player who did not notice they are in hardcore mode and shares something private is exactly the failure this feature must not cause.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Room carries a hardcore flag set by the host when configuring the game
- [ ] #2 In hardcore mode photos are sampled and uploaded without a preview or reshuffle
- [ ] #3 In normal mode the TASK-42 preview and reshuffle flow runs
- [ ] #4 Every client learns the mode from the room snapshot, not from local state
- [ ] #5 The lobby clearly shows which mode is active before any photo is uploaded
<!-- AC:END -->
