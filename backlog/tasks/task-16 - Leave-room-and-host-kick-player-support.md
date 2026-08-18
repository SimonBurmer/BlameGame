---
id: TASK-16
title: Leave-room and host kick-player support
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-18 14:43'
labels:
  - frontend
  - backend
  - gameplay
milestone: m-3
dependencies: []
priority: low
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
There is no leave-room or delete-room endpoint and no kick. Players can't cleanly exit and hosts can't remove someone. Add leave (client + server) and host-only kick.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A player can leave a room and is removed for everyone
- [ ] #2 The host can kick a player
- [ ] #3 Host leaving is handled (reassign host or end room)
<!-- AC:END -->
