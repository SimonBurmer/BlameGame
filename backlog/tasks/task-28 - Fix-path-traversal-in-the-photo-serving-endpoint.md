---
id: TASK-28
title: Fix path traversal in the photo-serving endpoint
status: Done
assignee: []
created_date: '2026-08-22 01:19'
updated_date: '2026-08-22 10:27'
labels:
  - security
  - backend
milestone: m-2
dependencies: []
priority: high
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GET /rooms/{code}/photos/{filename} joined both raw path params onto UPLOAD_DIR with no validation, so /rooms/../photos/pyproject.toml returned arbitrary files from the backend working directory (confirmed live: HTTP 200, 541 bytes). Resolve the candidate path and confirm it stays inside UPLOAD_DIR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Requests that escape UPLOAD_DIR return 404
- [x] #2 Legitimate uploaded photos are still served
- [x] #3 A regression test fails against the vulnerable code
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Confirmed exploitable against the running server: GET /rooms/../photos/pyproject.toml returned the file (HTTP 200, 541 bytes). Fixed by resolving the candidate path and requiring it to stay inside UPLOAD_DIR. Regression test verified to fail against the vulnerable code before the fix.
<!-- SECTION:NOTES:END -->
