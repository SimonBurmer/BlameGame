---
id: TASK-40
title: Design an app logo and ship it as the launcher icon
status: Done
assignee: []
created_date: '2026-08-22 11:17'
updated_date: '2026-08-22 12:24'
labels: []
dependencies: []
ordinal: 40000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The app ships with the stock Flutter launcher icon on every platform, so it is indistinguishable from any other Flutter project on a home screen. Design a simple mark from the existing palette and generate the icon sets from a single vector source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A logo mark exists as a vector source in the repo, using only AppColors.dark values
- [x] #2 iOS AppIcon set is regenerated at every size the asset catalog declares, with no alpha channel
- [x] #3 Android ships both the legacy launcher icon and an adaptive icon so launchers can mask it
- [x] #4 Web icons, maskable icons and the favicon are regenerated, and manifest.json carries the app's colours
- [x] #5 A script regenerates every platform icon from the vector source, using only tooling already on macOS
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Mark: a photo of somebody caught in a reticle. Three shapes - a card, a head-and-shoulders figure clipped to it, and a red ring with four ticks. The ring is an unbroken silhouette, so nothing inside it has to survive for the icon to read at 40px.

Chosen by the user from five candidates that each put a person in the photo. Not taken: a spotlight beam (the beam is white tints and is the first thing a shrinking icon discards), a censor bar over the portrait (bold when small, but censor bars read as scandal or arrest), a person badged onto the photo's corner (looks like a contacts app), and a three-suspect line-up (needs about 60px before it makes sense). Two earlier rounds were rejected outright: a pointing hand, and a set without any person in it.

The figure is the generic head-and-shoulders glyph on purpose. A drawn character acquires an age, a gender and a haircut, and then every player who is not that person is looking at somebody else's game.

Vector sources in assets/branding/ are the only thing edited by hand; every PNG comes from scripts/generate-app-icons.sh, including the resolution-aware logo_mark.png the home screen displays - Flutter has no SVG renderer without a package.

Rasterizing is scripts/rasterize-svg.swift rather than sips alone, for two reasons found by testing: ImageIO has no SVG type at all (CGImageSourceCreateWithURL returns nil, CGImageSourceCopyTypeIdentifiers lists nothing svg), so AppKit's NSImage is the only decoder on the machine; and sips always writes an alpha channel, which the iOS AppIcon set may not carry. Going through an explicit CGContext gives opaque PNGs with no lossy JPEG round-trip.

Android had no adaptive icon before this, only the legacy square PNG, so launchers on API 26+ were framing it themselves. Added mipmap-anydpi-v26/ic_launcher.xml with foreground/background layers at 108dp across all five densities, the foreground scaled to 0.86 so it sits inside the 66% zone a launcher masks to. No ic_launcher_round: the manifest declares no android:roundIcon, so it would never be read.

The home screen's Icons.photo_library_rounded was the old identity and is now the mark itself.

Verified: 15 iOS icons checked against Contents.json for size and opacity; flutter build ios --simulator succeeded and actool compiled the icon into Runner.app; installed on a booted simulator - the icon renders on the home screen and the mark renders above the title in-app. flutter analyze clean, 57 tests pass.

Stacked on top of TASK-41: the mark only makes sense once the app is called Blame Game.
<!-- SECTION:NOTES:END -->
