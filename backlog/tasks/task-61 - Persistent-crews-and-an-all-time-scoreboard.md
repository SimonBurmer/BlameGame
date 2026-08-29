---
id: TASK-61
title: Persistent crews and an all-time scoreboard
status: To Do
assignee: []
created_date: '2026-08-23 11:58'
labels: []
milestone: m-1
dependencies:
  - TASK-7
ordinal: 61000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A room code is thrown away the moment the game ends, so every session starts from nothing and the same group of friends has no record that they have played eleven times. There is no reason to come back beyond remembering that it was fun.

A named crew with a scoreboard that survives the room turns a party trick into something with a standing question attached: who actually knows this group best. That question is worth reopening the app for, and it is the only thing on this list that gives the game a reason to exist between parties.

Depends on there being an identity that outlives a room, which is TASK-7. It also cuts against the current promise that nothing is kept, so the deal has to be explicit and opt-in: a crew keeps scores, never photos, and can be deleted by anybody in it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A group of players can form a named crew that outlives the room
- [ ] #2 Scores accumulate across sessions and are shown as a standing table
- [ ] #3 Joining a crew is opt-in and a crew stores scores, never photos
- [ ] #4 Any member can leave, and leaving removes their history
- [ ] #5 A crew can be deleted outright by any member
- [ ] #6 The privacy section of the website is updated to say what a crew keeps
<!-- AC:END -->
