---
id: TASK-19
title: 'Validate game configuration bounds (rounds, player caps)'
status: To Do
assignee: []
created_date: '2026-08-18 14:40'
updated_date: '2026-08-18 14:43'
labels:
  - backend
  - gameplay
  - validation
milestone: m-3
dependencies: []
priority: low
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
StartBody.total_rounds has no bounds check (could be 0 or huge). There is no min/max player cap beyond the >=2 start rule. Add sane validation for round count and player limits.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 total_rounds is validated within sane min/max bounds
- [ ] #2 A maximum player cap is enforced on join
<!-- AC:END -->
