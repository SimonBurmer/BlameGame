---
id: TASK-10
title: Persistent datastore for rooms and game state
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 18:03'
labels:
  - backend
  - infra
  - persistence
milestone: m-2
dependencies: []
priority: low
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
All game state lives in a single process-wide in-memory dict (GameStore singleton). Everything is lost on restart/redeploy and cannot be shared across replicas (railway.json pins numReplicas: 1). Move room/game state to a real datastore (e.g. Redis/Postgres) to enable durability and horizontal scaling.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Room and game state persists across process restarts
- [ ] #2 State is shareable across multiple backend instances
- [ ] #3 The single-replica constraint in railway.json can be lifted
<!-- AC:END -->
