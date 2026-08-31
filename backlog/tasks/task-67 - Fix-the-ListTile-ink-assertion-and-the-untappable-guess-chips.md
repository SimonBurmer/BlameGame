---
id: TASK-67
title: Fix the ListTile ink assertion and the untappable guess chips
status: Done
assignee: []
created_date: '2026-08-31 02:16'
updated_date: '2026-08-31 02:20'
labels: []
dependencies: []
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
24 of the 99 Flutter tests fail on a framework assertion: a SwitchListTile inside TintedCard, which paints its background with a Container/BoxDecoration. ListTile draws its background and ink splashes on the nearest Material ancestor, so the DecoratedBox hides them — the hardcore switch has had no ripple this whole time. The tests are not wrong; they are reporting a real UI bug.

The fix belongs in TintedCard rather than at the one call site: painting through a Material gives every card an ink surface, which is what a card that contains anything tappable needs.

The game screen has the same class of problem from the other direction: the guess chips are bare GestureDetectors, so they have no ink response and no button semantics for VoiceOver — a screen reader announces them as plain text. The lobby already fixed this for its icon buttons and left a comment saying why.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 flutter test is fully green
- [x] #2 TintedCard paints through a Material so ink lands on it, with no visual change to the cards
- [x] #3 The guess chips respond to touch and are announced as buttons with VoiceOver
<!-- AC:END -->
