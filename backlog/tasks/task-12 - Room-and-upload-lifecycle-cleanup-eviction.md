---
id: TASK-12
title: Room and upload lifecycle cleanup / eviction
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 13:43'
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
- [x] #1 Finished/abandoned rooms are evicted after a TTL
- [x] #2 A room's photos are cleaned up when the room is evicted
- [x] #3 An endpoint exists to explicitly end/delete a room
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
GameStore now sweeps rooms idle past ROOM_TTL_SECONDS (6h) and deletes their uploads/{code}/ dir via an on_evict hook. Sweep is lazy on create/lookup rather than a background task - only a request can grow the store, so an idle server has nothing to clean. Lookup bumps last_active so a live room never ages out under players. Deletion is tightly scoped: the path is re-derived from the code and refused unless it is a direct child of UPLOAD_DIR. Also adds host-only DELETE /rooms/{code}, broadcasting room_closed before deleting. Backend suite 73 -> 85.

Known ceiling: a fully idle server keeps the last stale rooms in RAM until the next request. Acceptable on a single Railway replica with ephemeral disk. PR: https://github.com/SimonBurmer/BlameGame/pull/26
<!-- SECTION:NOTES:END -->
