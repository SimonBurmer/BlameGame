---
id: TASK-41
title: Rename the app to Blame Game
status: Done
assignee: []
created_date: '2026-08-22 11:46'
updated_date: '2026-08-22 11:47'
labels: []
dependencies: []
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The app carries Flutter's scaffolding identity (flutter_application_1, 'Flutter Application 1', com.example.flutterApplication1) and its working title, Photo Roulette, which is a real shipping app this one is modelled on. Rename it to Blame Game across every platform and take the placeholder bundle identifier with it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Dart package, app class and MaterialApp title are Blame Game; the home screen reads BLAME GAME
- [x] #2 iOS, Android, web, macOS, Linux and Windows all carry the display name and the new bundle identifier
- [x] #3 Backend, README and project docs no longer refer to Photo Roulette except where naming the game this one is modelled on
- [x] #4 flutter analyze is clean and the whole test suite passes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Names now in use: Dart package blame_game, display name 'Blame Game', bundle identifier com.blamegame.app (was the com.example placeholder on every platform).

Bundle identifier is a judgement call worth revisiting before any store submission - it is permanent once shipped, and com.blamegame.app assumes a domain nobody has registered. Changing it now is one pass of the same sed.

Two sentences had to be rewritten by hand rather than swapped: README.md and .claude/CLAUDE.md both described the app by reference to Photo Roulette, so a blanket substitution turned them into 'a clone of the Blame Game party game'. CLAUDE.md now reads 'a party game in the mould of Photo Roulette', which is the accurate statement and the one place the old name is still wanted.

Closed backlog tickets (task-1, task-8) still say Photo Roulette in their descriptions. Left alone deliberately: they record what was written at the time.

Verified: flutter analyze clean, 57 tests pass, flutter build ios --simulator produces com.blamegame.app with CFBundleDisplayName 'Blame Game', and the app was installed and launched on a simulator - home screen reads BLAME GAME.
<!-- SECTION:NOTES:END -->
