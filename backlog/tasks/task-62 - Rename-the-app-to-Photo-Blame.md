---
id: TASK-62
title: Rename the app to Photo Blame
status: In Progress
assignee: []
created_date: '2026-08-30 15:56'
updated_date: '2026-08-30 16:00'
labels: []
dependencies: []
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The app is being renamed from Blame Game to Photo Blame, with photo-blame.com as the website and hello@photo-blame.com as the contact address. Neither Blame Game nor Photo Roulette should survive anywhere in the product: Photo Roulette is a registered trademark of Photo Roulette AS and is currently still named in CLAUDE.md as the game this one is modelled on, which is the one place the old name was deliberately kept. That sentence has to be rewritten by hand rather than substituted - task-41 learned this the hard way, when a blanket swap turned the description into 'a clone of the Blame Game party game'.

Scope on main: Dart package blame_game, display name 'Blame Game', bundle identifier com.blamegame.app on iOS and Android, the Kotlin package directory android/app/src/main/kotlin/com/blamegame/app/, the four branding SVGs, web/index.html and web/manifest.json, backend, READMEs, scripts and the Backlog project name. Roughly 40 tracked files.

The bundle identifier is the one irreversible piece. task-41 flagged com.blamegame.app as a judgement call because it assumed a domain nobody owned; com.photoblame.app is backed by photo-blame.com, so this is the moment to get it right - it is permanent once the app ships to either store.

Two things sit outside this ticket and need their own passes: the marketing website on feature/task-48-marketing-website, which carries a @blame-game/brand package and its own copy, and the GitHub repository name (currently SimonBurmer/BlameGame), which only the owner can change.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Dart package is photo_blame and every import, app class and MaterialApp title follows; the home screen reads PHOTO BLAME
- [x] #2 iOS and Android carry the display name Photo Blame and the bundle identifier com.photoblame.app, with the Kotlin package directory moved to match
- [x] #3 No occurrence of 'Blame Game' or 'Photo Roulette' survives in code, branding assets, docs, backend or the Backlog project name, outside closed tickets that record history
- [x] #4 photo-blame.com and hello@photo-blame.com are the contact details wherever the app names a website or an address
- [x] #5 flutter analyze is clean, the Flutter and backend suites pass, and the renamed app builds and launches on a simulator
<!-- AC:END -->
