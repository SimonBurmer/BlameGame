---
id: TASK-68
title: Delete the CocoaPods leftovers and the stale build junk
status: Done
assignee: []
created_date: '2026-08-31 02:16'
updated_date: '2026-08-31 02:23'
labels: []
dependencies: []
ordinal: 68000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-25 moved iOS plugin linking to Swift Package Manager and CLAUDE.md says flatly that 'there is no ios/Podfile'. There is: ios/Podfile and ios/Podfile.lock are still tracked, and an ios/Pods directory sits untracked on disk. They are dead weight that will mislead the next person setting up a machine, and a stray 'pod install' would fight SPM.

On disk, untracked but real: apps/ is 72 MB of orphaned website build output whose sources live only on the website branch, backend/uploads holds 83 MB of real photos from local test games, and backend/photo_roulette_backend.egg-info is named after a package that no longer exists.

SIMONS.md is a third copy of the same command list already in README.md and CLAUDE.md, and it has drifted: it documents 'uvicorn --reload -port 8001' (a typo, and the wrong port).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The Podfile, Podfile.lock and Pods directory are gone and an iOS build still links every plugin through SPM
- [x] #2 The orphaned apps/ output, the test-game uploads and the stale egg-info are gone from the working tree, and .gitignore keeps them out
- [x] #3 There is one place that lists the dev commands, and it is correct
<!-- AC:END -->
