# Photo Roulette 2

This repository will contain a new version of the Photo Roulette app.

## Getting Started

Photo Roulette 2 is being built with Flutter.

### First-time setup

Native plugins (e.g. `photo_manager`) are linked with **Swift Package Manager**,
which ships with Xcode — CocoaPods is not needed. Just fetch Dart dependencies:

```sh
flutter pub get
```

### How to run

1. Start the backend (see [backend/README.md](backend/README.md)):

```sh
cd backend && uvicorn app.main:app --reload   # → http://localhost:8000
```

2. Open the iOS Simulator:

```sh
open -a Simulator
```

3. Run the app (defaults to `API_BASE=http://localhost:8000`):

```sh
flutter run
```

### Running the latest version after pulling changes

`flutter run`'s hot reload/restart does **not** pick up new native plugins or
dependency changes — you get a stale build (old data, missing features). After
switching branches or adding a dependency, do a clean rebuild:

```sh
flutter pub get           # resolve any new/changed packages
flutter clean             # drop stale build artifacts (only if things look wrong)
flutter run               # fresh build; press "q" to fully quit a running session first
```

If the simulator still shows an old build, uninstall it first:

```sh
xcrun simctl uninstall booted com.example.flutterApplication1
```

### Testing multiplayer locally (two simulators)

Photo Roulette needs 2+ players to start a game. To test that on one machine,
run the app on two simulators at once — one player creates the game and shares
the code, the other joins with it.

**Script (recommended):**

```sh
scripts/run-local-multiplayer.sh
```

One command starts everything: the backend (if not already running), the
Backlog.md board (`backlog browser`), and the app on two simulators (`iPhone 17`
and `iPhone 17 Pro` by default — override with `SIM_A_NAME`/`SIM_B_NAME` env
vars if you don't have those), all pointed at the same local backend.
Ctrl+C stops everything it started.

**Manual equivalent:**

```sh
xcrun simctl list devices available          # find two device UDIDs
xcrun simctl boot <udid-1>
xcrun simctl boot <udid-2>
open -a Simulator
flutter run -d <udid-1> --dart-define=API_BASE=http://localhost:8000
flutter run -d <udid-2> --dart-define=API_BASE=http://localhost:8000   # run in a second terminal
```

Each `flutter run` needs its own terminal/process — they're independent debug
sessions. Use `Cmd+Tab`/the simulator's device picker (or `xcrun simctl list
devices booted`) to switch which one is frontmost.
