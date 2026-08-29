---
id: TASK-56
title: 'Round type: where was this taken'
status: To Do
assignee: []
created_date: '2026-08-23 11:58'
labels: []
milestone: m-0
dependencies:
  - TASK-53
  - TASK-54
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A photo goes up and everybody guesses roughly where it was taken.

The interesting design question is the answer space, and it should be coarse on purpose: a country, or a city for photos taken close to home, picked from a short list rather than dropped on a world map. Coarse is easier to score, easier to play on a phone, and it is the only version of this that is defensible next to the promise that the app does not keep anybody's location.

Depends on TASK-54 having resolved the place on the device, so that neither the server nor the other players ever see a coordinate.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The round takes a coarse place from a short list of options, not a map pin
- [ ] #2 The options are generated so that the wrong ones are plausible
- [ ] #3 No coordinate is sent to the server or to any other player at any point
- [ ] #4 The reveal names the place without narrowing it further than the round asked
- [ ] #5 The round is not offered when too few photos carry a place
<!-- AC:END -->
