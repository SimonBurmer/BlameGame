---
id: TASK-31
title: Game can start with photos from a single player
status: Done
assignee: []
created_date: '2026-08-22 01:20'
updated_date: '2026-08-22 10:27'
labels:
  - bug
  - backend
  - gameplay
milestone: m-0
dependencies: []
priority: high
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
start_game only requires len(room.photos) >= 1 - not one per player, not two distinct owners - and the client's canStart only checks player count. If the host uploads while others are still on the photo-permission dialog, every round shows the host's own photos; the host recognises all of them and wins with a perfect score. The lobby also renders a green check next to every non-host player unconditionally, which reads as 'ready' and actively misleads the host into starting early.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Starting requires photos from at least 2 distinct owners
- [x] #2 The lobby shows real per-player upload state, not a decorative check
- [x] #3 Photo uploads outside the lobby state are rejected
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
start_game requires photos from 2+ distinct owners. Server broadcasts photos_updated with per-player photo_count; the lobby shows a real ready/waiting indicator instead of an always-green tick, and START explains why it is blocked. Uploads outside LOBBY are now rejected.
<!-- SECTION:NOTES:END -->
