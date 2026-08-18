---
id: TASK-7
title: User accounts and persistent identity
status: To Do
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-18 14:43'
labels:
  - frontend
  - backend
  - auth
milestone: m-1
dependencies: []
priority: medium
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
There is no auth, accounts, or persistent identity — player identity is per-session only (opaque player_id). A full clone needs accounts so players have a stable identity, friends, and history. Also: anyone holding a player_id can act as that player (no ownership verification).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Users can create an account / persistent identity (e.g. anonymous device identity at minimum, or full auth)
- [ ] #2 Identity persists across app launches (shared_preferences or equivalent)
- [ ] #3 Server verifies the caller owns the player_id they act as
<!-- AC:END -->
