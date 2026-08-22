---
id: TASK-42
title: Preview and reshuffle the randomly-picked photos before uploading
status: Done
assignee: []
created_date: '2026-08-22 13:37'
updated_date: '2026-08-22 17:56'
labels:
  - frontend
  - ui
  - privacy
dependencies: []
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Photos are sampled and uploaded blind: _addPhotos() in lobby_screen.dart calls sampleRandomPhotos() and immediately pipes the bytes into c.uploadPhotos(), so a player never sees what they are about to share with the room. A player with something private in their camera roll has no way out except not playing.

Show the sampled photos in a confirmation sheet before upload, with a reshuffle action that re-samples a fresh random set, and only upload on explicit confirm. This is client-side only: nothing reaches the backend until the player confirms, so no API change is needed.

PhotoSampler currently returns List<Uint8List> with no identity, so a reshuffle cannot avoid re-picking the same asset. Return something carrying the asset id (or the AssetEntity) so repeat picks can be excluded and so a thumbnail can be shown without decoding the full-resolution originBytes for the preview grid.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Sampled photos are shown to the player before anything is uploaded
- [x] #2 A reshuffle action re-samples a different random set
- [x] #3 Photos are uploaded only after the player explicitly confirms
- [x] #4 The preview grid uses thumbnails, not full-resolution originBytes
- [x] #5 PhotoSampler exposes per-photo identity so a reshuffle can avoid repeats
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
PhotoSampler now returns SampledPhoto {id, thumbnail, bytes} and takes exclude: Set<String> so a reshuffle skips already-shown assets. Thumbnails come from thumbnailDataWithSize(square(300)) so the preview grid never decodes full-resolution originBytes. _addPhotos() opens a confirmation sheet (3-col grid, RESHUFFLE + USE THESE) and uploads only on explicit confirm - dismissing uploads nothing. Client-side only, no API change. Flutter suite 57 -> 63.

Tests use a fixed-frame settle() helper rather than pumpAndSettle, because the ADD PHOTOS spinner runs while the sheet is open and pumpAndSettle would never return. PR: https://github.com/SimonBurmer/BlameGame/pull/27
<!-- SECTION:NOTES:END -->
