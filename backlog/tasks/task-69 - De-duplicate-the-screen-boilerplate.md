---
id: TASK-69
title: De-duplicate the screen boilerplate
status: Done
assignee: []
created_date: '2026-08-31 02:16'
updated_date: '2026-08-31 02:30'
labels: []
dependencies: []
ordinal: 69000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The three controller-driven screens each hand-roll the same scaffolding: addListener in initState, removeListener in dispose, an _onChange that guards on mounted and calls setState, and a _navigated latch so a stream event cannot push the same route twice. Getting any of those three wrong is a crash (TASK-46 was exactly this), and right now correctness is copied rather than shared.

Snackbars are the other copy-paste: the lobby has a private _snack helper and the game screen, results screen and preview sheet each spell out ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(...))) inline.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 One mixin owns the listener wiring, the mounted guard and the navigate-once latch, and all three screens use it
- [x] #2 One snackbar helper, used everywhere a screen shows a message
- [x] #3 flutter test and flutter analyze are green and no screen behaviour changed
<!-- AC:END -->
