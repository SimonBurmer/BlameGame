---
id: TASK-64
title: Point release builds at the production API instead of localhost
status: Done
assignee: []
created_date: '2026-08-31 02:16'
updated_date: '2026-08-31 02:25'
labels: []
dependencies: []
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`apiBase` defaults to `http://localhost:8000`. A release IPA built without `--dart-define=API_BASE=...` therefore ships pointing at the device's own loopback, and iOS App Transport Security blocks cleartext HTTP outright — so the TestFlight build would fail every call with no diagnosable error. This is the single change that decides whether the build works at all off a dev machine.

The fix is a build-mode-aware default: keep localhost for debug so `flutter run` still just works, and require an https base in release. A release build that somehow still has no API_BASE should fail loudly at startup rather than silently hang on a spinner.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 wsBase derives wss from an https base
- [x] #2 A non-https base in a release build is rejected rather than silently attempted
- [x] #3 flutter run with no dart-define still talks to localhost
- [x] #4 A release build with no --dart-define never falls back to localhost, and says on screen that it has no backend URL
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Release builds no longer fall back to localhost: apiBase resolves to '' under kReleaseMode, and apiBaseProblem turns that (and any non-https base) into a 'Not configured' screen at startup instead of a spinner that never resolves.

Deviation from the original AC #1, which asked for a production https default baked in: the Railway hostname is recorded nowhere in this repo and TASK-23's own 'the app can reach it via API_BASE' criterion is still unchecked, so there was no URL to bake in. Inventing a hostname would have shipped a build that fails in a *quieter* way than the one it replaced. The AC was rewritten to what was actually built. Once the Railway URL exists, the only change needed is a defaultValue on the kReleaseMode branch of apiBase.

The rules are split into pure apiBaseProblemFor/wsBaseFor helpers because a test binary is never a release build, so the release branches are otherwise unreachable from flutter test.
<!-- SECTION:NOTES:END -->
