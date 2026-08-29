---
id: TASK-53
title: 'Typed rounds: let a round ask a question, not always whose photo'
status: To Do
assignee: []
created_date: '2026-08-23 11:58'
labels: []
milestone: m-0
dependencies: []
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Today a round has exactly one question hard-coded into it: whose photo is this. Round in backend/app/game.py carries a photo and an owner, the round_started event carries a photo URL and a player list, and the client draws one screen. Every other round type in the backlog is blocked behind that.

Give the round a type. The type decides what the server sends, what the client draws, what a submission looks like and how it is scored. Scoring dispatches on it instead of assuming a player id was picked. One round type ships in this task - the existing one - and it should come out looking like one case among several rather than the case everything else is special-cased around.

The other half of the value is the mix: a game that runs five identical rounds is a mechanic, a game that runs five different questions about the same camera roll is a game. The host should be able to pick which types are in play.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Round carries a type, and the existing whose-photo round is one value of it
- [ ] #2 The round_started event carries the type and only the payload that type needs
- [ ] #3 Guess submission and scoring dispatch on the type instead of assuming a picked player id
- [ ] #4 The client renders per type, with an explicit fallback for a type it does not know
- [ ] #5 The host can choose which types are in play; the default is the current behaviour
- [ ] #6 A room with mixed types picks a type per round and never repeats the same one three times running
<!-- AC:END -->
