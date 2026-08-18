---
id: TASK-9
title: Push notifications for invites and turn alerts
status: To Do
assignee: []
created_date: '2026-08-18 14:39'
updated_date: '2026-08-18 14:43'
labels:
  - frontend
  - backend
  - notifications
milestone: m-1
dependencies:
  - TASK-8
priority: low
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
No push notification support (no firebase_messaging/flutter_local_notifications). The real game notifies on invites and game events. Wire up push so users get invited/alerted when not in-app.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Push notification infra is integrated (e.g. FCM)
- [ ] #2 Users receive a notification on game invite
- [ ] #3 Notifications deep-link into the relevant game
<!-- AC:END -->
