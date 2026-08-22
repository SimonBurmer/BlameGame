---
id: TASK-20
title: Fill backend HTTP/WS endpoint test gaps
status: In Progress
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 10:42'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Partially done as a side effect of the hardening work. Added: WebSocket accepts a lowercased room code, WebSocket rejects a non-player, oversized upload 413, non-image bytes rejected, per-player photo cap, upload rejected once started, rejected upload leaves no orphan file, room player cap, stale round_index rejected, server-derived seconds_left, and photo fetch-back plus path-traversal regression tests. Backend suite 57 -> 73. Still open: the endpoints listed in the original description that these did not touch.
<!-- SECTION:NOTES:END -->
