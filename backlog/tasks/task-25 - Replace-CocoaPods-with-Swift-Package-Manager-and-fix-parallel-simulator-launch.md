---
id: TASK-25
title: Replace CocoaPods with Swift Package Manager and fix parallel simulator launch
status: In Progress
assignee:
  - '@manuel'
created_date: '2026-08-21 21:00'
updated_date: '2026-08-21 21:00'
labels:
  - infra
  - ios
  - build
  - tooling
milestone: m-2
dependencies: []
priority: medium
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two local iOS build problems, both in the same toolchain. First, scripts/run-local-multiplayer.sh only booted one of the two simulators: the two `flutter run` calls build the same project into the same build/ios directory concurrently and race while copying Flutter.framework, failing one with "rsync ... move_file: Flutter.framework/Flutter: No such file or directory". Second, every iOS build printed a Flutter warning that all plugins are now Swift Packages while the project still carried CocoaPods integration, which costs build time for no benefit. Drop CocoaPods, and make the two-simulator launch serialize its build.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 scripts/run-local-multiplayer.sh launches the app on both simulators in one run
- [x] #2 CocoaPods is fully deintegrated: no ios/Podfile, no Pods xcconfig includes, no Pods reference in the workspace
- [x] #3 A clean flutter build ios --simulator succeeds with no CocoaPods warning
- [x] #4 Native plugins (photo_manager) are still linked via Swift Package Manager
- [x] #5 README and CLAUDE.md no longer instruct contributors to install CocoaPods
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Build the simulator app once in the script, then launch each device with --use-application-binary so only one Xcode build ever runs.
2. Run `pod deintegrate` in ios/, delete Podfile + Podfile.lock + Pods/, and strip the Pods xcconfig includes from Flutter/Debug.xcconfig and Flutter/Release.xcconfig.
3. Remove the leftover Pods.xcodeproj FileRef from Runner.xcworkspace (pod deintegrate leaves it behind).
4. Verify with flutter clean + a full rebuild and a real two-simulator run.
5. Update README, CLAUDE.md and the script header, which all still required CocoaPods.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Root cause of the one-simulator failure was a build race, not a broken simulator: two concurrent `flutter run`s share build/ios, and the 3s stagger in the script was not enough. Fixed by building once up front and passing --use-application-binary=build/ios/iphonesimulator/Runner.app to both runs, which skips the build step entirely. API_BASE moved to the build call since --dart-define is ignored on --use-application-binary runs. Hot reload still works on both devices.

CocoaPods deintegration was safe because Flutter had already migrated the project to SPM (FlutterGeneratedPluginSwiftPackage in project.pbxproj). Note for future debugging: SPM links plugins statically into Runner.app/Runner.debug.dylib rather than embedding them under Runner.app/Frameworks/, so verify with `nm Runner.app/Runner.debug.dylib | grep -i <plugin>` - the top-level Runner binary is only a thin launcher stub and will look empty.

Verified: flutter clean + pub get + build ios --simulator succeeds with zero CocoaPods warnings, PhotoManagerPlugin present in Runner.debug.dylib, and the full script attaches both iPhone 17 and iPhone 17 Pro. Incremental rebuild dropped from ~21s to ~5s. flutter analyze clean, flutter test 13 passed, backend pytest 39 passed.

Two fixes rode along in the same commit, both in scripts/run-local-multiplayer.sh: the `backlog` CLI missing from PATH now prints a skip message instead of "command not found", and "${PIDS[@]}" on an empty array is guarded, since that is an unbound-variable error under bash 3.2 + set -u and would have failed inside the cleanup trap and masked the real error.

Status stays In Progress until the PR is merged; all acceptance criteria are met on the branch.
<!-- SECTION:NOTES:END -->
