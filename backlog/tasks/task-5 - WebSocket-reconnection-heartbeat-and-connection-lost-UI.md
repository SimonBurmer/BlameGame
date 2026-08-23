---
id: TASK-5
title: 'WebSocket reconnection, heartbeat, and connection-lost UI'
status: Done
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-23 10:22'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Partially done. The connection-lost UI and manual reconnection landed: the event subscription now has onError/onDone feeding a connectionError field, ConnectionBanner shows on the lobby and game screens with a RETRY that re-seeds from GET /rooms/{code} (events missed while offline are gone, so replaying server state is the only way back in sync). Cancel-before-close ordering means normal teardown does not show a spurious banner. Still open: no heartbeat/ping, and no automatic retry with backoff - the player has to tap RETRY. Mid-round visual state after a reconnect is covered by TASK-6.
<!-- SECTION:NOTES:END -->
