// Drives the app through the states we want to photograph for the website.
//
// It does not take the screenshots itself: `scripts/capture-app-screenshots.sh`
// watches the room over HTTP and calls `xcrun simctl io screenshot` when the
// room changes phase. Keeping the capture on the host side avoids the
// platform-specific screenshot plumbing entirely, and the pictures are then
// exactly what a person would see on the device.
//
// The three other players are created over HTTP rather than by driving more
// simulators: the point is to photograph one client in a populated game.
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart' show MediaType;
import 'package:integration_test/integration_test.dart';

import 'package:blame_game/main.dart' as app;
import 'package:blame_game/screens/game_screen.dart';
import 'package:blame_game/state/game_controller.dart';
import 'package:blame_game/theme/app_theme.dart';

import 'demo_photos.g.dart';

const String apiBase = 'http://localhost:8000';

/// Long enough for the host capture script to notice the phase and shoot.
const Duration dwell = Duration(seconds: 6);

Future<Map<String, dynamic>> _post(String path, [Map<String, dynamic>? body]) async {
  final res = await http.post(
    Uri.parse('$apiBase$path'),
    headers: const {'content-type': 'application/json'},
    body: jsonEncode(body ?? const {}),
  );
  if (res.statusCode >= 300) {
    throw StateError('POST $path -> ${res.statusCode} ${res.body}');
  }
  return jsonDecode(res.body) as Map<String, dynamic>;
}

Future<void> _uploadPhoto(String code, String playerId, String base64Jpeg, String name) async {
  // owner_id is a query parameter, not a form field.
  final uri = Uri.parse('$apiBase/rooms/$code/photos')
      .replace(queryParameters: {'owner_id': playerId});
  final req = http.MultipartRequest('POST', uri)
    ..files.add(http.MultipartFile.fromBytes(
      'file',
      base64Decode(base64Jpeg),
      filename: '$name.jpg',
      contentType: MediaType('image', 'jpeg'),
    ));
  final res = await req.send();
  if (res.statusCode >= 300) {
    throw StateError('upload -> ${res.statusCode} ${await res.stream.bytesToString()}');
  }
}

/// Deals the demo roll out so no two players hold the same photograph. They
/// used to overlap, and two rounds in a row then showed the same picture, which
/// looks like a bug in the screenshots even though it is not one.
Future<void> _dealPhotos(String code, List<String> players) async {
  final each = demoPhotosBase64.length ~/ players.length;
  for (var i = 0; i < players.length; i++) {
    for (var n = 0; n < each; n++) {
      await _uploadPhoto(code, players[i], demoPhotosBase64[i * each + n], 'p$i$n');
    }
  }
}

/// pumpAndSettle never returns on the game screen: it runs a periodic countdown
/// timer, so the tree is never quiescent. Pump in slices instead.
Future<Map<String, dynamic>> _room(String code) async {
  final res = await http.get(Uri.parse('$apiBase/rooms/$code'));
  return jsonDecode(res.body) as Map<String, dynamic>;
}

/// Pumps frames while polling the server, so waits track real game state
/// instead of guessed durations.
Future<bool> pumpUntil(
  WidgetTester tester,
  String code,
  bool Function(Map<String, dynamic> room) done, {
  Duration limit = const Duration(seconds: 90),
}) async {
  final deadline = DateTime.now().add(limit);
  while (DateTime.now().isBefore(deadline)) {
    if (done(await _room(code))) return true;
    await pumpFor(tester, const Duration(milliseconds: 500));
  }
  return false;
}

Future<void> pumpFor(WidgetTester tester, Duration total) async {
  const step = Duration(milliseconds: 100);
  for (var spent = Duration.zero; spent < total; spent += step) {
    await tester.pump(step);
  }
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('walk the app through every screen worth photographing',
      (tester) async {
    // --- populate a room over HTTP -------------------------------------
    final room = await _post('/rooms');
    final code = room['code'] as String;
    final host = await _post('/rooms/$code/join', {'name': 'Mara'});
    final hostId = host['player_id'] as String;

    final others = <String>[hostId];
    for (final name in ['Jonas', 'Ada', 'Leo']) {
      final p = await _post('/rooms/$code/join', {'name': name});
      others.add(p['player_id'] as String);
    }

    await _dealPhotos(code, others);

    // --- home screen ----------------------------------------------------
    app.main();
    await tester.pumpAndSettle();
    debugPrint('SHOT: home');
    await pumpFor(tester, dwell);

    // --- join as a fifth player ----------------------------------------
    final fields = find.byType(TextField);
    await tester.enterText(fields.first, 'You');
    await tester.pumpAndSettle();
    await tester.enterText(fields.last, code);
    await tester.pumpAndSettle();
    await tester.tap(find.text('JOIN GAME'));
    await tester.pumpAndSettle();
    debugPrint('SHOT: lobby ($code)');
    await pumpFor(tester, dwell);

    // Starting from here crashes on main: LobbyScreen pushReplacements to
    // GameScreen, which completes the future HomeScreen is awaiting, so
    // HomeScreen disposes the controller while GameScreen is mounting. That is
    // TASK-46, and it is why the in-game shots are taken by the next test
    // instead of by continuing this one.
  }, timeout: const Timeout(Duration(minutes: 5)));

  testWidgets('photograph the in-game screens', (tester) async {
    final room = await _post('/rooms');
    final code = room['code'] as String;
    final host = await _post('/rooms/$code/join', {'name': 'Mara'});
    final hostId = host['player_id'] as String;

    final bots = <String>[hostId];
    for (final name in ['Jonas', 'Ada', 'Leo']) {
      final p = await _post('/rooms/$code/join', {'name': name});
      bots.add(p['player_id'] as String);
    }
    await _dealPhotos(code, bots);

    // Join as a real client, then mount the game flow directly. The screen and
    // the data are the real thing on a real device; only the route it was
    // reached by differs, because the normal route is broken (TASK-46).
    final controller = GameController();
    await controller.joinByCode(code, 'You');

    // Short rounds: the capture has to sit through every one of them.
    await _post('/rooms/$code/start',
        {'host_id': hostId, 'total_rounds': 5, 'round_seconds': 20});
    await tester.pumpWidget(MaterialApp(
      theme: buildAppTheme(),
      debugShowCheckedModeBanner: false,
      home: GameScreen(controller: controller),
    ));
    await pumpUntil(tester, code, (r) => r['state'] == 'in_round');
    await pumpFor(tester, const Duration(seconds: 2));
    debugPrint('SHOT: round');
    await pumpFor(tester, dwell);

    // Guess, so the instant points banner is on screen.
    for (final name in ['Jonas', 'Ada', 'Mara', 'Leo']) {
      final chip = find.text(name);
      if (chip.evaluate().isNotEmpty) {
        await tester.tap(chip.first, warnIfMissed: false);
        break;
      }
    }
    await pumpFor(tester, const Duration(seconds: 2));
    debugPrint('SHOT: guessed');
    await pumpFor(tester, dwell);

    // Everyone else answers the round that is actually running, so it resolves
    // early and the reveal appears rather than waiting out the clock.
    // Each bot picks a different player, rotating per round. Nobody can know
    // the owner before the reveal, so this is how the demo game ends up with a
    // spread of scores instead of a leaderboard of zeroes.
    Future<void> botsAnswer() async {
      final r = await _room(code);
      final round = r['current_round'] as int;
      for (var i = 0; i < bots.length; i++) {
        try {
          await _post('/rooms/$code/guess', {
            'guesser_id': bots[i],
            'guessed_owner_id': bots[(i + round) % bots.length],
            'round_index': round,
          });
        } catch (_) {/* already guessed this round */}
      }
    }

    await botsAnswer();
    await pumpUntil(tester, code, (r) => r['state'] == 'revealing');
    await pumpFor(tester, const Duration(seconds: 3));

    // Play out the rest, guessing each round so the scores are real. The
    // remaining shots are taken here rather than all in round one, so each one
    // shows a different photo.
    for (var round = 1; round < 5; round++) {
      if (!await pumpUntil(tester, code, (r) => r['state'] == 'in_round')) break;
      await pumpFor(tester, const Duration(seconds: 1));
      for (final name in ['Jonas', 'Ada', 'Mara', 'Leo']) {
        final chip = find.text(name);
        if (chip.evaluate().isNotEmpty) {
          await tester.tap(chip.first, warnIfMissed: false);
          break;
        }
      }
      if (round == 1) {
        await pumpFor(tester, const Duration(seconds: 2));
        debugPrint('SHOT: guessed');
        await pumpFor(tester, dwell);
      }
      await botsAnswer();
      await pumpUntil(tester, code, (r) => r['state'] != 'in_round');
      if (round == 2) {
        debugPrint('SHOT: reveal');
        await pumpFor(tester, const Duration(seconds: 3));
      }
    }

    final finished =
        await pumpUntil(tester, code, (r) => r['state'] == 'finished');
    debugPrint('finished=$finished');
    await pumpFor(tester, const Duration(seconds: 3));
    debugPrint('SHOT: results');
    await pumpFor(tester, dwell);

    controller.dispose();
  }, timeout: const Timeout(Duration(minutes: 5)));
}
