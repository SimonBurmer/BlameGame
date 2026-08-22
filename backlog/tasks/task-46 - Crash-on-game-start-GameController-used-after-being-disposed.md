---
id: TASK-46
title: 'Crash on game start: GameController used after being disposed'
status: In Progress
assignee: []
created_date: '2026-08-22 18:07'
updated_date: '2026-08-22 18:14'
labels:
  - bug
  - flutter
  - crash
dependencies: []
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reported from a live two-simulator session on main (after TASK-16/42 merged): starting a game shows the red Flutter error screen on BOTH devices with 'A GameController was used after being disposed.'

Game is unplayable - this is the top priority.

Investigation so far (orchestrator, inconclusive - do not treat as the answer):
- HomeScreen._run awaits Navigator.push and calls controller.dispose() when it resolves, so anything that pops the lobby route disposes the controller.
- lobby -> game and game -> results use pushReplacement, which should NOT resolve Home's push. Worth re-checking, because the crash timing points here.
- LobbyScreen._onChange pops on c.hasLeftRoom. hasLeftRoom is set in two places (game_controller.dart:216 PlayerLeft-for-me, and :321 leaveRoom). If either fires spuriously at game start, Home disposes the controller while GameScreen is still listening.
- Two repro attempts FAILED to reproduce in a unit test: a socket event after dispose (the socket is already closed by dispose, so it cannot deliver) and an in-flight guess completing after dispose (harmless). So the trigger is probably navigation/listener ordering, not a late async result.

A live trace is available. Two simulators are running under  with output streaming to /tmp/bg-run-a.log (iPhone 17, CD36E708-B14B-4D93-8411-94B87457B767) and /tmp/bg-run-b.log (iPhone 17 Pro, 521ADB22-72FD-46C6-9D2B-B442BFA5B88D). Backend is on http://localhost:8010. Reproduce the crash and READ THE ACTUAL STACK TRACE from those logs rather than reasoning from the source alone.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The root cause is identified from a real stack trace, not inferred
- [ ] #2 Starting a game no longer disposes a controller that is still in use
- [ ] #3 A regression test reproduces the crash and fails without the fix
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
ROOT CAUSE FOUND (agent stopped before the fix landed).

Navigator.pushReplacement completes the route it replaces. So when the lobby pushReplacement's the game screen, HomeScreen._run's awaited Navigator.push resolves mid-hand-off and runs controller.dispose() - while GameScreen.initState is calling addListener on that same controller. Same shape applies to game -> results.

This is why two earlier unit-test repro attempts failed: the trigger is navigation/route completion, not a late async result. A socket event cannot reach a disposed controller (dispose closes the socket first) and an in-flight guess completing after dispose is harmless.

A failing widget test is committed on branch fix/task-46-controller-used-after-dispose (test/navigation_disposal_test.dart, commit 63a2cdb). It drives Home -> Lobby -> (RoundStarted) -> Game through a real Navigator and reproduces the exact production error. It also has a second test asserting the controller IS still disposed on a genuine unwind (back out of the lobby), so a fix cannot just delete the dispose call and leak the socket.

Still to do: the fix itself, plus red-green confirmation and the full test run.
<!-- SECTION:NOTES:END -->
