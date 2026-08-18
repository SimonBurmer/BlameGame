---
id: TASK-11
title: Durable photo storage (object storage instead of ephemeral disk)
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-18 14:43'
labels:
  - backend
  - infra
  - photos
milestone: m-2
dependencies: []
priority: medium
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Uploaded photos are written to local disk (uploads/{code}/{id}.jpg). Railway's filesystem is ephemeral, so photos vanish on redeploy. Uploads are also unbounded in size and read fully into memory. Move to object storage (e.g. S3/GCS) with size limits.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Photos are stored in durable object storage, not ephemeral local disk
- [ ] #2 Upload size is limited and enforced
- [ ] #3 Photos survive a redeploy
<!-- AC:END -->
