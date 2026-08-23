---
id: TASK-20
title: Fill backend HTTP/WS endpoint test gaps
status: Done
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-23 10:17'
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
- [x] #1 The /guess HTTP endpoint and its guess_result broadcast are tested
- [x] #2 Photo file-serving and upload error paths are tested
- [x] #3 WebSocket disconnect / dead-socket pruning is tested
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Partially done as a side effect of the hardening work. Added then: WebSocket accepts a lowercased room code, WebSocket rejects a non-player, oversized upload 413, non-image bytes rejected, per-player photo cap, upload rejected once started, rejected upload leaves no orphan file, room player cap, stale round_index rejected, server-derived seconds_left, and photo fetch-back plus path-traversal regression tests. Backend suite 57 -> 73.

Finished here: 19 endpoint tests added to backend/tests/test_api.py, suite 133 -> 152.

AC1 (/guess + guess_result broadcast): guess_result reaches another player's socket; wrong guess scores exactly zero in both response and broadcast; second guess in a round rejected and score unchanged; guess from a non-player 400; unknown room 404; guess before the game starts 400. The two broadcast tests assert server-side via a recorded-broadcast spy as well as through a real socket -- a socket-only assertion turns a missing broadcast into an infinite receive_json() block instead of a failure.

AC2 (photo serving + upload error paths): missing photo 404, unknown room's photos 404, upload to unknown room 404, upload for a player not in the room 400 (and photo_count stays 0), missing owner_id 422, missing file 422, empty file 400 pinned to the 'empty file' detail, non-image content-type 400. Already covered before this ticket, not duplicated: fetch-back round-trip, PNG/JPEG content-type, HEIC rejection, path traversal, 413, magic bytes, per-player cap, post-start rejection, orphan-file cleanup.

AC3 (disconnect / dead-socket pruning): clean disconnect drops both the room and player registry entries; one client leaving keeps the others connected and still receiving; broadcast prunes a socket whose send raises and does not write to it again; a dead peer does not cost live sockets their events. Already covered by TASK-45, not duplicated: close_player pruning on kick, and kick closing every socket a player holds.

Red-green verified (each break restored afterwards; app/ is unchanged in this branch):
- disabled the guess_result broadcast -> 2 failed (both AC1 broadcast tests), 0.39s, no hang
- removed the add_photo owner check -> 2 failed (incl. the new invalid-owner test)
- replaced the WS finally with a dead branch AND disabled broadcast's prune -> 4 failed (all AC3 tests)
- dropped is_file() from the photo route -> 2 failed (both new 404 tests)
- disabled the double-guess guard -> 2 failed (new endpoint test + existing unit test)

Dropped one candidate test: an empty-upload check that passed even with the 'empty file' guard removed (the magic-byte check caught it), so it was rewritten to assert the specific detail message rather than kept as a test that passes against broken code.
<!-- SECTION:NOTES:END -->
