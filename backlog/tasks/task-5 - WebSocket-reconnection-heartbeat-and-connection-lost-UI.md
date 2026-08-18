---
id: TASK-5
title: 'WebSocket reconnection, heartbeat, and connection-lost UI'
status: To Do
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-18 14:43'
labels:
  - frontend
  - backend
  - realtime
milestone: m-0
dependencies: []
priority: high
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GameSocket (game_socket.dart) has no reconnect logic, no onDone/onError handling, and no heartbeat/ping. A dropped socket silently ends the game feed with no user feedback. Backend WS is also receive-only and doesn't track players per connection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Client auto-reconnects with backoff after a dropped socket
- [ ] #2 Heartbeat/ping keeps the connection alive and detects silent drops
- [ ] #3 Connection-lost state is surfaced in the UI
- [ ] #4 onDone/onError are handled rather than silently ending the stream
<!-- AC:END -->
