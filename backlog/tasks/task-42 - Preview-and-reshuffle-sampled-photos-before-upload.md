---
id: TASK-42
title: Preview and reshuffle sampled photos before upload
status: In Progress
assignee: []
created_date: '2026-08-22 13:41'
updated_date: '2026-08-22 13:41'
labels: []
dependencies: []
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Photos are sampled and uploaded blind in _addPhotos(); the player never sees what leaves their device. Add a preview + reshuffle confirmation step before upload. Client-side only.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Sampled photos are previewed before any upload
- [x] #2 Reshuffle offers a fresh batch, avoiding photos already shown
- [x] #3 The preview grid renders thumbnails, not full-resolution originBytes
- [x] #4 Dismissing the preview uploads nothing
<!-- AC:END -->
