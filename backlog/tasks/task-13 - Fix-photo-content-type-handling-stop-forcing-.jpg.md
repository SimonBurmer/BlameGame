---
id: TASK-13
title: Fix photo content-type handling (stop forcing .jpg)
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-18 14:43'
labels:
  - frontend
  - backend
  - photos
  - bug
milestone: m-2
dependencies: []
priority: low
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Backend always writes uploads as .jpg regardless of real format (main.py), and the Flutter ApiClient hardcodes image/jpeg MediaType regardless of the picked file. Non-JPEG uploads are mislabeled/corrupted. Detect and preserve the real content type end to end.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Client sends the correct content-type for the picked file
- [ ] #2 Server stores files with the correct extension/type
- [ ] #3 PNG/HEIC and other common formats round-trip correctly
<!-- AC:END -->
