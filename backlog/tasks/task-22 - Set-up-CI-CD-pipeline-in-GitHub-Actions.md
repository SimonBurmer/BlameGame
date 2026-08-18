---
id: TASK-22
title: Set up CI/CD pipeline in GitHub Actions
status: To Do
assignee: []
created_date: '2026-08-18 14:50'
labels:
  - infra
  - cicd
  - ci
milestone: m-2
dependencies: []
priority: medium
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
There is no CI/CD. Add GitHub Actions workflows to run automated checks on every PR/push: Flutter (analyze + test) and backend (pytest + lint). This gates merges on green tests and keeps quality from regressing as the clone grows.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A GitHub Actions workflow runs 'flutter analyze' and 'flutter test' on PRs and pushes
- [ ] #2 A workflow runs backend pytest and a Python linter on PRs and pushes
- [ ] #3 Workflows trigger on pull_request and push to main
- [ ] #4 Failing checks block the PR from merging (status checks required)
- [ ] #5 Dependency caching is configured to keep runs fast
<!-- AC:END -->
