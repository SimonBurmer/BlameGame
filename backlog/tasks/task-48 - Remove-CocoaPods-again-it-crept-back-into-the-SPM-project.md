---
id: TASK-48
title: Remove CocoaPods again - it crept back into the SPM project
status: To Do
assignee: []
created_date: '2026-08-22 22:47'
updated_date: '2026-08-22 22:47'
labels:
  - ios
  - build
  - chore
dependencies: []
ordinal: 48000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-25 deliberately deintegrated CocoaPods in favour of Swift Package Manager (commit b5a32f6), and .claude/CLAUDE.md is explicit that there is no ios/Podfile and that brew install cocoapods is not part of setup. CocoaPods is now tracked on main again:

- ios/Podfile - added by 48a90ea (the TASK-42 photo-preview PR)
- ios/Podfile.lock - added by e716846
- 8 Pods_ references baked into ios/Runner.xcodeproj/project.pbxproj, also via e716846
- Pods includes in ios/Flutter/Debug.xcconfig and Release.xcconfig

How it happened: any flutter command (pub get, analyze, test, build) regenerates ios/Podfile and re-adds the Pods xcconfig includes, and running a build then rewrites project.pbxproj with Pods framework refs and freshly randomized UUIDs. Agents and humans then swept those up with git add -A. This has already polluted several unrelated PRs with 122 lines of pure UUID churn, and it will keep doing so.

Note the ordering trap: adding Podfile to .gitignore is NOT enough on its own, because the file is already tracked - gitignore does not affect tracked files. It has to be git rm --cached'd as well.

Verify the app still builds and runs on a simulator after removal - that is the real acceptance test, not just that the files are gone. CLAUDE.md notes plugins are statically linked into Runner.debug.dylib under SPM rather than embedded in Runner.app/Frameworks, so check there (nm Runner.app/Runner.debug.dylib | grep -i photo_manager) to confirm plugins are still linked.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ios/Podfile and ios/Podfile.lock are untracked and gitignored
- [ ] #2 Pods references and xcconfig includes are removed from the Xcode project
- [ ] #3 The app still builds and launches on a simulator with plugins linked
- [ ] #4 A flutter build no longer leaves tracked-file churn in git status
<!-- AC:END -->
