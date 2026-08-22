---
id: TASK-44
title: Accept HEIC uploads (iOS shoots HEIC by default)
status: To Do
assignee: []
created_date: '2026-08-22 13:45'
updated_date: '2026-08-22 13:47'
labels:
  - backend
  - frontend
  - ios
dependencies: []
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The upload endpoint allowlists JPEG and PNG by magic bytes and rejects everything else. iOS cameras shoot HEIC by default, so a player whose camera roll is untouched HEIC originals can have photos silently rejected at upload time.

TASK-13 fixed the extension/content-type handling for the formats already accepted, but deliberately did not widen the allowlist - HEIC needs either a transcode to JPEG on upload or a decoder on the client, which is a different piece of work.

Check first whether photo_manager's originBytes already hands back a transcoded JPEG on iOS; if it does, this may only need a test proving it, not a transcoder. Do not widen the magic-byte allowlist without also being able to decode what is let in.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The server only accepts formats it can actually serve back
- [ ] #2 The behaviour is covered by a test using real HEIC magic bytes
- [ ] #3 A HEIC original from an iOS camera roll can be contributed successfully
- [ ] #4 The server only accepts formats it can actually serve back
- [ ] #5 The behaviour is covered by a test using real HEIC magic bytes
<!-- AC:END -->
