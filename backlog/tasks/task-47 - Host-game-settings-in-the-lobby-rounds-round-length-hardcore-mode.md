---
id: TASK-47
title: 'Host game settings in the lobby (rounds, round length, hardcore mode)'
status: To Do
assignee: []
created_date: '2026-08-22 18:07'
updated_date: '2026-08-22 22:44'
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
The host currently has no settings UI. startGame() is called with hardcoded totalRounds: 5, roundSeconds: 10 in lobby_screen.dart, and TASK-43 put the hardcore toggle on the HOME screen at room creation. Move all of it into one lobby settings panel: rounds, round length, and hardcore mode.

The hardcore toggle must be REMOVED from the home screen entirely, not duplicated. One obvious place to set it beats two.

Non-host players see the current settings read-only, so everyone knows what they are about to play.

IMPORTANT constraint on hardcore, do not regress it: TASK-43 deliberately fixed the hardcore flag at room creation because photos are contributed in the lobby, and a host who could flip to hardcore after players had already preview-approved their photos would retroactively break the promise that you saw what you shared. So hardcore must be editable in the lobby ONLY while no photos have been uploaded yet, and must lock as soon as the first upload lands. Rounds and round length have no such constraint and stay editable until start.

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
Hardcore moved ENTIRELY to the lobby: the home-screen Switch and its copy are deleted, not kept as an initial value (verified - zero hardcore references left in home_screen.dart). POST /rooms still accepts a hardcore body for API compat but the client never sends it.

Backend: new game.set_settings() holds the rule - a hardcore CHANGE is refused once room.photos is non-empty, while restating the unchanged value is allowed; rounds/round length stay editable until start; nothing is editable outside the lobby. POST /rooms/{code}/settings is host-only (403 otherwise) and broadcasts settings_updated. Room gains total_rounds so a lobby room reports its configured count before rounds exist.

Frontend: SettingsUpdated event in the sealed hierarchy; ApiClient.updateSettings sends only changed fields; startGame() defaults to room settings instead of 5/10. Lobby panel gives the host steppers (rounds 1-20, seconds 5-60) plus the hardcore switch; non-hosts see the same values read-only. The switch disables with 'Locked - photos have already been added' once anyone uploads.

Backend 125 -> 133, Flutter 83 -> 86. Verified independently by the orchestrator on the branch: 133 backend passed, 86 flutter passed, analyze clean, and the server-side lock reviewed by hand.

Known minor: the stepper posts one request per tap, so holding '+' fires a request each time. Fine at this scale; debounce in _setSetting if it ever matters. PR: https://github.com/SimonBurmer/BlameGame/pull/39
<!-- SECTION:NOTES:END -->
