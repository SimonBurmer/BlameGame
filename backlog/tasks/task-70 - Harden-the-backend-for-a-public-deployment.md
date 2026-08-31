---
id: TASK-70
title: Harden the backend for a public deployment
status: Done
assignee: []
created_date: '2026-08-31 02:17'
updated_date: '2026-08-31 02:33'
labels: []
dependencies: []
ordinal: 70000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The backend is about to be reachable by anyone with the Railway URL, and its in-memory store has no ceiling: POST /rooms is unauthenticated and unbounded, so a loop creating rooms grows the process until Railway kills it, taking every live game with it. Rooms are only reclaimed by a 6h idle sweep, which is far too slow to be the answer.

Two smaller things in the same area. The __main__ block runs uvicorn with reload=True, which is a development setting sitting in the file that gets deployed. And photo retention is a privacy property nobody has written down: uploads are served to anyone holding the unguessable URL and deleted when the room is evicted, which is the right design but needs stating so it does not get changed by accident.

Also confirm what the client actually uploads. photo_manager's thumbnail pipeline re-encodes through UIImageJPEGRepresentation, which should drop EXIF and with it the GPS coordinates on every camera photo — but 'should' is not good enough for location data, so it needs checking against real bytes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The room store has a hard cap and refuses new rooms past it rather than growing without limit
- [x] #2 The deployed entrypoint has no reload=True
- [x] #3 Uploaded photos are confirmed to carry no EXIF or GPS, with a test that fails if that stops being true
- [x] #4 Photo retention and the unguessable-URL access model are written down where the next change will see them
- [x] #5 pytest and ruff are green
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The EXIF criterion was met by moving the guarantee rather than verifying the assumption. photo_manager's thumbnail re-encode does drop EXIF, but that is one client on one platform — Android, a web client or anything calling the API directly would all bypass it. app/photo_meta.py now strips JPEG APP1-APP15/COM segments and PNG text/eXIf chunks server-side, structurally, with no image library in the trust path for attacker-supplied bytes and no re-encode.

Room cap is 500, swept before the check so an expired store does not read as a flood, and refused with 503 (out of capacity) rather than 429 (rate limited).

reload=True is now opt-in via a RELOAD env var; Railway starts uvicorn itself so the __main__ block is a convenience path only.
<!-- SECTION:NOTES:END -->
