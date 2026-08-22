---
id: TASK-34
title: GameController is leaked on every back-navigation
status: Done
assignee: []
created_date: '2026-08-22 01:20'
updated_date: '2026-08-22 10:27'
labels:
  - bug
  - flutter
  - leak
milestone: m-0
dependencies: []
priority: high
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
HomeScreen creates the controller but only disposes it on the failure path. The lobby back arrow and BACK TO HOME both pop to Home leaving it alive - socket open, http.Client unclosed, listener registered, still deserializing events. Three games in one session means three live WebSockets, and server-side those sockets stay registered in the room.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The controller is disposed whenever the game flow unwinds to Home
- [x] #2 No WebSocket outlives the screen that owns it
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
HomeScreen now awaits the push and disposes the controller when the flow unwinds, plus disposes on the not-mounted path that previously leaked too.
<!-- SECTION:NOTES:END -->
