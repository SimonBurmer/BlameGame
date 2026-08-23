---
id: TASK-37
title: Extract the app theme and shared widgets
status: In Progress
assignee: []
created_date: '2026-08-22 01:21'
updated_date: '2026-08-23 16:56'
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
- [x] #1 Screens read colours and text styles from the theme
- [x] #2 The repeated widget patterns exist in one place
- [x] #3 The visual design is unchanged
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Done. All four screens (home, lobby, game, results) now read colours from context.colors and, where the values matched exactly, from the theme's TextTheme; the six duplicated widget patterns live in lib/ui/.

Shared widgets: GradientScaffold, PrimaryButton/SecondaryButton, PlayerAvatar, TintedCard, PillBadge (this ticket) on top of the earlier ResultBanner, ConnectionBanner, PlayerCosmetics and friendlyError.

Visual design is unchanged, and that was verified visually rather than by reading code: BEFORE screenshots were taken from unmodified main on the iPhone 17 simulator, then AFTER screenshots from this branch, and the four screens compared element by element (home, lobby with two players and the settings panel, in-round game screen, results leaderboard).

Variants deliberately NOT unified, because collapsing them would have been a real visual change:
- three background gradients (diagonal three-stop, vertical two-stop, vertical three-stop) stay as an AppGradient enum
- three button heights (50/52/56) and two radii (14/16) stay as parameters
- per-call-site fill alphas, radii and paddings on TintedCard/PillBadge/PlayerAvatar stay as parameters
- Colors.white54 (54%) is kept as an explicit alpha rather than snapped to the palette's 50% onSurfaceFaint

One drift was caught by the screenshot comparison and fixed: mapping the results winner name to textTheme.headlineLarge resolved to a different line height and shifted everything below it up ~14pt, so that one Text keeps its explicit style with a comment saying why. This is exactly the class of change reading the code would have missed.

Remainder (small, deliberate): the photo-preview bottom sheet's RESHUFFLE / USE THESE buttons are half-width in a Row rather than the full-width shape PrimaryButton/SecondaryButton model, so they were migrated to context.colors but not wrapped in the shared buttons. The trophy gradient's darker stop (0xFFFFA500) is a one-off and stays local rather than being added to AppColors.

flutter analyze: 0 issues. flutter test: 94 passed. backend pytest: 140 passed.
<!-- SECTION:NOTES:END -->
