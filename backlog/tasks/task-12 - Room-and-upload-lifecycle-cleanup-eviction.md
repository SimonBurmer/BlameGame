---
id: TASK-12
title: Room and upload lifecycle cleanup / eviction
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-18 14:43'
labels:
  - backend
  - infra
milestone: m-2
dependencies: []
priority: medium
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rooms and their upload directories accumulate forever — no cleanup or eviction. Memory and disk leak over uptime (uploads/ already has 9 leftover room folders). Add TTL-based eviction of finished/abandoned rooms and their photos, plus a way to end/delete a room.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Finished/abandoned rooms are evicted after a TTL
- [ ] #2 A room's photos are cleaned up when the room is evicted
- [ ] #3 An endpoint exists to explicitly end/delete a room
<!-- AC:END -->
