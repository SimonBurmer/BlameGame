---
id: TASK-20
title: Fill backend HTTP/WS endpoint test gaps
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-18 14:43'
labels:
  - backend
  - testing
milestone: m-4
dependencies: []
priority: medium
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Pure logic layers are well tested, but the I/O layer has gaps: POST /guess endpoint + its broadcast, POST /advance, GET photo file-serving, GET /health, photo-upload error paths (missing/invalid owner, unknown room), WS disconnect/dead-socket pruning, and RoundDriver-vs-REST concurrency are untested.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The /guess HTTP endpoint and its guess_result broadcast are tested
- [ ] #2 Photo file-serving and upload error paths are tested
- [ ] #3 WebSocket disconnect / dead-socket pruning is tested
<!-- AC:END -->
