---
id: TASK-36
title: Refactor the Flutter client architecture
status: Done
assignee: []
created_date: '2026-08-22 01:21'
updated_date: '2026-08-22 10:29'
labels:
  - refactor
  - flutter
milestone: m-4
dependencies: []
priority: medium
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Senior-Dart pass over the client core: model the joined-room invariant as a GameSession object so the 12 force-unwraps disappear and a half-joined controller is unrepresentable; encapsulate the live player list behind an unmodifiable view; move player cosmetics out of the model layer so models are pure Dart (and fix the colour derivation, which used String.hashCode and therefore differed between VM and web for the same player); extract the duplicated POST-JSON helper in ApiClient and bound every call with a timeout; drop dead code.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 No force-unwraps of room/player identity in the controller
- [x] #2 Live state cannot be mutated from outside the controller
- [x] #3 Models carry no Flutter UI dependency
- [x] #4 Every HTTP call is bounded by a timeout
- [x] #5 flutter analyze clean and all tests pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
GameSession removes all 12 force-unwraps; _players is private behind an UnmodifiableListView (and finalRankings likewise); cosmetics moved to lib/ui/player_cosmetics.dart with a platform-stable hash, so models are pure Dart; ApiClient gained a _postJson helper and a 10s timeout on every call; dead code removed (uploadPhoto, the unread getRoom 'state' field). Also fixed while in here: the in-game score badge read 0 all game because guess_result never updated the roster, and a failed guess left the round permanently locked.
<!-- SECTION:NOTES:END -->
