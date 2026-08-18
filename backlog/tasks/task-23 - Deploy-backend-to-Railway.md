---
id: TASK-23
title: Deploy backend to Railway
status: To Do
assignee: []
created_date: '2026-08-18 14:50'
updated_date: '2026-08-18 14:50'
labels:
  - infra
  - backend
  - deploy
  - railway
milestone: m-2
dependencies:
  - TASK-22
priority: medium
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The FastAPI backend has a Procfile and railway.json but is not yet set up as a reliable deployment. Configure the Railway service, environment variables, and (ideally) auto-deploy from the CI/CD pipeline so the API is reachable by the Flutter app via the API_BASE dart-define.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Backend is deployed and reachable on a stable Railway URL
- [ ] #2 Required environment variables (e.g. UPLOAD_DIR) are configured in Railway
- [ ] #3 The /health endpoint returns ok on the deployed instance
- [ ] #4 The Flutter app can reach it via --dart-define=API_BASE=<railway-url>
- [ ] #5 Deploy is triggered automatically on merge to main (via the CI/CD pipeline)
<!-- AC:END -->
