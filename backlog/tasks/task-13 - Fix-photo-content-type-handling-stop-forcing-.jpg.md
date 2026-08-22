---
id: TASK-13
title: Fix photo content-type handling (stop forcing .jpg)
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-22 13:42'
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
- [x] #1 Client sends the correct content-type for the picked file
- [x] #2 Server stores files with the correct extension/type
- [ ] #3 PNG/HEIC and other common formats round-trip correctly
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
JPEG/PNG now round-trip with their real extension and content-type: the upload magic-byte sniff picks the extension, so the stored file, the photo URL and FileResponse's inferred content-type all agree. Client sends the real subtype too instead of hardcoding image/jpeg.

AC#3 is only partly met and stays open: HEIC is NOT covered. The server allowlist is JPEG/PNG by magic bytes and never accepted HEIC, so 'other common formats' would need transcoding (iOS shoots HEIC by default, so this is a real gap worth its own ticket). PR: https://github.com/SimonBurmer/BlameGame/pull/25
<!-- SECTION:NOTES:END -->
