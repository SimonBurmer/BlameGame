---
id: TASK-55
title: 'Round type: when was this taken'
status: To Do
assignee: []
created_date: '2026-08-23 11:58'
labels: []
milestone: m-0
dependencies:
  - TASK-53
  - TASK-54
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A photo goes up and everybody guesses the year. Closest wins.

This is the first round type that cannot be scored by comparing two ids, so it is where proximity scoring has to exist: full points for the exact year, less as you get further away, and speed still counting for something. Being one year out should feel close; being eight years out should not.

It is also the round type that makes the oldest thing in somebody's camera roll worth having, which is a different feeling from the base game and a good reason to contribute more than the minimum.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The round shows a photo and takes a year rather than a player
- [ ] #2 Scoring is by distance from the true year, not right or wrong, and stays server-authoritative
- [ ] #3 Ties and equal distances resolve deterministically
- [ ] #4 The reveal shows the true year and how far each player was from it
- [ ] #5 The round is not offered when too few photos carry a date
<!-- AC:END -->
