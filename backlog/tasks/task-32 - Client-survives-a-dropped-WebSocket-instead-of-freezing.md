---
id: TASK-32
title: Client survives a dropped WebSocket instead of freezing
status: Done
assignee: []
created_date: '2026-08-22 01:20'
updated_date: '2026-08-22 10:27'
labels:
  - bug
  - flutter
  - resilience
milestone: m-0
dependencies: []
priority: high
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The event subscription has no onError/onDone and nothing reconnects. Backgrounding the app for ~30s or a network handover leaves the player frozen on the old photo with the timer at 0 and every guess button greyed, forever, with no error shown and no way out but killing the app. Lobby has the same failure: 'Waiting for the host' forever, and rejoining is impossible because the name is taken.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A dropped connection surfaces in the UI instead of failing silently
- [x] #2 The player can retry and re-sync from the server snapshot
- [x] #3 Normal teardown does not show a spurious connection error
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Subscription now has onError/onDone feeding a connectionError field; ConnectionBanner offers RETRY, which re-seeds from the server snapshot (events missed while offline are gone). Cancel-before-close ordering means normal teardown does not show a spurious banner.
<!-- SECTION:NOTES:END -->
