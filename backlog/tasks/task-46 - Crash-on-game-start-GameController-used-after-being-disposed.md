---
id: TASK-46
title: 'Crash on game start: GameController used after being disposed'
status: In Progress
assignee: []
created_date: '2026-08-22 18:07'
updated_date: '2026-08-23 00:46'
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
ROOT CAUSE FOUND (from a deterministic single-device repro, not the two-simulator session).

Navigator.pushReplacement completes the REPLACED route's popped future. That is documented behaviour, not a quirk: the old route is removed and its future completes with the result (null by default).

So the chain is:
1. home_screen.dart:65  await Navigator.push(LobbyScreen)  -- Home parks here holding the controller.
2. lobby_screen.dart:64 Navigator.pushReplacement(GameScreen) on game_started.
3. That completes Home's awaited future immediately, so home_screen.dart runs controller.dispose().
4. game_screen.dart:46 _GameScreenState.initState calls c.addListener(_onChange) on the now-disposed controller.

Stack confirms step 4 exactly:
  #2 ChangeNotifier.addListener (change_notifier.dart:273)
  #3 _GameScreenState.initState (game_screen.dart:46)

This is why the ticket's investigation stalled: it recorded the assumption 'lobby -> game and game -> results use pushReplacement, which should NOT resolve Home's push'. That assumption is backwards, and it is the whole bug. It also explains why both unit-test repro attempts failed - they probed async ordering (a late socket event, an in-flight guess), but the trigger is navigation, so nothing async is involved at all. The same applies to results_screen.dart:42, which pushReplacements again.

Not fixing it here: this came up while capturing marketing screenshots (TASK-48), and the fix is a real design choice about who owns the controller's lifetime rather than a one-liner. The options, briefly:
- Stop tying the controller's lifetime to the push future, and give the game flow a wrapper widget that creates the controller in initState and disposes it in dispose. Most correct, and it makes the lifetime independent of how the screens navigate.
- Or keep push() for lobby -> game instead of pushReplacement, which fixes the disposal but changes what the back gesture does.

REPRODUCTION, now one command and no manual tapping:
  ./scripts/capture-app-screenshots.sh
It populates a room over HTTP, drives one simulator into the game, and the red screen appears on the 'round' screenshot in build/app-screenshots/. Full trace in /tmp/crash-trace.log.
<!-- SECTION:NOTES:END -->
