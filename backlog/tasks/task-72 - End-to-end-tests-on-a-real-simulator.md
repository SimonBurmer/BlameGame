---
id: TASK-72
title: End-to-end tests on a real simulator
status: Done
assignee: []
created_date: '2026-08-31 03:30'
updated_date: '2026-08-31 03:30'
labels: []
dependencies: []
ordinal: 72000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Everything under test/ fakes the socket, the API client and the camera roll, so none of it can catch the failures that only happen on a device: a plugin that does not link, a permission that is never granted, a build whose API_BASE points nowhere, or a route transition that leaves two screens in the tree at once.

Two suites now run against a real backend on real simulators. integration_test/app_test.dart hosts a game on one device and drives the second player over HTTP from inside the test, which produces exactly the broadcasts a second phone would. integration_test/two_device_test.dart runs on two simulators at once, both joining one pre-created room through the app's own JOIN GAME flow, and both have to reach the same leaderboard; scripts/run-two-device-test.sh creates the room and staggers the two runs so their builds do not race in build/ios.

The camera-roll picker is the one path these cannot exercise: the first permission request pops a system alert, WidgetTester injects pointer events straight into the engine rather than through the window server, and a pre-granted TCC decision does not survive the reinstall flutter test performs. Both suites detect that and contribute the photo over the API instead, so everything downstream still runs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A full game — create, join, photos, start, guess, leaderboard — runs against a real backend on a real simulator
- [x] #2 Two simulators play the same room simultaneously and both reach the leaderboard
- [x] #3 A blocked photo permission degrades to a skip with a clear message rather than a hang
- [x] #4 flutter analyze is clean and the unit suites still pass
<!-- AC:END -->
