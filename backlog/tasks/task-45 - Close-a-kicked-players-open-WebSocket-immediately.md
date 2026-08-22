---
id: TASK-45
title: Close a kicked player's open WebSocket immediately
status: Done
assignee: []
created_date: '2026-08-22 15:34'
updated_date: '2026-08-22 22:36'
labels:
  - backend
  - security
  - realtime
dependencies: []
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-16 added leave/kick, but a kicked player's ALREADY-OPEN WebSocket stays connected until they next interact. The /ws route gates membership at connect time so they cannot reconnect, and the Flutter client tears down on player_left - but a hostile or modified client that simply ignores the event keeps receiving the room feed, which carries every photo URL.

This is a privacy hole, not just tidiness: kicking someone is exactly the moment you want them to stop seeing other people's photos, and today the guarantee depends on the kicked client cooperating.

Closing it needs ConnectionManager (backend/app/connection.py) to map player_id -> socket, which it does not today - it only tracks sockets per room. The TASK-16 agent started that plumbing twice and backed it out rather than ship a half-measure that reads as protection without being it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Kicking a player closes their open socket server-side, not just on client cooperation
- [x] #2 A client that ignores player_left stops receiving the room feed
- [x] #3 ConnectionManager can address a single player's socket
- [x] #4 Kicking a player closes their open socket server-side, not just on client cooperation
- [x] #5 A client that ignores player_left stops receiving the room feed
<!-- AC:END -->
