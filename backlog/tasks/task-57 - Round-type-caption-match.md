---
id: TASK-57
title: 'Round type: caption match'
status: To Do
assignee: []
created_date: '2026-08-23 11:58'
labels: []
milestone: m-0
dependencies:
  - TASK-53
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A photo goes up and everybody writes a caption for it. Then all the captions appear and the room has to match each one to whoever wrote it.

No metadata, so it works on every photo in the roll, including the screenshots and the saved memes that the date and place rounds have to skip. It is also the first round type where players make the content rather than only choosing from it, which is where this kind of game usually gets funny.

Two phases in one round is new - write, then match - so the round driver has to grow a phase beyond in_round and revealing. Needs a text input path, which means it needs the same length limits and the same treatment of empty and duplicate submissions that names already get.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The round runs a write phase and then a match phase, both server-timed
- [ ] #2 A player who writes nothing is handled without stalling the round
- [ ] #3 Captions are length-capped and cannot be submitted twice by the same player
- [ ] #4 Scoring rewards matching captions to authors, and rewards a caption that fooled the room
- [ ] #5 The reveal shows every caption next to whoever actually wrote it
<!-- AC:END -->
