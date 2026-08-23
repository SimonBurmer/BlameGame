---
id: TASK-51
title: >-
  Website: drop the tablet mock, add store proof and a GDPR section, widen the
  layout
status: Done
assignee: []
created_date: '2026-08-23 10:24'
updated_date: '2026-08-23 10:24'
labels: []
dependencies: []
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up on TASK-50. The scroll-driven tablet frame is not wanted. The band under the hero should carry App Store-style proof rather than game limits. The page should say what happens to people's photos, because a game built on camera rolls has to answer that before anybody joins one. And the desktop layout should use the full width the navbar already uses.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The scroll-driven tablet section is gone, along with the component behind it
- [x] #2 The band under the hero shows a download count and two figures the app actually keeps
- [x] #3 A GDPR section states that photos are deleted with the room and that nothing is tracked, and every claim in it is true of the code
- [x] #4 Desktop sections use the same content column as the navbar
- [x] #5 Both locales build; lint, typecheck, Flutter and backend tests all pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The download count is invented. There is no App Store listing, so nobody has downloaded anything; '10,000+' is on the page because the site is written as if the app had shipped, which is TASK-49's framing. It is deliberately kept out of the JSON-LD — no aggregateRating, no interactionStatistic — because fabricated structured data is how a site earns a manual action instead of a rich result. Delete it or make it true before the page goes public.

Everything in the GDPR section is true of the code and was checked against it: store.delete_room fires on_evict, which main.py wires to _delete_room_uploads, so ending a room removes its uploads; a room nobody has touched for ROOM_TTL_SECONDS (6h) is swept the same way. There is no account system, the site sets no cookies and runs no analytics. If any of that changes the section is wrong and has to change with it — there is a comment saying so above it.

The 'guessed' screenshot is no longer shown anywhere, so prepare-screenshots.sh stops shipping it and the file is deleted. The capture run still stops there, so it can come back without another simulator run.
<!-- SECTION:NOTES:END -->
