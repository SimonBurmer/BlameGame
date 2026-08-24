---
id: TASK-5
title: 'WebSocket reconnection, heartbeat, and connection-lost UI'
status: Done
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-23 10:16'
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
- [x] #1 Client auto-reconnects with backoff after a dropped socket
- [x] #2 Heartbeat/ping keeps the connection alive and detects silent drops
- [x] #3 Connection-lost state is surfaced in the UI
- [x] #4 onDone/onError are handled rather than silently ending the stream
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Done. Four layers, all injectable so tests run in milliseconds.

Server: the WS route answers {"type":"ping"} with {"type":"pong"}. This exists because a silently dropped mobile connection delivers no close frame at all - neither onDone nor onError fires - so a missing reply is the only evidence the socket is dead. The frame is JSON-parsed rather than string-compared, and anything unparseable is ignored: a garbage frame must not kill a player's feed.

Heartbeat: GameController runs a Timer.periodic on heartbeatInterval (15s). Each tick pings and clears a _sawFrame flag; a tick that finds the flag still clear declares the socket dead. Any inbound frame counts, so the pong only has to arrive, not to mean anything (it decodes to an UnknownEvent and is discarded). heartbeatInterval: Duration.zero turns it off, which is what widget tests pass - the test framework fails any test ending with a timer pending.

Auto-reconnect: a connection error schedules a retry from the bounded retryBackoff list (1s, 2s, 5s, 10s), each retry calling the existing reconnect(). There is deliberately no second recovery path: reconnect() re-seeds from GET /rooms/{code}, which is the only way back in sync since events missed while offline are gone. The budget resets on a successful reconnect and, once spent, the banner stays up with manual RETRY as the fallback - an endless silent retry loop is worse than a visible failure. isReconnecting drives the banner's 'Reconnecting...' state so RETRY is not offered while a retry is already in flight.

Disposal: both timers are cancelled in dispose() and in _teardownSocket(). GameController defers disposal while a screen still listens (TASK-46), so a surviving heartbeat would leak a timer per game and a surviving retry would call reconnect() on a disposed controller - exactly the 'used after being disposed' crash. Teardown on leave/kick drops the pending retry too, so a timer cannot reconnect us to a room we left.

Tests: 135 backend (pong answered, garbage frame ignored), 93 flutter (heartbeat pings while frames flow, a silent interval kills the socket, a drop reconnects without RETRY, retries are bounded, disposal cancels the pending retry). navigation_disposal_test.dart still passes.
<!-- SECTION:NOTES:END -->
