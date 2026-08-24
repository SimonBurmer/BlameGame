---
id: TASK-49
title: round_started leaks the photo owner to every client before anyone guesses
status: Done
assignee: []
created_date: '2026-08-23 10:17'
updated_date: '2026-08-24 11:08'
labels:
  - backend
  - security
  - gameplay
dependencies: []
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
backend/app/timer.py:59 _photo_dict() includes owner_id, and it is broadcast in the round_started event at timer.py:102 - at the START of the round, before any guess is made. Every connected client therefore receives the answer to the round it is about to play.

This is the whole game. Anyone reading the WebSocket frame (browser devtools, a proxy, a modified client) gets a guaranteed correct guess every round, with maximum speed points.

TASK-6 hit this while adding mid-round state to the REST snapshot and deliberately withheld owner_id there while the round is live, matching what round_revealed discloses. But the WebSocket path still leaks it, which makes that care pointless in practice - it was out of TASK-6's scope and is filed here instead.

Fix: withhold owner_id from the round_started payload and only disclose it in round_revealed (which already carries it). Check PhotoInfo on the client - lib/models/game_models.dart parses owner_id and TASK-6 already made PhotoInfo.ownerId nullable, so the client may need no change at all. Verify nothing in the UI depends on it before reveal; the reveal is driven by revealedOwnerId on the controller, not by the photo.

Also grep for any other broadcast that includes the owner before reveal.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 round_started no longer includes the photo owner
- [x] #2 The owner is disclosed only at reveal
- [x] #3 A test asserts the live-round broadcast withholds the owner
<!-- AC:END -->
