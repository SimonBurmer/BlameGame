---
id: TASK-47
title: 'Host game settings in the lobby (rounds, round length, hardcore mode)'
status: In Progress
assignee: []
created_date: '2026-08-22 18:07'
updated_date: '2026-08-22 22:43'
labels:
  - frontend
  - backend
  - ui
  - gameplay
dependencies:
  - TASK-43
ordinal: 47000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The host currently has no settings UI. startGame() is called with hardcoded totalRounds: 5, roundSeconds: 10 in lobby_screen.dart, and TASK-43 puts the hardcore toggle on the HOME screen at room creation. The host should configure the game from the lobby instead, in one place.

Give the host a settings panel in the lobby covering number of rounds, round length, and hardcore mode. Non-host players see the current settings read-only, so everyone knows what they are about to play.

IMPORTANT constraint on hardcore, do not regress it: TASK-43 deliberately fixes the hardcore flag at room creation because photos are contributed in the lobby, and a host who could flip to hardcore after players had already preview-approved their photos would retroactively break the promise that you saw what you shared. So hardcore must be editable in the lobby ONLY while no photos have been uploaded yet, and must lock as soon as the first upload lands. Rounds and round length have no such constraint and stay editable until start.

The backend must enforce the lock, not just the UI - a client can post whatever it likes. Settings changes need to reach every client (a settings-changed broadcast or the existing snapshot), since non-hosts must see them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Host can set rounds and round length from the lobby instead of hardcoded values
- [x] #2 Host can toggle hardcore mode in the lobby while no photos have been uploaded
- [x] #3 Hardcore mode locks server-side once the first photo is uploaded
- [x] #4 Non-host players see the current settings read-only
- [x] #5 Settings changes are broadcast to every client in the room
- [x] #6 The hardcore toggle is removed from the home screen, not duplicated
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hardcore moved entirely to the lobby: the home-screen Switch and its explanatory text are gone. One obvious place to set it. Rooms are created non-hardcore (POST /rooms still accepts a hardcore body for API compat, but the client no longer sends it) and the host turns it on in the lobby while zero photos exist.

Settings ride a new settings_updated broadcast rather than the room snapshot -- there was no snapshot event to reuse, only the REST GET.

Backend enforces the hardcore lock in game.set_settings: a *change* is rejected once room.photos is non-empty (restating the current value is fine, so a full-settings post from a client isn't spuriously refused). Rounds/round length stay editable until start. POST /rooms/{code}/start now defaults to the room's configured settings.
<!-- SECTION:NOTES:END -->
