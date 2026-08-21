---
id: TASK-27
title: 'Show points earned immediately after guessing, not only at round reveal'
status: To Do
assignee: []
created_date: '2026-08-21 23:18'
labels:
  - frontend
  - backend
  - gameplay
  - ux
milestone: m-0
dependencies: []
priority: medium
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After tapping a guess, the player gets no feedback until the round timer runs out and GamePhase.revealed fires the existing _resultBanner (lib/screens/game_screen.dart:262, driven by c.lastPointsEarned). Since scoring is time-weighted (backend/app/scoring.py: seconds_left * 100), the score for a correct guess is already knowable the instant the guess is submitted -- there's no reason to make the player wait out the rest of the round to see it. Show an immediate 'you guessed X, +N points' (or correct/incorrect) confirmation right after the tap, as gamification/instant feedback, separate from the existing end-of-round reveal banner that shows everyone the true owner.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Immediately after submitting a guess, the player sees their own result (correct/incorrect and points earned) without waiting for the round to end
- [ ] #2 The existing end-of-round reveal banner (showing the true photo owner to everyone) is unaffected and still appears when the round resolves
- [ ] #3 Guess submission (POST /rooms/{code}/guess) already returns enough info to know correctness and points -- reuse that response instead of adding a new endpoint
<!-- AC:END -->
