---
id: TASK-44
title: Accept HEIC uploads (iOS shoots HEIC by default)
status: In Progress
assignee: []
created_date: '2026-08-22 13:45'
updated_date: '2026-08-22 18:06'
labels:
  - backend
  - frontend
  - ios
dependencies: []
priority: high
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
- [x] #1 The server only accepts formats it can actually serve back
- [x] #2 The behaviour is covered by a test using real HEIC magic bytes
- [x] #3 A HEIC original from an iOS camera roll can be contributed successfully
- [x] #4 The server only accepts formats it can actually serve back
- [x] #5 The behaviour is covered by a test using real HEIC magic bytes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
HEIC does reach the server today. Checked photo_manager 3.12.0 sources: on iOS AssetEntity.getOriginBytes has no native handler at all (only Android SDK>29 and OHOS), so it falls through to originFile -> getFullFile(isOrigin: true) -> PMManager.fetchOriginImageFile. That path explicitly treats public.heic/public.heif as fetchable raster and the comment on fallbackFetchImageDataFor states it "writes the raw image bytes verbatim, so there is no JPEG recompression". No transcode - HEIC originals were being uploaded and 400ed.

Fix is client-side and one line: sample the upload bytes via thumbnailDataWithSize(2048) instead of originBytes. photo_manager thumbnails default to ThumbnailFormat.jpeg (PMImageUtil -> UIImageJPEGRepresentation on iOS), so this is a free HEIC->JPEG transcode with no new dependency and no server-side decoder. 2048px is above any phone screen the photo is shown on and keeps uploads under the 8 MB cap.

Server allowlist deliberately unchanged - it still only accepts what the Flutter client can decode when the photo is served back. Added backend/tests/test_api.py::test_heic_upload_is_rejected with real ftypheic ISO-BMFF magic bytes to pin that.

ACs #4/#5 are verbatim duplicates of #1/#2.
<!-- SECTION:NOTES:END -->
