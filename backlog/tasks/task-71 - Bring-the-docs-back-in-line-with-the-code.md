---
id: TASK-71
title: Bring the docs back in line with the code
status: Done
assignee: []
created_date: '2026-08-31 02:17'
updated_date: '2026-08-31 02:34'
labels: []
dependencies: []
ordinal: 71000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CLAUDE.md is the file every agent session reads first, and several of its statements are now false: it claims 57 Flutter tests (there are 99) and 85 backend tests (there are 162), it points at a backend/Procfile that does not exist, it says there is no ios/Podfile while one is tracked, and it never mentions backend/app/models.py. Each wrong line costs a future session a wasted detour.

The README carries the same drift.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every command, path and count in CLAUDE.md is true of the current tree
- [x] #2 README.md agrees with it
- [x] #3 The iOS setup section describes what is actually there after the CocoaPods cleanup
<!-- AC:END -->
