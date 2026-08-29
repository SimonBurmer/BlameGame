---
id: TASK-54
title: Keep the date and place a photo already carries
status: To Do
assignee: []
created_date: '2026-08-23 11:58'
labels: []
milestone: m-0
dependencies: []
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
lib/services/photo_sampler.dart works with photo_manager AssetEntity objects. Those carry createDateTime and coordinates, and both are thrown away - the sampler only ever reads thumbnailDataWithSize. That is the material every metadata round type needs, already in hand and currently discarded.

Read them at sample time and send them with the upload. Send the answer, never the raw EXIF: a year and a coarse place, resolved on the device, not a lat/long pair and not an embedded EXIF block. The server needs to be able to mark a guess right or wrong and nothing more, and that is a much easier thing to defend on the privacy page than a location column would be.

Photos that have no date or no location are normal - screenshots, saved images, anything sent over a messenger. They have to be usable for the round types that do not need metadata, and skipped for the ones that do.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The sampler reads createDateTime and coordinates from AssetEntity where present
- [ ] #2 Coordinates are resolved to a coarse place on the device; no raw coordinates and no EXIF block leave the phone
- [ ] #3 The upload carries the derived answer, and the server stores nothing finer than it needs to mark a guess
- [ ] #4 Photos with no date or no place are accepted and are simply not eligible for the round types that need them
- [ ] #5 A room refuses to start a metadata round type when too few photos carry that metadata
- [ ] #6 The privacy section of the website is updated to say what is derived and what is stored
<!-- AC:END -->
