---
id: TASK-37
title: Extract the app theme and shared widgets
status: In Progress
assignee: []
created_date: '2026-08-22 01:21'
updated_date: '2026-08-22 10:29'
labels:
  - refactor
  - flutter
  - ui
milestone: m-3
dependencies: []
priority: medium
ordinal: 37000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Theme.of(context) appears zero times across the four screens - the seeded ColorScheme in main.dart is effectively dead while screens hardcode the brand colour 16 times, 27 font sizes, and 11 distinct white alphas. Six widget patterns are duplicated across the screens (gradient scaffold with three different gradients, result banner, buttons at three heights and two radii, player avatar, tinted card, pill badge), roughly 380 of 1242 lines. Extract a ThemeExtension plus a real TextTheme and a small shared widget set.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Screens read colours and text styles from the theme
- [ ] #2 The repeated widget patterns exist in one place
- [ ] #3 The visual design is unchanged
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Partially done. buildAppTheme() + AppColors ThemeExtension landed in lib/theme/app_theme.dart and is wired into main.dart, with context.colors for access. Shared widgets extracted so far: ResultBanner (the two near-identical banners, one of which was missing the Flexible and overflowed by 25px), ConnectionBanner, PlayerCosmetics, friendlyError. Remaining: most screens still hardcode colours and font sizes, and the gradient scaffold / buttons / player avatar / tinted card / pill badge duplication is still in place.
<!-- SECTION:NOTES:END -->
