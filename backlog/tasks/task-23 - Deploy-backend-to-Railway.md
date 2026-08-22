---
id: TASK-23
title: Deploy backend to Railway
status: Done
assignee:
  - '@simon'
created_date: '2026-08-18 14:50'
updated_date: '2026-08-22 13:07'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add rootDirectory=backend + healthcheckPath=/health to backend/railway.json so Railway builds the subdir and gates deploys on health.
2. Delete backend/Procfile (railway.json startCommand already covers it; two sources of truth).
3. Add .github/workflows/ci.yml: run backend pytest on PR/push, then deploy to Railway via railway CLI on push to main (needs RAILWAY_TOKEN secret).
4. Document Railway setup steps (service creation, UPLOAD_DIR env var, token) in backend/README.md.
5. Verify /health on deployed URL and Flutter --dart-define=API_BASE=<url>.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Config side done: railway.json gains healthcheckPath=/health (deploy gated on health) and keeps numReplicas=1 (in-memory state). Deleted backend/Procfile - railway.json startCommand was already the source of truth, two files was duplicate config. Added .github/workflows/backend.yml: pytest on every PR, railway up on push to main. backend/README.md documents the manual Railway steps and the two GitHub Actions credentials.

App code needed no changes - main.py already binds 0.0.0.0/$PORT, reads UPLOAD_DIR from env (default 'uploads'), and exposes /health.

Remaining work is dashboard-only and cannot be done from the repo: create the Railway service with Root Directory=backend, generate a domain, add RAILWAY_TOKEN secret + RAILWAY_SERVICE variable in GitHub. AC 1-5 stay unchecked until verified against the live URL.

Known limitation (accepted, not a bug): Railway's filesystem is ephemeral, so uploaded photos are lost on redeploy. Fine for short-lived rounds; needs a Volume + UPLOAD_DIR override for persistence.

Switched deploy strategy: Railway's GitHub integration now drives deploys instead of a 'railway up' job in CI. The deploy job has been removed from .github/workflows/ci.yml, so RAILWAY_TOKEN and RAILWAY_SERVICE are no longer needed in GitHub.

Reason: the requirement was to redeploy only on backend changes. Railway supports that natively via watch patterns, but they are evaluated against the uploaded archive - and 'railway up' uploads the CONTENTS of backend/ as the archive root, so paths inside it are app/main.py rather than backend/app/main.py. A /backend/** pattern therefore matches nothing and every deploy is silently marked Skipped (no build, no error). The GitHub integration checks out the whole repo, so the pattern works there.

Required dashboard settings for the new setup: Root Directory=backend, Watch patterns=/backend/**, and a generated domain.

Also worth recording: the Homebrew railway formula is pinned to v2.1.0, whose auth endpoint is gone - 'railway login' fails with a bare 404. Use 'npm install -g @railway/cli' for v5.
<!-- SECTION:NOTES:END -->
