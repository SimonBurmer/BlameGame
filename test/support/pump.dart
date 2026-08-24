import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:blame_game/theme/app_theme.dart';
import 'package:blame_game/models/game_models.dart';
import 'package:blame_game/services/api_client.dart';
import 'package:blame_game/state/game_controller.dart';

import 'fakes.dart';

/// A joined controller plus the fake socket driving it, for widget tests.
class TestHarness {
  final GameController controller;
  final FakeGameSocket socket;
  final RecordingClient http;

  TestHarness(this.controller, this.socket, this.http);

  /// Push an event and let the notifier settle.
  Future<void> emit(WidgetTester tester, GameEvent event) async {
    socket.emit(event);
    await tester.pump();
    await tester.pump();
  }
}

const _defaultSnapshot = {
  'state': 'lobby',
  'round_seconds': 10,
  'players': [
    {'id': 'me', 'name': 'Emma', 'is_host': true, 'score': 0},
    {'id': 'p2', 'name': 'Jake', 'is_host': false, 'score': 0},
  ],
};

/// Builds a controller that has already joined a room.
Future<TestHarness> harness({
  bool isHost = true,
  Map<String, Object?> snapshot = _defaultSnapshot,
  Object? guess = const {'points': 800, 'correct': true},
  Object? reset = const {'state': 'lobby'},
}) async {
  final http = RecordingClient(
    join: {'player_id': 'me', 'is_host': isHost},
    snapshot: snapshot,
    guess: guess,
    reset: reset,
  );
  final socket = FakeGameSocket();
  final controller = GameController(
    api: ApiClient(httpClient: http.client, baseUrl: 'http://test'),
    socketFactory: fakeSocketFactory(socket),
    // No heartbeat in widget tests: they assert on screens, not on the
    // connection, and the test framework fails any test that ends with a timer
    // still pending. `game_controller_test.dart` covers the heartbeat itself.
    heartbeatInterval: Duration.zero,
    // No automatic retry either: these tests assert that a drop surfaces a
    // banner with a manual RETRY, which is exactly the state the automatic
    // retries would clear out from under them.
    retryBackoff: const [],
  );
  await controller.joinByCode('ABC12', 'Emma');
  return TestHarness(controller, socket, http);
}

/// A phone-sized surface. The default 800x600 test window is the wrong shape
/// for these screens, and tall Columns collapse in it.
const phoneSize = Size(420, 900);

/// Pumps [child] inside the real app theme, so tests see production styling.
Future<void> pumpScreen(WidgetTester tester, Widget child) async {
  tester.view.physicalSize = phoneSize;
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  await tester.pumpWidget(
    MaterialApp(theme: buildAppTheme(), home: child),
  );
  await tester.pump();
}
