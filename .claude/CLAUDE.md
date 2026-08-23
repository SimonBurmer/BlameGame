# Blame Game — Project Knowledge

A party game in the mould of Photo Roulette: players join a room, contribute random
photos from their camera roll, then guess *whose* photo each round shows. Points are
awarded for correct + fast guesses; rounds tally into a final leaderboard.

## Repo layout

An npm-workspaces monorepo for the JavaScript side, with the Flutter app and
the FastAPI backend left where they are:

```
lib/, ios/, android/ …   Flutter app (repo root — moving it would break the
                         Xcode project, the icon scripts and CI for no gain)
backend/                 FastAPI service
apps/website/            Marketing site (Next.js + Tailwind, static, EN/DE)
packages/brand/          Palette, app name and game limits shared with the site
assets/branding/         Vector sources for every icon and the OG card
assets/demo-photos/      The camera roll the screenshot run plays with
```

## Stack

- **Frontend:** Flutter (Dart SDK `^3.11.5`), Material 3. Code in `lib/`.
- **Backend:** FastAPI (Python 3.12), in-memory state + WebSockets. Code in `backend/app/`.
- **Deploy:** backend targets Railway (`backend/railway.json`, `Procfile`). Single replica.

## Architecture

### Flutter (`lib/`)
Layered: `config → models → services → state → screens`, with `theme/` and
`ui/` holding presentation shared across screens.
- `config.dart` — `apiBase` from `String.fromEnvironment('API_BASE', default 'http://localhost:8000')`; `wsBase` derived by swapping `http`→`ws`. Production URL is passed via `--dart-define=API_BASE=<url>`.
- `models/game_models.dart` — `GamePlayer`, `PhotoInfo`, and a sealed `GameEvent` hierarchy (deserialize-only). **Pure Dart, no Flutter import** — per-player colours/avatars live in `ui/player_cosmetics.dart` instead, derived from a platform-stable hash (`String.hashCode` differs between the VM and dart2js, so the same player looked different on iOS and web).
- `services/api_client.dart` — thin `http` REST wrapper; injectable `http.Client` for tests.
- `services/game_socket.dart` — `web_socket_channel`, exposes `Stream<GameEvent>`. A `GameSocketFactory` typedef is injected into the controller so tests can drive state with a fake socket.
- `state/game_controller.dart` — `ChangeNotifier` (no Provider/Riverpod/Bloc). One instance is created in `HomeScreen`, passed by constructor down through Lobby → Game → Results, and **disposed by `HomeScreen` when the pushed route returns** (it awaits the `push`) — otherwise every game leaks a live WebSocket. Identity lives in a non-nullable `GameSession` created at join time, so there are no `roomCode!` force-unwraps and a half-joined controller is unrepresentable. `connectionError` + `reconnect()` surface a dropped socket rather than freezing the game.
- `theme/app_theme.dart` — `buildAppTheme()` plus an `AppColors` `ThemeExtension`; read it via `context.colors`.
- `ui/` — cross-screen presentation: `player_cosmetics.dart`, `result_banner.dart`, `connection_banner.dart`, `error_text.dart` (`friendlyError` unwraps the backend's `{"detail": ...}` so raw JSON never reaches a player).
- `screens/` — `home`, `lobby`, `game`, `results`.

### Backend (`backend/app/`)
Pure logic under thin I/O layers:
- `game.py`, `scoring.py` — pure game rules + scoring (well unit-tested).
- `main.py` — FastAPI routes (REST + one WS route `/ws/{code}/{player_id}`).
- `store.py` — process-wide in-memory `GameStore` singleton (`dict[code→Room]`). **State is lost on restart and can't be shared across replicas.** Rooms carry `last_active` and are evicted after `ROOM_TTL_SECONDS` (6h) idle by a **lazy sweep on create/lookup** — no background task, since only a request can grow the store. `time_fn`/`on_evict` are injectable; `main.py` wires `on_evict` to delete `uploads/{code}/`, refusing any code that resolves outside `UPLOAD_DIR`. `DELETE /rooms/{code}?host_id=` ends a room explicitly.
- `connection.py` — `ConnectionManager`, broadcasts events to a room's sockets.
- `timer.py` — `RoundDriver` drives round timing (sleep injectable for tests). It holds on the reveal for `REVEAL_SECONDS` before advancing; without that pause `round_revealed` and the next `round_started` land in the same tick and players never see whose photo it was. It re-checks the room before revealing, so a round that moved underneath it isn't announced with the wrong photo.
- Photos are written to local disk under `uploads/{code}/` (ephemeral on Railway).

## Commands

### Flutter
```sh
flutter pub get
flutter analyze
flutter test                     # currently 57 tests
flutter run                      # needs a simulator/device
```

### Backend
```sh
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                           # currently 85 tests
ruff check .                     # pyflakes (F) only; configured in backend/pyproject.toml
```

### Branding / app icon
Every launcher icon is generated — never hand-edit the PNGs, regenerate them.
```sh
./scripts/generate-app-icons.sh   # iOS, Android (legacy + adaptive) and web, from the SVGs
```
- `assets/branding/app_icon.svg` is the source of truth. `logo_mark.svg` is the mark
  with no background; `app_icon_foreground.svg` / `app_icon_background.svg` are the two
  Android adaptive layers, the foreground inset to the 66% zone launchers mask to.
- `scripts/rasterize-svg.swift` does the rasterizing. It exists because **AppKit is the
  only SVG decoder on macOS** — ImageIO reports no SVG type at all — and because `sips`
  can render the SVG but always writes an alpha channel, which the iOS AppIcon set is
  not allowed to have. Drawing through an explicit `CGContext` is what makes the iOS
  PNGs opaque without a lossy JPEG round-trip.
- `logo_mark.png` (+ `2.0x/`, `3.0x/`) is generated too — the home screen shows the mark,
  and Flutter cannot render SVG without a package.
- Colours come from `AppColors.dark` only. The mark is a pointing hand: white, with the
  brand red on the cuff so something other than white survives at 40px.

### Website
```sh
npm install                                  # workspaces; from the repo root
npm run dev     --workspace @blame-game/website   # localhost:3000
npm run build   --workspace @blame-game/website   # -> apps/website/out
npm run preview --workspace @blame-game/website   # builds, serves out/ on :4173
npm run lint    --workspace @blame-game/website
```
- `apps/website` is **Next.js (App Router) + Tailwind v4**, `output: 'export'` —
  a folder of static HTML, no server. `src/app/[[...lang]]` is one route serving
  two pages: `/` is English, `/de/` is German.
- The page is prerendered, so every heading, answer and meta tag is in the HTML
  before a script runs; the bundle only adds motion. A `<noscript>` rule in the
  layout reveals the pieces that fade themselves in.
- **Animated components are vendored from the [Aceternity UI](https://ui.aceternity.com)
  registry into `src/components/ui/`**, and several are edited — for React 19's
  ref types, for `strict`, and because they ship styled for a light page with
  Aceternity's own demo copy inside them. Every edited file says so at the top;
  **re-fetching a component overwrites those edits.** That directory is exempted
  from a few lint rules in `eslint.config.mjs` for the same reason.
- Tailwind's `dark:` variant is bound to a class and `dark` sits on `<html>`.
  Those components style themselves almost entirely through `dark:`, and the
  default variant follows the OS — without this the page renders light for
  anyone on a light-mode machine.
- `public/screenshots/` are real simulator captures, not mockups. Regenerate with
  `scripts/capture-app-screenshots.sh` then `scripts/prepare-screenshots.sh`.
- `public/photos/` are the photographs the app is holding *in* those screenshots
  — the same twelve files, written from `assets/demo-photos/` by
  `scripts/generate-demo-photos.sh` (which also rebuilds the Dart fixture the
  capture run uploads). Generated: don't hand-edit. Real photographs under the
  Unsplash licence, credited in that folder's README and in the site footer.
- Copy lives in `src/i18n/{en,de}.ts`, both annotated `: Messages`, so a key
  missing from one language fails `tsc` instead of leaving a blank section.
- SEO tags, `sitemap.xml` and `robots.txt` are all derived from the `locales`
  array — adding a locale needs no edits to any of them.
- `apps/website/public/` icons are generated by `scripts/generate-app-icons.sh`,
  not hand-made. See the branding section above.
- Section widths and vertical rhythm come from two constants in
  `src/lib/utils.ts` — `shell` and `band`. The navbar is given `shell` too, and
  no longer shrinks on scroll, so nothing on the page is narrower than the
  header above it.
- `src/components/site/count-up.tsx` is ours, not vendored: Aceternity's number
  ticker is a paid block with no source. It animates with `motion` like
  everything else here, writes digits straight to the text node rather than
  through React state, and is server-rendered at its final value so the figures
  survive with scripting off.
- The GDPR section's claims are all true of the code and were checked against it:
  `store.delete_room` fires `on_evict` → `_delete_room_uploads`, so ending a room
  deletes its photos, and an idle room is swept the same way after
  `ROOM_TTL_SECONDS`. No accounts, no cookies, no analytics. **If any of that
  changes, that section is wrong and has to change with it.**
- The copy says the app is out on the App Store. **It is not** — `stores.appStore`
  in `packages/brand` is empty, so the button renders but is not a link.
  The "10,000+ downloads" figure under the hero is invented for the same framing,
  and is deliberately kept out of the JSON-LD; fabricated structured data is how a
  site earns a manual action rather than a rich result.
  The page must not go public until both are true.
- `siteOrigin` is `https://blamegame.app`, a domain nobody owns yet; every
  canonical, hreflang and sitemap URL is built from it.
- No imprint, privacy policy or cookie banner yet. The site sets no cookies and
  runs no analytics, but a German-language site needs an Impressum and a
  Datenschutzerklärung before it goes public.

## Tickets / Backlog

Work is tracked with **Backlog.md** in `backlog/`. Tasks are grouped under milestones
(Core Gameplay, Accounts & Social, Infrastructure & Persistence, Gameplay Polish,
Testing & Quality) with dependency links.

```sh
backlog task list --plain
backlog board
backlog browser                  # web UI
```

## Working conventions (IMPORTANT)

- **One ticket = one PR.** Each Backlog task is implemented on its own branch
  (`feature/task-<id>-<slug>`) and opened as a separate pull request. Never bundle
  multiple tickets into one branch/PR.
- **Spawn a subagent per ticket when it fits.** For tickets that are self-contained
  units of work (most of them), dispatch a subagent to implement it — use an isolated
  **worktree** so parallel tickets don't collide. Keep small/trivial changes inline.
- Mark the ticket `In Progress` when starting and check off acceptance criteria as they
  land (`backlog task edit <id> -s "In Progress" --check-ac <n>`).
- **Never push to git without being asked** (also a global rule). Commit on the feature
  branch; open the PR only when the user requests it.
- Branch feature work off `main`, not off another in-flight feature branch.

## Game rules that are enforced server-side (don't re-litigate client-side)

- **Scoring timing is the server's.** The round's deadline lives on `Round.ends_at`
  (set by the `RoundDriver`); `submit_guess` derives `seconds_left` from it. The client
  sends only `round_index`, never a countdown — it used to send `seconds_left`, and
  posting `99999` was worth ~10M points.
- **Guesses carry their round.** A guess in flight across a round boundary is rejected
  rather than recorded against the round the player never saw (which also used to
  consume their guess slot for the new round).
- **Starting needs photos from 2+ distinct players**, or every round shows one person's
  pictures and they win by recognising all of them. The lobby mirrors this in
  `GameController.canStart` and shows real per-player readiness from `photo_count`.
- Uploads are capped (8 MB, 10 per player, JPEG/PNG magic bytes checked, lobby only);
  rooms cap at 12 players; names are 1–24 chars.

## Style

Prefer the simplest solution that actually works: reuse what's already in the codebase,
stdlib/native before new dependencies, no abstractions or config that aren't needed yet.
Don't simplify away input validation at trust boundaries, error handling, or security.

## Local iOS dev — known gotchas (learned the hard way)

- **iOS plugins are linked with Swift Package Manager, not CocoaPods.** CocoaPods was
  deintegrated once every plugin became a Swift Package; there is no `ios/Podfile` and
  `brew install cocoapods` is not part of setup. Plugins are statically linked into
  `Runner.debug.dylib` rather than embedded under `Runner.app/Frameworks/`, so check
  there (`nm Runner.app/Runner.debug.dylib | grep -i <plugin>`) when verifying a plugin
  is linked — the top-level `Runner` binary is just a thin launcher stub.
- **Never run two `flutter run`s against this project concurrently.** They share
  `build/ios` and race while copying `Flutter.framework`, failing one with
  `rsync`/`move_file: Flutter.framework/Flutter: No such file or directory`. Build once
  (`flutter build ios --simulator --debug`) and launch each device with
  `--use-application-binary=build/ios/iphonesimulator/Runner.app`, as
  `scripts/run-local-multiplayer.sh` does.
- **A stale app on the simulator looks exactly like "my change didn't work."** Symptoms:
  buttons don't do anything, UI shows data/copy that doesn't exist anywhere in `lib/`,
  and the backend log shows zero incoming requests. Confirm which build is actually
  running before debugging app logic — check `ps`/`pgrep -fl "flutter run"` for a live
  session, and grep `lib/` for suspicious UI text before assuming it's a code bug.
  Fix: fully quit (`q` in the `flutter run` terminal, not hot reload/restart — new native
  plugins need a real rebuild), and if needed `xcrun simctl uninstall booted <bundle-id>`
  first, then relaunch clean.
- **A subagent's "done, verified" claim needs re-checking when the agent couldn't run the
  toolchain.** One subagent guessed a `photo_manager` API name
  (`requestPermissionExtended`) that didn't exist (real method: `requestPermissionExtend`)
  because it had no `flutter`/`dart` on PATH to catch it. `flutter analyze` caught it in
  under 2 seconds once run for real. Always run analyze/test yourself against actual
  installed package sources before merging subagent-written code that touches an external
  API surface.
- **Local multiplayer testing** needs 2+ players; use `scripts/run-local-multiplayer.sh`
  to boot two simulators + backend + Backlog board in one shot rather than juggling
  multiple manual `flutter run` sessions by hand.
