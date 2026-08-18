/// App configuration.
///
/// The backend base URL is read from a compile-time environment variable so we
/// can point the app at localhost during development and at Railway in
/// production, without changing code:
///
///   flutter run -d chrome --dart-define=API_BASE=http://localhost:8000
///
/// Defaults to localhost so `flutter run` "just works" while developing.
library;

/// Base URL of the REST API, e.g. `http://localhost:8000`.
const String apiBase = String.fromEnvironment(
  'API_BASE',
  defaultValue: 'http://localhost:8000',
);

/// How many random photos to auto-sample from the camera roll per player.
const int photoSampleCount = 5;

/// WebSocket base URL, derived from [apiBase] by swapping the scheme
/// (`http`->`ws`, `https`->`wss`).
String get wsBase => apiBase.replaceFirst(RegExp(r'^http'), 'ws');
