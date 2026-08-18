---
id: TASK-2
title: Server-authoritative round timer synced to clients
status: To Do
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-18 14:43'
labels:
  - frontend
  - backend
  - core
milestone: m-0
dependencies: []
priority: high
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 10s countdown in game_screen.dart is display-only and hardcoded (duplicated in game_controller default and game_screen const). It does not read the server round_seconds and does nothing on expiry. Make the backend the source of truth for the round clock and have clients render the real remaining time.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Backend broadcasts round start time / duration so clients compute remaining time
- [ ] #2 Client countdown reads the server value instead of the hardcoded 10s
- [ ] #3 roundSeconds is defined in one place, not duplicated
- [ ] #4 Timer expiry triggers a defined behavior (auto-submit no-guess / timeout), not a no-op
<!-- AC:END -->
