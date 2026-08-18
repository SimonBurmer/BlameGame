---
id: TASK-1
title: Implement real photo-roulette mechanic (auto-sample device camera roll)
status: To Do
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-18 14:43'
labels:
  - frontend
  - core
  - photos
milestone: m-0
dependencies: []
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The defining feature of Photo Roulette is missing. Currently players manually pick and upload ONE photo via image_picker. The real game randomly samples multiple recent photos from each player's camera roll and mixes them into the round pool. Add a photo_manager/photo_gallery based enumeration, request photo-library permission, randomly sample N photos, and batch-upload them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Photo-library permission is requested with an explicit permission flow (permission_handler)
- [ ] #2 App enumerates the device camera roll and randomly samples N photos (configurable)
- [ ] #3 Sampled photos are batch-uploaded to the room for the local player
- [ ] #4 Manual single-pick upload is replaced or supplemented by the auto-sample flow
<!-- AC:END -->
