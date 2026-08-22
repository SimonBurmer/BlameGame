# @blame-game/brand

Tokens shared between the Flutter app and the website: the palette, the app
name, the limits the game enforces, and the store links.

The palette is a transcription of `AppColors.dark` in
`lib/theme/app_theme.dart`. Dart and TypeScript cannot share a constant, so
this is the seam where the two can drift — if a colour changes there, change it
here too. They are the same brand, not two that happen to match.

`limits` exists so marketing copy quotes the rules rather than retyping them:
the player cap and photo cap come from `backend/app/game.py`, the room-code
length from `backend/app/store.py`.
