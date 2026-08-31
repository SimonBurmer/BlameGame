---
id: TASK-65
title: Add the iOS privacy manifest and export-compliance keys
status: Done
assignee: []
created_date: '2026-08-31 02:16'
updated_date: '2026-08-31 02:27'
labels: []
dependencies: []
ordinal: 65000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
App Store Connect requires a PrivacyInfo.xcprivacy privacy manifest; there is none. The app reads the camera roll and uploads those photos to a server, which is collected data that has to be declared, and Flutter's engine plus photo_manager use required-reason APIs (file timestamps, disk space, UserDefaults) that each need a declared reason code.

Separately, Info.plist has no ITSAppUsesNonExemptEncryption, so every single TestFlight upload stops and asks for an export-compliance answer by hand. The app only uses standard HTTPS, which is exempt.

CFBundleName is also still the Dart package name (photo_blame) rather than the product name.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 ios/Runner/PrivacyInfo.xcprivacy exists, is in the Runner target's Copy Bundle Resources, and declares the photo collection plus every required-reason API the app and its plugins use
- [x] #2 ITSAppUsesNonExemptEncryption is set so TestFlight stops asking
- [x] #3 CFBundleName reads Photo Blame
- [x] #4 flutter build ios --release succeeds and the manifest is inside the built .app
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
ios/Runner/PrivacyInfo.xcprivacy added and wired into the Runner target's Resources phase; confirmed present in both build/ios/iphonesimulator/Runner.app and a --release device build.

Flutter.framework and photo_manager already ship their own manifests (file timestamp, system boot time), so the app's own NSPrivacyAccessedAPITypes is deliberately empty — Apple aggregates all three. What the app manifest carries is the collection nobody else can declare for it: photos uploaded to the game server, and the display name a player types when joining. Both unlinked, neither used for tracking, both AppFunctionality.

photo_manager's own manifest claims the photos are for ProductPersonalization/Other, which describes the plugin, not this app; the app-level declaration is what App Store Connect reads for the nutrition label.
<!-- SECTION:NOTES:END -->
